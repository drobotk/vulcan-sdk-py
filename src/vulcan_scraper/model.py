from dataclasses import dataclass, is_dataclass
from typing import Any
from datetime import datetime
from bs4 import BeautifulSoup

from .error import ScraperException


def reprable(*attrs):
    def wrapper(cls):
        def __repr__(self) -> str:
            return f'<{self.__class__.__name__} { " ".join([ f"{attr}={repr(getattr(self, attr))}" for attr in attrs ]) }>'

        cls.__repr__ = __repr__

        return cls

    return wrapper


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


def get_default(data: dict, key: str, default: Any):
    return data.get(key, default) or default


class CertificateResponse:
    def __init__(self, text: str):
        soup = BeautifulSoup(text, "lxml")
        try:
            self.action: str = soup.select("form")[0]["action"]
            self.wa: str = soup.select('input[name="wa"]')[0]["value"]
            self.wresult: str = soup.select('input[name="wresult"]')[0]["value"]

            s = soup.select('input[name="wctx"]')
            self.wctx: str = s[0]["value"] if s else None

        except Exception as e:
            raise ScraperException(
                f"Certificate Response parse error: {e.__class__.__name__}: {e}"
            )

    @property
    def request_body(self) -> dict[str, str]:
        data = {"wa": self.wa, "wresult": self.wresult}
        if self.wctx:
            data["wctx"] = self.wctx

        return data


@dataclass
class Feedback:
    Handled: bool = None
    FType: str = None
    Message: str = None
    ExceptionType: Any = None
    ExceptionMessage: str = None
    InnerExceptionMessage: str = None
    Action: Any = None
    data: Any = None
    success: bool = None
    requestId: Any = None


@nested_dataclass
class ApiResponse:
    success: bool
    data: Any = None
    feedback: Feedback = None


@reprable("id", "abbreviation")
class ReportingUnit:
    def __init__(self, **data):
        self.id: int = data["IdJednostkaSprawozdawcza"]
        self.abbreviation: str = data["Skrot"]
        self.sender_id: int = data["Id"]
        self.sender_name: str = data["NazwaNadawcy"]
        self.roles: list[int] = data["Role"]


@reprable("id", "number", "start", "end")
class Period:
    def __init__(self, **data):
        self.id: int = data["Id"]
        self.class_id: int = data["IdOddzial"]
        self.unit_id = data["IdJednostkaSprawozdawcza"]
        self.number: int = data["NumerOkresu"]
        self.level: int = data["Poziom"]
        self.start: datetime = datetime.fromisoformat(data["DataOd"])
        self.end: datetime = datetime.fromisoformat(data["DataDo"])
        self.is_last: bool = data["IsLastOkres"]


@reprable("register_id", "student_id", "year", "level")
class StudentRegister:
    def __init__(self, **data):
        self.is_register: bool = data["IsDziennik"]
        self.id: int = data["Id"]
        self.register_id: int = data["IdDziennik"]
        self.kindergarten_register_id: int = data["IdPrzedszkoleDziennik"]
        self.name: str = get_default(data, "Nazwa", "")
        self.level: int = data["Poziom"]
        self.symbol: str = get_default(data, "Symbol", "")
        self.year: int = data["DziennikRokSzkolny"]

        self.student_id: int = data["IdUczen"]
        self.student_first_name: str = data["UczenImie"]
        self.student_middle_name: str = get_default(data, "UczenImie2", "")
        self.student_last_name: str = data["UczenNazwisko"]
        self.student_full_name_with_year: str = data["UczenPelnaNazwa"]

        self.periods: list[Period] = [Period(**d) for d in data["Okresy"]]


@reprable("entry", "weight", "symbol", "description", "date")
class Grade:
    def __init__(self, **data):
        self.entry: str = data["Wpis"]
        self.color: int = data["KolorOceny"]
        self.symbol: str = data["KodKolumny"]
        self.description: str = data["NazwaKolumny"]
        self.weight: float = data["Waga"]
        self.date: datetime = datetime.strptime(data["DataOceny"], "%d.%m.%Y")

    def __str__(self) -> str:
        return self.entry


