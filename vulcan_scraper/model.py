from dataclasses import dataclass
from typing import *
from datetime import datetime

from .utils import nested_dataclass, get_default, reprable

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

@reprable("id", "number", "start", "end")
class Period:
    def __init__( self, **data ):
        self.id: int = data["Id"]
        self.class_id: int = data["IdOddzial"]
        self.unit_id = data["IdJednostkaSprawozdawcza"]
        self.number: int = data["NumerOkresu"]
        self.level: int = data["Poziom"]
        self.start: datetime = datetime.fromisoformat( data["DataOd"] )
        self.end: datetime = datetime.fromisoformat( data["DataDo"] )
        self.is_last: bool = data["IsLastOkres"]

@reprable("register_id", "student_id", "year", "level")
class StudentRegister:
    def __init__( self, **data ):
        self.is_register: bool = data["IsDziennik"]
        self.id: int = data["Id"]
        self.register_id: int = data["IdDziennik"]
        self.kindergarten_register_id: int = data["IdPrzedszkoleDziennik"]
        self.name: str = get_default( data, "Nazwa", "")
        self.level: int = data["Poziom"]
        self.symbol: str = get_default( data, "Symbol", "")
        self.year: int = data["DziennikRokSzkolny"]

        self.student_id: int = data["IdUczen"]
        self.student_first_name: str = data["UczenImie"]
        self.student_middle_name: str = get_default( data, "UczenImie2", "")
        self.student_last_name: str = data["UczenNazwisko"]
        self.student_full_name_with_year: str = data["UczenPelnaNazwa"]

        self.periods: list[Period] = [ Period(**d) for d in data["Okresy"] ]

@reprable("entry", "weight", "symbol", "description", "date")
class Grade:
    def __init__( self, **data ):
        self.entry: str = data["Wpis"]
        self.color: int = data["KolorOceny"]
        self.symbol: str = data["KodKolumny"]
        self.description: str = data["NazwaKolumny"]
        self.weight: float = data["Waga"]
        self.date: str = data["DataOceny"]

    def __str__( self ) -> str:
        return self.entry

@reprable("subject_name", "average")
class SubjectGrades:
    def __init__( self, **data ):
        self.subject_name: str = data["Przedmiot"]
        self.subject_visible: bool = data["WidocznyPrzedmiot"]
        self.position: int = data["Pozycja"]
        self.average: float = data["Srednia"]
        self.proposed_annual: str = data["ProponowanaOcenaRoczna"]
        self.annual: str = data["OcenaRoczna"]
        self.proposed_annual_points: str = get_default( data, "ProponowanaOcenaRocznaPunkty", "")
        self.annual_points: str = get_default( data, "OcenaRocznaPunkty", "")
        self.points_sum: str = get_default( data, "SumaPunktow", "")
        self.grades: list[Grade] = [ Grade(**d) for d in data["OcenyCzastkowe"] ]

    def __str__( self ) -> str:
        return self.subject_name

@reprable("subject_name")
class DescriptiveAssessment:
    def __init__( self, **data ):
        self.subject_name: str = data["NazwaPrzedmiotu"]
        self.assessment: str = data["Opis"]
        self.is_religia_etyka: bool = data["IsReligiaEtyka"]

    def __str__( self ) -> str:
        return self.assessment

@reprable("is_average_available", "uses_points", "grades_type")
class GradesData:
    def __init__( self, **data ):
        self.is_average_available: bool = data["IsSrednia"]
        self.uses_points: bool = data["IsPunkty"]
        self.grades_type: int = data["TypOcen"]
        self.is_last_period: bool = data["IsOstatniSemestr"]
        self.is_adult: bool = data["IsDlaDoroslych"]
        self.subjects: list[SubjectGrades] = [ SubjectGrades(**d) for d in data["Oceny"] ]
        self.descriptive: list[DescriptiveAssessment] = [ DescriptiveAssessment(**d) for d in data["OcenyOpisowe"] ]

@reprable("date", "category", "teacher")
class Note:
    def __init__( self, **data ):
        self.date: datetime = datetime.fromisoformat( data["DataWpisu"] )
        self.teacher: str = data["Nauczyciel"]
        self.category: str = data["Kategoria"]
        self.content: str = data["TrescUwagi"]
        self.category_type: int = get_default( data, "KategoriaTyp", 0 )
        self.points: str = get_default( data, "Punkty", "")
        self.show_points: bool = get_default( data, "PokazPunkty", False )

class NotesAndAchievementsData:
    def __init__( self, **data ):
        self.notes: list[Note] = [ Note(**d) for d in data["Uwagi"] ]
        self.notes.sort( key = lambda note: note.date )
        self.achievements: list[str] = data["Osiagniecia"]