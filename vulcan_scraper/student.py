from typing import Optional

from .utils import reprable
from .http import HTTP
from .model import (
    GradesData,
    Meeting,
    NotesAndAchievementsData,
    ReportingUnit,
    StudentRegister,
)


@reprable("first_name", "last_name", "class_symbol", "year", "school_name")
class Student:
    def __init__(
        self,
        vulcan,
        instance: str,
        headers: dict[str, str],
        school_name: str,
        reg: StudentRegister,
        unit: Optional[ReportingUnit] = None,
    ):
        self._v = vulcan
        self._http: HTTP = vulcan.http
        self._symbol: str = vulcan.symbol
        self._instance = instance
        self._headers = headers

        self.register = reg
        self.school_name = school_name

        self.reporting_unit = unit
        self.school_abbreviation = unit.abbreviation if unit else ""

        self._cookies = {
            "idBiezacyDziennik": str(reg.register_id),
            "idBiezacyUczen": str(reg.student_id),
            "idBiezacyDziennikPrzedszkole": str(reg.kindergarten_register_id),
            "biezacyRokSzkolny": str(reg.year),
        }

        self.id = reg.student_id
        self.register_id = reg.register_id
        self.first_name = reg.student_first_name
        self.middle_name = reg.student_middle_name
        self.last_name = reg.student_last_name
        self.year = reg.year
        self.level = reg.level
        self.full_name_with_year = reg.student_full_name_with_year
        self.class_symbol = str(reg.level) + reg.symbol

    def __str__(self) -> str:
        return self.full_name_with_year

    async def get_grades(self, *, period: int = 0) -> GradesData:
        period_id = self.register.periods[period].id
        return await self._http.uczen_get_grades(
            self._symbol,
            self._instance,
            self._headers,
            self._cookies,
            period_id=period_id,
        )

    async def get_notes_and_achievements(self) -> NotesAndAchievementsData:
        return await self._http.uczen_get_notes_achievements(
            self._symbol,
            self._instance,
            self._headers,
            self._cookies,
        )

    async def get_meetings(self) -> list[Meeting]:
        return await self._http.uczen_get_meetings(
            self._symbol,
            self._instance,
            self._headers,
            self._cookies,
        )
