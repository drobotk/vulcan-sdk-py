class CUFS:
    START: str = "/{SYMBOL}/Account/LogOn?ReturnUrl=%2F{SYMBOL}%2FFS%2FLS%3Fwa%3Dwsignin1.0%26wtrealm%3D{REALM}"
    LOGOUT: str = "/{SYMBOL}/FS/LS?wa=wsignout1.0"


class UONETPLUS:
    START: str = "/{SYMBOL}"


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
    ZEBRANIA_GET: str = "/{SYMBOL}/{INSTANCE}/Zebrania.mvc/Get"
    PLANZAJEC_GET: str = "/{SYMBOL}/{INSTANCE}/PlanZajec.mvc/Get"
