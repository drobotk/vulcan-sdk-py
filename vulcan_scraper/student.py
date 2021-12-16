from .utils import reprable
from .http import HTTP
from .model import GradesData, StudentRegister

@reprable('first_name', 'last_name', 'class_symbol', 'year', 'school_name')
class Student:
    def __init__( 
        self,
        vulcan,
        instance: str,
        headers: dict[str, str],
        school_name: str,
        reg: StudentRegister
    ):
        self._v = vulcan
        self._http: HTTP = vulcan.http
        self._symbol: str = vulcan.symbol
        self._instance = instance
        self._headers = headers

        self.school_name = school_name
        self.register = reg

        self._cookies = {
            "idBiezacyDziennik":            str( reg.register_id ),
            "idBiezacyUczen":               str( reg.student_id ),
            "idBiezacyDziennikPrzedszkole": str( reg.kindergarten_register_id ),
            "biezacyRokSzkolny":            str( reg.year )
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

    async def get_grades( self, *, period: int = 0 ) -> GradesData:
        period_id = self.register.periods[period].id
        return await self._http.uczen_get_grades(
            self._symbol, self._instance, self._headers, self._cookies,
            period_id = period_id
        )