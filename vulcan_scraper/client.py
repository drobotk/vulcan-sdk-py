import logging
import asyncio
import sys
from typing import *

from .error import *
from .http import HTTP
from .student import Student
from . import utils
from .model import ReportingUnit
from .enum import LoginType

if (
    sys.version_info[0] == 3
    and sys.version_info[1] >= 8
    and sys.platform.startswith("win")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class VulcanWeb:
    def __init__(
        self,
        *,
        host: str,
        email: str,
        password: str,
        symbol: Optional[str] = None,
        ssl: bool = True,
    ):
        self._log = logging.getLogger(__name__)

        self.email = email
        self.password = password
        if not self.email or not self.password:
            raise ValueError("Email and password cannot be empty")

        self.symbol = symbol

        self.http = HTTP(host, ssl)

        self._uonetplus_text = ""
        self._uonetplus_permissions = ""
        self._instances: list[str] = []
        self._instance = ""

        self.logged_in = False
        self.students: list[Student] = []

    async def login(self):
        """Attempts the login process using credentials passed in the constructor"""

        self.logged_in = False

        info = await self._get_login_info(self.http.base_host, self.symbol)
        self._log.debug(info)

        if info.type is LoginType.CUFS:
            text, _ = await self.http.request(
                "POST",
                info.url,
                data={"LoginName": self.email, "Password": self.password},
            )

            if "Zła nazwa użytkownika lub hasło" in text:
                raise InvalidCredentialsError

        elif info.type is LoginType.ADFS or info.type is LoginType.ADFSLight:
            text, _ = await self.http.request(
                "POST",
                info.url,
                data={
                    "Username": self.email,
                    "Password": self.password,
                    "AuthMethod": "FormsAuthentication",
                    "x": 0,
                    "y": 0,
                },
            )

            if "hasło są niepoprawne" in text:
                raise InvalidCredentialsError

            if not all(
                ["wa" in text, "wresult" in text, "wctx" in text, "action" in text]
            ):
                raise ScraperException("Certificate not found in ADFS response")

            wa, wctx, wresult, action = utils.extract_cert(text)

            text, _ = await self.http.request(
                "POST", action, data={"wa": wa, "wresult": wresult, "wctx": wctx}
            )

        else:
            raise ScraperException(f"{info.type} not implemented!")

        if not all(["wa" in text, "wresult" in text, "wctx" in text, "action" in text]):
            raise ScraperException("Certificate not found in CUFS response")

        wa, wctx, wresult, _ = utils.extract_cert(text)

        if not self.symbol:
            symbols = utils.extract_symbols(wresult)
            self._log.debug(f"Extracted symbols: { symbols }")

        else:
            symbols = [self.symbol]

        try:
            symbols.remove(self.http.SYMBOL_DEFAULT)
        except ValueError:
            pass

        for s in symbols:
            if await self._login_cert(s, wa, wctx, wresult):
                self.logged_in = True
                self.symbol = s
                break

        if not self.logged_in:
            raise NoValidSymbolError(
                f"Could not login on any symbol ({ ', '.join(symbols) })"
            )

    async def _login_cert(self, symbol: str, wa: str, wctx: str, wresult: str) -> bool:
        self._log.debug(f'Attempting UONETPLUS login on "{ symbol }"')

        text = await self.http.uonetplus_send_cert(symbol, wa, wctx, wresult)

        if "nie został zarejestrowany" in text or "VParam" not in text:
            return False

        self._uonetplus_text = text
        self._uonetplus_permissions = utils.get_script_param(text, "permissions")

        return True

    async def get_students(self) -> list[Student]:
        assert self.logged_in and self._uonetplus_text

        instances = utils.extract_instances(self._uonetplus_text)
        units = await self.http.uzytkownik_get_reporting_units(self.symbol)

        students = await asyncio.gather(
            *[
                self._get_students_for_instance(instance, units)
                for instance in instances
            ]
        )

        self.students = [s for sub in students for s in sub]

        return self.students

    async def _get_students_for_instance(
        self, instance: str, units: list[ReportingUnit]
    ) -> list[Student]:
        students = []

        text = await self.http.uczen_start(self.symbol, instance)
        if "VParam" not in text:
            raise ScraperException("VParam not found on uczen start page")

        aft = utils.get_script_param(text, "antiForgeryToken")
        ag = utils.get_script_param(text, "appGuid")
        v = utils.get_script_param(text, "version")
        school_name = utils.get_script_param(text, "organizationName")

        headers = {
            "X-V-AppGuid": ag,
            "X-V-AppVersion": v,
            "X-V-RequestVerificationToken": aft,
        }

        registers = await self.http.uczen_get_registers(self.symbol, instance, headers)
        for register in registers:
            unit = (
                utils.get_first(units, id=register.periods[0].unit_id)
                if register.periods
                else None
            )
            students.append(
                Student(self, instance, headers, school_name, register, unit)
            )

        return students

    async def _get_login_info(self, host: str, symbol: str):
        text, url = await self.http.get_login_page(host, symbol)
        info = utils.extract_login_info(text)
        info.url = url
        return info

    async def close(self):
        """
        Closes the client
        """
        await self.http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
