import requests as req
from bs4 import BeautifulSoup

class FormHelper:
    URL_QUALIFICHE = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_qualifiche"
    URL_PESO = "https://www.fpi.it/index.php?option=com_callrestapi&task=json_peso"
    
    payload = {
        'id_tipo_tessera': '5',  # Atleta dilettante IBA
        'sesso': 'M'
    }

    def __init__(self, session: req.Session):
        self.session = session

    def get_comitati(self) -> dict[str, int]:
        response = self.session.get("https://www.fpi.it/atleti.html")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            select_element = soup.find("select", id="id_comitato_atleti")
            return {option.text: option["value"] for option in select_element.find_all("option")}
        return {}
    
    def update_comitato(self, selected_comitato: str) -> None:
        self.payload["id_comitato_atleti"] = self.__set_value(selected_comitato, self.get_comitati())
    
    def get_qualifiche(self) -> dict[str, int]:
        return self.__get_options(self.URL_QUALIFICHE)
    
    def update_qualifica(self, selected_qualifica: str) -> None:
        self.payload["qualifica"] = self.__set_value(selected_qualifica, self.get_qualifiche())

    def get_pesi(self) -> dict[str, int]:
        return self.__get_options(self.URL_PESO)
    
    def update_pesi(self, selected_peso: str) -> None:
        self.payload["id_peso"] = self.__set_value(selected_peso, self.get_pesi())
    
    def __get_options(self, url: str) -> dict[str, int]:
        response = self.session.get(url, params=self.payload)
        if response.status_code == 200:
            options_soup = BeautifulSoup(response.text, 'html.parser')
            options = {option.text: option["value"] for option in options_soup.find_all("option") if option['value']}
            return options
        return {}

    def __set_value(self, value: str, all_values: dict) -> (int | str):
        try:
            return int(all_values.get(value, 0))
        except:
            return ""
