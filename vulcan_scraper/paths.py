class CUFS:
    LOGIN_PAGE: str = "/{SYMBOL}/Account/LogOn"
    SEND_CREDENTIALS: str = "/{SYMBOL}/Account/LogOn?ReturnUrl=%2F{SYMBOL}%2FFS%2FLS%3Fwa%3Dwsignin1.0%26wtrealm%3Dhttps%253a%252f%252fuonetplus.vulcan.net.pl%252f{SYMBOL}%252fLoginEndpoint.aspx%26wctx%3Dhttps%253a%252f%252fuonetplus.vulcan.net.pl%252f{SYMBOL}%252fLoginEndpoint.aspx"


class UONETPLUS:
    LOGIN: str = "/{SYMBOL}/LoginEndpoint.aspx"


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
