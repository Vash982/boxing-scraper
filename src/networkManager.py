import requests as req
from bs4 import BeautifulSoup

class NetworkManager:
    #urls to recive dynamic options in roder to show the correct available options in the gui
    URL_ATLETI = "https://www.fpi.it/atleti.html"
    URL_QUALIFICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_qualifiche"
    URL_PESO = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_peso"
    URL_STATISTICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_totalizzatori"
    cache = dict()

    """
    the html corresponding to URL_ATLETI has a form with post method composed of select-option tags,
    you have to create a dictionary to send as parameter to compile the form.
    However, there are form fields whose options are generated dynamically by javascript.
    To have access to the available info and their values you need to access the php that provides them.
    sending a payload to php this responds with a list of options based on the data received.
    For this you have to create an initial payload with form options that are constant,
    and update the payload to each request get to php of the field you want to compile. """
    payload = {
        'id_tipo_tessera': '5',  # Atleta dilettante IBA
        'sesso': 'M'
    }

    def __init__(self) -> None:
        self.session = self.initSession()

    #initialize the session in order to get cookies and tokens if necessary
    def initSession(self) -> req.Session:
        s = req.Session()
        try:
            s.get(self.URL_ATLETI)
        except:
            s.verify = False
            s.get(self.URL_ATLETI)
        return s

    #scraps available options and their relative int value from the HTML souce code
    def getComitati(self) -> dict[str, int]:
        if "comitati" in self.cache:
            return self.cache["comitati"]
        response = self.session.get(self.URL_ATLETI)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            select_element = soup.find("select", id="id_comitato_atleti")
            comitati = {option.text: option["value"] for option in select_element.find_all("option")}
            self.cache["comitati"] = comitati
            return comitati
        return {}
        
    #scraps available options and their relative int value from the HTML souce code
    def getOptions(self, url: str) -> dict[str, int]:
        response = self.session.get(url, params=self.payload)
        if response.status_code == 200:
            options_soup = BeautifulSoup(response.text, 'html.parser')
            options = {option.text: option["value"] for option in options_soup.find_all("option") if option['value']}
            self.cache[url] = options
            return options
        return {}

    def cleanQualifica(self):
        if self.payload.get("qualifica") is not None:
            self.payload.pop("qualifica")
        if self.payload.get("id_qualifica") is not None:
            self.payload.pop("id_qualifica")
        if self.payload.get("id_peso") is not None:
            self.payload.pop("id_peso")

    def fetch_athletes(self, url: str) -> list:
        response = self.session.post(url, params=self.payload)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find_all('div', class_='atleta')
        return []

    def get_athlete_stats(self, matricola: str) -> dict[str, int]:
        if matricola in self.cache:
            return self.cache[matricola]
        response = self.session.get(self.URL_STATISTICHE, params={'matricola': matricola})
        if response.status_code == 200:
            stats = BeautifulSoup(response.text, 'html.parser').find_all("td")
            statistiche = {
                "numero_match": int(stats[0].text),
                "vittorie": int(stats[1].text),
                "sconfitte": int(stats[2].text),
                "pareggi": int(stats[3].text),
            }
            self.cache[matricola] = statistiche
            return statistiche
        return {}
