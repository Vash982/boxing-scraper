import requests as req

class SessionManager:
    URL_ATLETI = "https://www.fpi.it/atleti.html"

    @staticmethod
    def init_session() -> req.Session:
        s = req.Session()
        s.get(SessionManager.URL_ATLETI)
        return s
