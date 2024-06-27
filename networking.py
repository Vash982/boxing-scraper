import requests as req
from bs4 import BeautifulSoup
from typing import Any, List, Dict
import certifi

class NetworkManager:
    #urls to recive dynamic options in roder to show the correct available options in the gui
    URL_ATLETI = "https://www.fpi.it/atleti.html"
    URL_QUALIFICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_qualifiche"
    URL_PESO = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_peso"
    URL_STATISTICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_totalizzatori"

    def __init__(self):
        self.session = self.__init_session()
        self.cache = {}

        """
        the html corresponding to URL_ATLETI has a form with post method composed of select-option tags,
        you have to create a dictionary to send as parameter to compile the form.
        However, there are form fields whose options are generated dynamically by javascript.
        To have access to the available info and their values you need to access the php that provides them.
        sending a payload to php this responds with a list of options based on the data received.
        For this you have to create an initial payload with form options that are constant,
        and update the payload to each request get to php of the field you want to compile. """
        self.payload = {
            'id_tipo_tessera': '5',  # Atleta dilettante IBA
            'sesso': 'M'
        }

    #initialize the session in order to get cookies and tokens if necessary
    def __init_session(self) -> req.Session:
        s = req.Session()
        try:
            s.verify = certifi.where()
            s.get(self.URL_ATLETI)
            print("connessione riuscita con verifica dei certificati")
        except:
            s.verify = False
            s.get(self.URL_ATLETI)
            print("Connessione riuscita senza verifica dei certificati")
        print("attendere l'apertura della finestra")
        return s

    #scraps available options and their relative int value from the HTML souce code
    def get_comitati(self) -> Dict[str, int]:
        if "comitati" in self.cache:
            return self.cache["comitati"]
        try:
            self.session.verify = certifi.where()
            response = self.session.get(self.URL_ATLETI)
        except:
            self.session.verify = False
            response = self.session.get(self.URL_ATLETI)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            select_element = soup.find("select", id="id_comitato_atleti")
            comitati = {option.text: option["value"] for option in select_element.find_all("option")}
            self.cache["comitati"] = comitati
            return comitati
        return {}

    def get_options(self, url: str) -> Dict[str, int]:
        if url in self.cache:
            return self.cache[url]
        try:
            self.session.verify = certifi.where()
            response = self.session.get(url, params=self.payload)
        except:
            self.session.verify = False
            response = self.session.get(url, params=self.payload)
        if response.status_code == 200:
            options_soup = BeautifulSoup(response.text, 'html.parser')
            options = {option.text: option["value"] for option in options_soup.find_all("option") if option['value']}
            self.cache[url] = options
            return options
        return {}

    def fetch_athletes(self, url: str) -> List[Any]:
        try:
            self.session.verify = certifi.where()
            response = self.session.post(url, params=self.payload)
        except:
            self.session.verify = False
            response = self.session.post(url, params=self.payload)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find_all('div', class_='atleta')
        return []

    def get_athlete_stats(self, matricola: str) -> Dict[str, int]:
        if matricola in self.cache:
            return self.cache[matricola]
        try:
            self.session.verify = certifi.where()
            response = self.session.get(self.URL_STATISTICHE, params={'matricola': matricola})
        except:
            self.session.verify = False
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
