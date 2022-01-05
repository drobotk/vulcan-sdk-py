class CUFS:
    LOGIN_PAGE: str = "/{SYMBOL}/Account/LogOn?ReturnUrl=%2Fdefault%2FFS%2FLS%3Fwa%3Dwsignin1.0%26wtrealm%3D{REALM}%26wctx%3D{REALM}"
    LOGOUT: str = "/{SYMBOL}/FS/LS?wa=wsignout1.0"


class UONETPLUS:
    LOGIN: str = "/{SYMBOL}/LoginEndpoint.aspx"
    LOGOUT: str = "/{SYMBOL}/?logout=true"


class UZYTKOWNIK:
    NOWAWIADOMOSC_GETJEDNOSTKIUZYTKOWNIKA: str = (
        "/{SYMBOL}/NowaWiadomosc.mvc/GetJednostkiUzytkownika"
    )


class UCZEN:
    START: str = "/{SYMBOL}/{INSTANCE}/Start"
    UCZENCACHE_GET: str = "/{SYMBOL}/{INSTANCE}/UczenCache.mvc/Get"
    UCZENDZIENNIK_GET: str = "/{SYMBOL}/{INSTANCE}/UczenDziennik.mvc/Get"
    OCENY_GET: str = "/{SYMBOL}/{INSTANCE}/Oceny.mvc/Get"
    STATYSTYKI_GETOCENYCZASTKOWE: str = (
        "/{SYMBOL}/{INSTANCE}/Statystyki.mvc/GetOcenyCzastkowe"
    )
    UWAGIIOSIAGNIECIA_GET: str = "/{SYMBOL}/{INSTANCE}/UwagiIOsiagniecia.mvc/Get"
