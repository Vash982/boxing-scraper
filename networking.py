import requests as req
from bs4 import BeautifulSoup
from typing import Any, List, Dict
import certifi

class NetworkManager:
    URL_ATLETI = "https://www.fpi.it/atleti.html"
    URL_QUALIFICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_qualifiche"
    URL_PESO = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_peso"
    URL_STATISTICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_totalizzatori"

    def __init__(self):
        self.session = self.__init_session()
        self.cache = {}
        self.payload = {
            'id_tipo_tessera': '5',  # Atleta dilettante IBA
            'sesso': 'M'
        }

    def __init_session(self) -> req.Session:
        s = req.Session()
        s.verify = certifi.where()
        s.get(self.URL_ATLETI)
        print("Sessione inizializzata")
        return s

    def get_comitati(self) -> Dict[str, int]:
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

    def get_options(self, url: str) -> Dict[str, int]:
        if url in self.cache:
            return self.cache[url]
        response = self.session.get(url, params=self.payload)
        if response.status_code == 200:
            options_soup = BeautifulSoup(response.text, 'html.parser')
            options = {option.text: option["value"] for option in options_soup.find_all("option") if option['value']}
            self.cache[url] = options
            return options
        return {}

    def fetch_athletes(self, url: str) -> List[Any]:
        response = self.session.post(url, params=self.payload)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find_all('div', class_='atleta')
        return []

    def get_athlete_stats(self, matricola: str) -> Dict[str, int]:
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