@reprable("subject_name", "average")
class SubjectGrades:
    def __init__(self, **data):
        self.subject_name: str = data["Przedmiot"]
        self.subject_visible: bool = data["WidocznyPrzedmiot"]
        self.position: int = data["Pozycja"]
        self.average: float = data["Srednia"]
        self.proposed_annual: str = data["ProponowanaOcenaRoczna"]
        self.annual: str = data["OcenaRoczna"]
        self.proposed_annual_points: str = get_default(
            data, "ProponowanaOcenaRocznaPunkty", ""
        )
        self.annual_points: str = get_default(data, "OcenaRocznaPunkty", "")
        self.points_sum: str = get_default(data, "SumaPunktow", "")
        self.grades: list[Grade] = [Grade(**d) for d in data["OcenyCzastkowe"]]
        self.grades.sort(key=lambda grade: grade.date)

    def __str__(self) -> str:
        return self.subject_name


@reprable("subject_name")
class DescriptiveAssessment:
    def __init__(self, **data):
        self.subject_name: str = data["NazwaPrzedmiotu"]
        self.assessment: str = data["Opis"]
        self.is_religia_etyka: bool = data["IsReligiaEtyka"]

    def __str__(self) -> str:
        return self.assessment


@reprable("is_average_available", "uses_points", "grades_type")
class GradesData:
    def __init__(self, **data):
        self.is_average_available: bool = data["IsSrednia"]
        self.uses_points: bool = data["IsPunkty"]
        self.grades_type: int = data["TypOcen"]
        self.is_last_period: bool = data["IsOstatniSemestr"]
        self.is_adult: bool = data["IsDlaDoroslych"]
        self.subjects: list[SubjectGrades] = [SubjectGrades(**d) for d in data["Oceny"]]
        self.descriptive: list[DescriptiveAssessment] = [
            DescriptiveAssessment(**d) for d in data["OcenyOpisowe"]
        ]


@reprable("date", "category", "teacher")
class Note:
    def __init__(self, **data):
        self.date: datetime = datetime.fromisoformat(data["DataWpisu"])
        self.teacher: str = data["Nauczyciel"]
        self.category: str = data["Kategoria"]
        self.content: str = data["TrescUwagi"]
        self.category_type: int = get_default(data, "KategoriaTyp", 0)
        self.points: str = get_default(data, "Punkty", "")
        self.show_points: bool = get_default(data, "PokazPunkty", False)


class NotesAndAchievementsData:
    def __init__(self, **data):
        self.notes: list[Note] = [Note(**d) for d in data["Uwagi"]]
        self.notes.sort(key=lambda note: note.date)
        self.achievements: list[str] = data["Osiagniecia"]


@reprable("title", "topic", "date")
class Meeting:
    def __init__(self, **data):
        self.id: int = data["Id"]
        self.topic: str = data["TematZebrania"]
        self.agenda: str = data["Agenda"]
        self.people_present: str = data["ObecniNaZebraniu"]
        self.online: str = get_default(data, "ZebranieOnline", "")

        split = data["Tytul"].split(", ")
        self.title: str = ", ".join(split[2:])

        date = get_default(data, "DataSpotkania", "")
        if date:
            self.date = datetime.fromisoformat(date)
        else:
            self.date = datetime.strptime(
                split[1].replace(" godzina", ""), "%d.%m.%Y %H:%M"
            )


class TimetableHeader:
    def __init__(self, **data):
        self.text: str = data["Text"]
        self.width: str = get_default(data, "Width", "")
        self.distinction: bool = data["Distinction"]
        self.flex: int = data["Flex"]


class TimetableAdditional:
    def __init__(self, **data):
        self.header: str = data["Header"]
        self.descriptions: list[str] = [
            d["Description"] for d in data["Descriptions"]
        ]  # weird


class TimetableResponse:
    def __init__(self, **data):
        self.date: str = data["Data"]
        self.headers: list[TimetableHeader] = [
            TimetableHeader(**d) for d in data["Headers"]
        ]
        self.rows: list[list[str]] = data["Rows"]
        self.additionals: list[TimetableAdditional] = [
            TimetableAdditional(**d) for d in data["Additionals"]
        ]


@reprable("date", "subject", "type", "description")
class Exam:
    date: datetime
    type: str

    def __init__(self, **data):
        self.entry_date: datetime = datetime.fromisoformat(data["DataModyfikacji"])
        self.subject: str = data["Nazwa"]
        self.type = data["Rodzaj"]
        self.teacher: str = data["Pracownik"]
        self.description: str = data["Opis"]


class ExamsDay:
    def __init__(self, **data):
        self.date: datetime = datetime.fromisoformat(data["Data"])
        self.exams: list[Exam] = [Exam(**d) for d in data["Sprawdziany"]]


class ExamsResponse:
    def __init__(self, data):
        self.days = [
            ExamsDay(**d) for x in data for d in x["SprawdzianyGroupedByDayList"]
        ]
