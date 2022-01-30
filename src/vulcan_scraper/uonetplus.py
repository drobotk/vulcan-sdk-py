from .http import HTTP
from .model import LuckyNumber
from .error import ScraperException
from .utils import sub_after


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
        for unit in data:
            for school in unit.content:
                for number in school.content:
                    value = int(sub_after(number.name, ": "))
                    ret.append(
                        LuckyNumber(
                            instance_name=unit.name, school=school.name, value=value
                        )
                    )

        return ret
