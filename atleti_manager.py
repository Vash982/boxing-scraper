from typing import Any
import requests as req
from bs4 import BeautifulSoup, ResultSet

class AtletiManager:
    URL_ATLETI = "https://www.fpi.it/atleti.html"
    URL_STATISTICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_totalizzatori"
    MIN_MATCHES = 0
    MAX_MATCHES = 20
    
    def __init__(self, payload: dict[str, Any], session: req.Session):
        self.payload = payload
        self.session = session
    
    def get_filtered_athletes(self) -> list:
        athlete_divs = self.__fetch_athletes()
        athletes = [self.__parse_athlete_data(div) for div in athlete_divs]
        return self.__filter_athletes(athletes)

    def __fetch_athletes(self) -> (ResultSet[Any] | list):
        response = self.session.post(self.URL_ATLETI, params=self.payload)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find_all('div', class_='atleta')
        return []
    
    def __parse_athlete_data(self, athlete_div) -> dict[str, Any]:
        nome = athlete_div.find(class_='card-title').text
        età = int(athlete_div.find(class_='card-title').find_next_sibling(class_='card-title').text.split(':')[-1])
        società = athlete_div.find('h6', string='Società').find_next('p').text

        bottone = athlete_div.find('button', class_='btn btn-dark btn-sm record')
        matricola = bottone["data-id"]
        statistiche = self.__get_athlete_stats(matricola)

        return {
            "nome": nome,
            "età": età,
            "società": società,
            "statistiche": statistiche
        }
    
    def __get_athlete_stats(self, matricola) -> (dict[str, int] | dict):
        response = self.session.get(self.URL_STATISTICHE, params={'matricola': matricola})
        if response.status_code == 200:
            stats = BeautifulSoup(response.text, 'html.parser').find_all("td")
            return {
                "numero_match": int(stats[0].text),
                "vittorie": int(stats[1].text),
                "sconfitte": int(stats[2].text),
                "pareggi": int(stats[3].text),
            }
        return {}

    def __filter_athletes(self, athletes: list[dict[str, Any]]) -> list:
        return [
            atleta for atleta in athletes
            if self.MIN_MATCHES <= atleta["statistiche"]["numero_match"] <= self.MAX_MATCHES
        ]
