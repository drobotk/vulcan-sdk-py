from .http import HTTP
from .model import LuckyNumber, SchoolAnnouncement
from .error import ScraperException
from .utils import sub_after
from datetime import datetime
from bs4 import BeautifulSoup


class Uonetplus:
    # set later
    symbol: str
    text: str
    permissions: str

    def __init__(self, vulcan):
        self._v = vulcan
        self._http: HTTP = vulcan.http

    async def get_lucky_numbers(self) -> list[LuckyNumber]:
        if not self.symbol or not self.permissions:
            raise ScraperException("Uonetplus service module not initialized")

        data = await self._http.uonetplus_get_lucky_numbers(
            self.symbol, self.permissions
        )
        ret = []
        for instance in data:
            for unit in instance.content:
                for number in unit.content:
                    value = int(sub_after(number.name, ": "))
                    ret.append(
                        LuckyNumber(
                            instance_name=instance.name,
                            unit_abbr=unit.name,
                            value=value,
                        )
                    )

        return ret

    async def get_school_announcements(self) -> list[SchoolAnnouncement]:
        if not self.symbol or not self.permissions:
            raise ScraperException("Uonetplus service module not initialized")

        data = await self._http.uonetplus_get_school_announcements(
            self.symbol, self.permissions
        )
        ret = []
        for wrapper in data:
            for announcement in wrapper.content:
                date = datetime.strptime(announcement.name[:10], "%d.%m.%Y")
                subject = announcement.name[11:]
                content = BeautifulSoup(
                    announcement.data.replace("<br />", "\n"), "lxml"
                ).text
                ret.append(
                    SchoolAnnouncement(date=date, subject=subject, content=content)
                )

        return ret
