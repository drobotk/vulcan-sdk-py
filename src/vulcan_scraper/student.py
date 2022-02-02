from datetime import datetime
from typing import Optional

from .model import (
    SchoolAnnouncement,
    reprable,
    StudentRegister,
    ReportingUnit,
    GradesData,
    NotesAndAchievementsData,
    Meeting,
    Exam,
    Homework,
)
from .http import HTTP
from .uonetplus import Uonetplus
from .timetable import Timetable
from .utils import sub_before, reverse_teacher_name, get_monday, Instance, get_first


@reprable("first_name", "last_name", "class_symbol", "year", "school_name")
class Student:
    def __init__(
        self,
        vulcan,
        instance: Instance,
        headers: dict[str, str],
        school_name: str,
        reg: StudentRegister,
        unit: Optional[ReportingUnit] = None,
    ):
        self._v = vulcan
        self._http: HTTP = vulcan.http
        self._uonetplus: Uonetplus = vulcan.uonetplus
        self._symbol = vulcan.symbol
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
            self._instance.id,
            self._headers,
            self._cookies,
            period_id=period_id,
        )

    async def get_notes_and_achievements(self) -> NotesAndAchievementsData:
        return await self._http.uczen_get_notes_achievements(
            self._symbol,
            self._instance.id,
            self._headers,
            self._cookies,
        )

    async def get_meetings(self) -> list[Meeting]:
        meetings = await self._http.uczen_get_meetings(
            self._symbol,
            self._instance.id,
            self._headers,
            self._cookies,
        )
        return sorted(meetings, key=lambda m: m.date)

    async def get_timetable(self, week_day: datetime) -> Timetable:
        """
        Get the student's timetable for the week `week_day` is in.

        You can use `datetime.now()` to get current week's timetable
        """
        data = await self._http.uczen_get_timetable(
            self._symbol,
            self._instance.id,
            self._headers,
            self._cookies,
            get_monday(week_day),
        )

        return Timetable(data)

    async def get_exams(self, week_day: datetime) -> list[Exam]:
        """
        Get the student's exams for the next 4 weeks starting from the week `week_day` is in.
        """
        data = await self._http.uczen_get_exams(
            self._symbol,
            self._instance.id,
            self._headers,
            self._cookies,
            get_monday(week_day),
            self.year,
        )

        type_to_name = {1: "Sprawdzian", 2: "Kartkówka", 3: "Praca Klasowa"}

        exams = []
        for day in data.days:
            for exam in day.exams:
                exam.date = day.date
                exam.teacher = reverse_teacher_name(sub_before(exam.teacher, " ["))
                exam.type = type_to_name[exam.type]
                exams.append(exam)

        return exams

    async def get_homework(self, week_day: datetime) -> list[Homework]:
        """
        Get the student's homework for the week `week_day` is in.
        """
        data = await self._http.uczen_get_homework(
            self._symbol,
            self._instance.id,
            self._headers,
            self._cookies,
            get_monday(week_day),
            self.year,
        )

        homework = []
        for day in data.days:
            for h in day.homework:
                h.teacher = reverse_teacher_name(sub_before(h.teacher, " ["))
                homework.append(h)

        return homework

    async def get_lucky_number(self) -> Optional[int]:
        numbers = await self._uonetplus.get_lucky_numbers()
        if not numbers:
            return

        num = (
            get_first(numbers, unit_abbr=self.school_abbreviation)
            or get_first(numbers, instance_name=self._instance.name)
            or numbers[0]
        )

        return num.value

    async def get_school_announcements(self) -> list[SchoolAnnouncement]:
        # TODO: only return ones relevant to this student
        return await self._uonetplus.get_school_announcements()
