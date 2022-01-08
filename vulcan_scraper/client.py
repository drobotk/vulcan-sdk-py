import logging
import asyncio
import sys
from typing import Optional

from .error import *
from .http import HTTP
from .student import Student
from .model import CertificateResponse, ReportingUnit
from .enum import LoginType
from . import utils

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
        if self.symbol and not utils.re_valid_symbol.fullmatch(self.symbol):
            raise ValueError("Symbol can only contain letters and numbers")

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

        info = await self._get_login_info()
        if info.type is LoginType.UNKNOWN:
            raise ScraperException(
                f'Unknown login type on "{self.http.base_host}/{self.symbol}"'
            )

        self._log.debug(info)

        login = self.email
        if info.prefix and "@" not in login:
            login = f"{info.prefix}\\{login}"

        if info.type is LoginType.CUFS:
            text, _ = await self.http.request(
                "POST",
                info.url,
                data={"LoginName": login, "Password": self.password},
            )

        else:
            if info.type is LoginType.ADFS:
                data = {
                    "UserName": login,
                    "Password": self.password,
                    "AuthMethod": "FormsAuthentication",
                }
            elif info.type is LoginType.ADFSCards:
                data = {
                    "UsernameTextBox": login,
                    "PasswordTextBox": self.password,
                    "__VIEWSTATE": info.vs,
                    "__VIEWSTATEGENERATOR": info.vsg,
                    "__EVENTVALIDATION": info.ev,
                    "__db": info.db,
                    "SubmitButton.x": "0",
                    "SubmitButton.y": "0",
                }
            elif info.type is LoginType.ADFSLight:
                data = {"Username": login, "Password": self.password}

            text, _ = await self.http.request("POST", info.url, data=data)

            cres = CertificateResponse(text)
            text, _ = await self.http.request(
                "POST",
                cres.action,
                data={"wa": cres.wa, "wctx": cres.wctx, "wresult": cres.wresult},
            )

        cres = CertificateResponse(text)

        if not self.symbol:
            symbols = utils.extract_symbols(cres.wresult)
            self._log.debug(f"Extracted symbols: { symbols }")

        else:
            symbols = [self.symbol]

        try:
            symbols.remove(self.http.SYMBOL_DEFAULT)
        except ValueError:
            pass

        for s in symbols:
            if await self._login_uonetplus(s, cres.wa, cres.wctx, cres.wresult):
                self.logged_in = True
                self.symbol = s
                break

        if not self.logged_in:
            raise NoValidSymbolException(
                f"Could not login on any symbol ({ ', '.join(symbols) })"
            )

    async def _login_uonetplus(
        self, symbol: str, wa: str, wctx: str, wresult: str
    ) -> bool:
        text = await self.http.uonetplus_send_cert(symbol, wa, wctx, wresult)

        if "nie został zarejestrowany" in text:
            return False

        assert "VParam" in text

        self._uonetplus_text = text
        self._uonetplus_permissions = utils.get_script_param(text, "permissions")

        return True

    async def get_students(self) -> list[Student]:
        """Fetches all students from all schools available on the account"""

        if not self.logged_in:
            raise NotLoggedInException

        assert self._uonetplus_text

        instances = utils.extract_instances(self._uonetplus_text)
        try:  # 05.01.2021 - endpoint failing constantly
            units = await self.http.uzytkownik_get_reporting_units(self.symbol)
        except VulcanException:
            self._log.warn(
                "Failed to fetch reporting units. Some student data might be unavailable"
            )
            units = []

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

    async def _get_login_info(self):
        text, url = await self.http.get_login_page(self.symbol)
        info = utils.extract_login_info(text)
        info.url = url
        return info

    async def logout(self):
        if not self.logged_in:
            raise NotLoggedInException

        await self.http.uonetplus_logout(self.symbol)
        await self.http.cufs_logout(self.symbol)
        self.http.session.cookie_jar.clear()
        self.logged_in = False

    async def close(self):
        """Logs out and closes the client"""

        if self.logged_in:
            await self.logout()

        await self.http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
