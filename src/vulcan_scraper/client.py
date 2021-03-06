import logging
import asyncio
import sys
from typing import Optional

from .error import (
    ScraperException,
    InvalidSymbolException,
    NotLoggedInException,
    NoValidSymbolException,
)
from .http import HTTP
from .student import Student
from .model import CertificateResponse, ReportingUnit
from .enum import LoginType
from .uonetplus import Uonetplus
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

        self.uonetplus = Uonetplus(self)

        self._cufs_logged_in = False
        self.logged_in = False
        self._units: list[ReportingUnit] = []
        self.students: list[Student] = []

    async def login(self):
        """Attempts the login process using credentials passed in the constructor"""

        self._cufs_logged_in = False
        self.logged_in = False

        cres = await self._send_credentials()
        self._cufs_logged_in = True

        if not self.symbol:
            symbols = utils.extract_symbols(cres.wresult)
            self._log.debug(f"Symbols: { ', '.join(symbols) }")

        else:
            symbols = [self.symbol]

        try:
            symbols.remove(self.http.SYMBOL_DEFAULT)
        except ValueError:
            pass

        for s in symbols:
            if await self._login_uonetplus(s, cres):
                self.logged_in = True
                self.symbol = self.uonetplus.symbol
                break

        if not self.logged_in:
            raise NoValidSymbolException(
                f"Could not login on any symbol ({ ', '.join(symbols) })"
            )

    async def _send_credentials(self) -> CertificateResponse:
        info = await self._get_login_info()
        self._log.debug(info)
        if info.type is LoginType.UNKNOWN:
            raise ScraperException(
                f'Unknown login type on "{self.http.base_host}/{self.symbol}"'
            )

        login = self.email
        if info.prefix and info.prefix not in login and "@" not in login:
            login = rf"{info.prefix}\{login}"

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

            text = await self.http.execute_cert_form(cres)

        return CertificateResponse(text)

    async def _login_uonetplus(self, symbol: str, cres: CertificateResponse) -> bool:
        try:
            text = await self.http.uonetplus_send_cert(symbol, cres.request_body)
        except InvalidSymbolException:
            return False

        assert "VParam" in text

        self.uonetplus.symbol = symbol
        self.uonetplus.text = text
        self.uonetplus.permissions = utils.get_script_param(text, "permissions")
        self.uonetplus.instances = utils.extract_instances(text)

        self._units = await self.http.uzytkownik_get_reporting_units(symbol)

        return True

    async def get_students(self) -> list[Student]:
        """Fetches all students from all schools available on the account"""

        if not self.logged_in:
            raise NotLoggedInException

        assert self.uonetplus.instances, self._units

        students = await asyncio.gather(
            *[
                self._get_students_for_instance(instance, self._units)
                for instance in self.uonetplus.instances
            ]
        )

        self.students = [s for sub in students for s in sub]

        return self.students

    async def _get_uczen_start_data(self, instance_id: str) -> tuple[str, str]:
        text = await self.http.uczen_start(self.symbol, instance_id)
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
        return headers, school_name

    async def _get_students_for_instance(
        self, instance: utils.Instance, units: list[ReportingUnit]
    ) -> list[Student]:
        students = []

        headers, school_name = await self._get_uczen_start_data(instance.id)

        registers = await self.http.uczen_get_registers(
            self.symbol, instance.id, headers
        )
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

    async def refresh_session(self):
        if not self.logged_in:
            raise NotLoggedInException

        if not self.students:
            raise ScraperException("Unable to refresh session: no students in cache")

        await self.students[0].refresh_session()

    async def logout(self):
        if self._cufs_logged_in:
            self._log.debug("Logging out...")
            await self.http.cufs_logout(self.symbol)

        self._cufs_logged_in = False
        self.logged_in = False
        self.http.session.cookie_jar.clear()

    async def close(self):
        """Logs out and closes the client"""

        await self.logout()
        await self.http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
