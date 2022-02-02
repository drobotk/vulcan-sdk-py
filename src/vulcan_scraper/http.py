from logging import getLogger
from aiohttp import ClientSession
from json import loads
from urllib.parse import quote
from datetime import datetime

from . import paths
from .error import ScraperException, HTTPException, VulcanException
from .model import (
    ApiResponse,
    CertificateResponse,
    ReportingUnit,
    StudentRegister,
    GradesData,
    NotesAndAchievementsData,
    TimetableResponse,
    Meeting,
    ExamsResponse,
    HomeworkResponse,
    UonetplusTileResponse,
)
from .utils import check_for_vulcan_error


class HTTP:
    SYMBOL_DEFAULT = "Default"

    def __init__(self, host: str, ssl: bool = True):
        self.base_host = host
        self.ssl = ssl

        self._log = getLogger(__name__)
        self.session = ClientSession()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"
            }
        )

    async def close(self):
        if self.session:
            await self.session.close()

    def build_url(
        self,
        *,
        ssl: bool = None,
        host: str = None,
        subd: str = None,
        path: str = None,
        **kwargs,
    ) -> str:
        s = self.ssl if ssl is None else ssl
        url = "https://" if s else "http://"

        if subd:
            url += f"{subd}."

        url += host or self.base_host

        if path:
            url += path

        if not kwargs.get("symbol"):
            kwargs["symbol"] = self.SYMBOL_DEFAULT

        for k in kwargs:
            url = url.replace(f"{{{k.upper()}}}", str(kwargs[k]))

        return url

    async def request(self, verb: str, url: str, **kwargs) -> tuple[str, str]:
        verb = verb.upper()
        async with self.session.request(verb, url, **kwargs) as res:
            for r in res.history:
                self._log.debug(f"{r.status} {r.method} {r.url}")

            self._log.debug(f"{res.status} {res.method} {res.url}")

            if not res.ok:
                raise HTTPException(f"{verb} {url} got {res.status}")

            text = await res.text()
            if res.content_type.lower().split("/")[-1] != "json":
                check_for_vulcan_error(text)

            return (text, str(res.url))

    async def api_request(self, verb: str, url: str, **kwargs):
        text, _ = await self.request(verb, url, **kwargs)
        try:
            data = loads(text)
        except:
            raise ScraperException("Failed to parse JSON data")

        res = ApiResponse(**data)
        if not res.success:
            msg = (
                res.feedback.Message
                if res.feedback is not None
                else f"{verb} {url} {res.success = }"
            )
            raise VulcanException(msg)

        return res.data

    async def get_login_page(self, symbol: str = None) -> tuple[str, str]:
        realm = self.build_url(subd="uonetplus")
        url = self.build_url(
            subd="cufs",
            path=paths.CUFS.START,
            symbol=symbol,
            realm=quote(quote(realm, safe=""), safe=""),  # double encoding
        )
        return await self.request("GET", url)

    async def execute_cert_form(self, cres: CertificateResponse) -> str:
        return (await self.request("POST", cres.action, data=cres.request_body))[0]

    async def uonetplus_send_cert(self, symbol: str, data: dict[str, str]) -> str:
        url = self.build_url(
            subd="uonetplus", path=paths.UONETPLUS.START, symbol=symbol
        )
        return (await self.request("POST", url, data=data))[0]

    async def cufs_logout(self, symbol) -> str:
        url = self.build_url(subd="cufs", path=paths.CUFS.LOGOUT, symbol=symbol)
        return (await self.request("GET", url))[0]

    async def uczen_start(self, symbol: str, schoolid: str) -> str:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.START,
            symbol=symbol,
            schoolid=schoolid,
        )
        return (await self.request("GET", url))[0]

    async def uzytkownik_get_reporting_units(self, symbol: str) -> list[ReportingUnit]:
        url = self.build_url(
            subd="uonetplus-uzytkownik",
            path=paths.UZYTKOWNIK.NOWAWIADOMOSC_GETJEDNOSTKIUZYTKOWNIKA,
            symbol=symbol,
        )
        data = await self.api_request("GET", url)
        return [ReportingUnit(**x) for x in data]

    async def uczen_get_registers(
        self, symbol: str, schoolid: str, headers: dict[str, str]
    ) -> list[StudentRegister]:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.UCZENDZIENNIK_GET,
            symbol=symbol,
            schoolid=schoolid,
        )
        data = await self.api_request("POST", url, headers=headers)
        return [StudentRegister(**x) for x in data]

    async def uczen_get_grades(
        self,
        symbol: str,
        schoolid: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        period_id: int,
    ) -> GradesData:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.OCENY_GET,
            symbol=symbol,
            schoolid=schoolid,
        )
        data = await self.api_request(
            "POST", url, headers=headers, cookies=cookies, json={"okres": period_id}
        )
        return GradesData(**data)

    async def uczen_get_notes_achievements(
        self,
        symbol: str,
        schoolid: str,
        headers: dict[str, str],
        cookies: dict[str, str],
    ) -> NotesAndAchievementsData:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.UWAGIIOSIAGNIECIA_GET,
            symbol=symbol,
            schoolid=schoolid,
        )
        data = await self.api_request("POST", url, headers=headers, cookies=cookies)
        return NotesAndAchievementsData(**data)

    async def uczen_get_meetings(
        self,
        symbol: str,
        schoolid: str,
        headers: dict[str, str],
        cookies: dict[str, str],
    ) -> list[Meeting]:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.ZEBRANIA_GET,
            symbol=symbol,
            schoolid=schoolid,
        )
        data = await self.api_request("POST", url, headers=headers, cookies=cookies)
        return [Meeting(**x) for x in data]

    async def uczen_get_timetable(
        self,
        symbol: str,
        schoolid: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        date: datetime,
    ) -> TimetableResponse:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.PLANZAJEC_GET,
            symbol=symbol,
            schoolid=schoolid,
        )
        data = await self.api_request(
            "POST",
            url,
            headers=headers,
            cookies=cookies,
            data={"data": date.strftime("%Y-%m-%dT00:00:00")},
        )
        return TimetableResponse(**data)

    async def uczen_get_exams(
        self,
        symbol: str,
        schoolid: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        date: datetime,
        year: int,
    ) -> ExamsResponse:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.SPRAWDZIANY_GET,
            symbol=symbol,
            schoolid=schoolid,
        )
        data = await self.api_request(
            "POST",
            url,
            headers=headers,
            cookies=cookies,
            data={"data": date.strftime("%Y-%m-%dT00:00:00"), "rokSzkolny": year},
        )
        return ExamsResponse(data)

    async def uczen_get_homework(
        self,
        symbol: str,
        schoolid: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        date: datetime,
        year: int,
    ) -> HomeworkResponse:
        url = self.build_url(
            subd="uonetplus-uczen",
            path=paths.UCZEN.HOMEWORK_GET,
            symbol=symbol,
            schoolid=schoolid,
        )
        data = await self.api_request(
            "POST",
            url,
            headers=headers,
            cookies=cookies,
            data={"date": date.strftime("%Y-%m-%dT00:00:00"), "schoolYear": year},
        )
        return HomeworkResponse(data)

    async def uonetplus_get_lucky_numbers(
        self, symbol: str, permissions: str
    ) -> list[UonetplusTileResponse]:
        url = self.build_url(
            subd="uonetplus",
            path=paths.UONETPLUS.GETKIDSLUCKYNUMBERS,
            symbol=symbol,
        )
        data = await self.api_request("POST", url, data={"permissions": permissions})
        return [UonetplusTileResponse(**x) for x in data]

    async def uonetplus_get_school_announcements(
        self, symbol: str, permissions: str
    ) -> list[UonetplusTileResponse]:
        url = self.build_url(
            subd="uonetplus",
            path=paths.UONETPLUS.GETSTUDENTDIRECTORINFORMATIONS,
            symbol=symbol,
        )
        data = await self.api_request("POST", url, data={"permissions": permissions})
        return [UonetplusTileResponse(**x) for x in data]
