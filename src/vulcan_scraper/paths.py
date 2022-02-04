class CUFS:
    START: str = "/{SYMBOL}/Account/LogOn?ReturnUrl=%2F{SYMBOL}%2FFS%2FLS%3Fwa%3Dwsignin1.0%26wtrealm%3D{REALM}"
    LOGOUT: str = "/{SYMBOL}/FS/LS?wa=wsignout1.0"


class UONETPLUS:
    START: str = "/{SYMBOL}/LoginEndpoint.aspx"
    GETKIDSLUCKYNUMBERS: str = "/{SYMBOL}/Start.mvc/GetKidsLuckyNumbers"
    GETSTUDENTDIRECTORINFORMATIONS: str = (
        "/{SYMBOL}/Start.mvc/GetStudentDirectorInformations"
    )


class UZYTKOWNIK:
    NOWAWIADOMOSC_GETJEDNOSTKIUZYTKOWNIKA: str = (
        "/{SYMBOL}/NowaWiadomosc.mvc/GetJednostkiUzytkownika"
    )


class UCZEN:
    START: str = "/{SYMBOL}/{SCHOOLID}/Start"
    UCZENCACHE_GET: str = "/{SYMBOL}/{SCHOOLID}/UczenCache.mvc/Get"
    UCZENDZIENNIK_GET: str = "/{SYMBOL}/{SCHOOLID}/UczenDziennik.mvc/Get"
    OCENY_GET: str = "/{SYMBOL}/{SCHOOLID}/Oceny.mvc/Get"
    STATYSTYKI_GETOCENYCZASTKOWE: str = (
        "/{SYMBOL}/{SCHOOLID}/Statystyki.mvc/GetOcenyCzastkowe"
    )
    UWAGIIOSIAGNIECIA_GET: str = "/{SYMBOL}/{SCHOOLID}/UwagiIOsiagniecia.mvc/Get"
    ZEBRANIA_GET: str = "/{SYMBOL}/{SCHOOLID}/Zebrania.mvc/Get"
    PLANZAJEC_GET: str = "/{SYMBOL}/{SCHOOLID}/PlanZajec.mvc/Get"
    SPRAWDZIANY_GET: str = "/{SYMBOL}/{SCHOOLID}/Sprawdziany.mvc/Get"
    HOMEWORK_GET: str = "/{SYMBOL}/{SCHOOLID}/Homework.mvc/Get"
    REFRESHSESSION: str = "/{SYMBOL}/{SCHOOLID}/Home.mvc/RefreshSession"
