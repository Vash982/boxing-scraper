import tkinter as tk
from tkinter import ttk, messagebox
import re
from threading import Thread
from networking import NetworkManager
import data_processing
from data_processing import parse_athlete_data, filter_athletes, save_to_excel

FONT=("sans serif", 12)

class Application:
    DEFAULT_MIN_MATCHES = 0
    DEFAULT_MAX_MATCHES = 10

    def __init__(self, window: tk.Tk):
        #initialize an instance of network manager to connect the gui with http requests
        self.network_manager = NetworkManager()

        #initialize the result excel filename as empty
        self.file_name = ""

        window.title("RICERCA PUGILI")
        window.geometry("800x700")

        #main body the same size as the window
        body = tk.Frame(window)
        body.pack(fill="both", expand=True)

        #content occupied by the application
        content = tk.Frame(body, width=700, height=600, padx=10, pady=10, bg="green")
        content.place(relx=0.5, rely=0.5, anchor="center")
        content.pack_propagate(False)

        #container for default filters (such as: sesso_id, min_matches and max matches)
        defaults = tk.Frame(content)
        defaults.pack(fill="x")

        #input for min and max matches with 0 and 10 as default (row 9 and 10)
        tk.Label(defaults, text="Incontri minimi:", font=FONT).grid(row=0, column=0)
        self.min_matches_entry = tk.Entry(defaults, width=5, font=FONT, validate="key", validatecommand=(window.register(self.__validate_int), '%P'))
        self.min_matches_entry.grid(row=0, column=1, padx=(0, 10))
        self.min_matches_entry.insert(0, str(self.DEFAULT_MIN_MATCHES))

        tk.Label(defaults, text="Incontri massimi:", font=FONT).grid(row=0, column=2)
        self.max_matches_entry = tk.Entry(defaults, width=5, font=FONT, validate="key", validatecommand=(window.register(self.__validate_int), '%P'))
        self.max_matches_entry.grid(row=0, column=3, padx=(0, 10))
        self.max_matches_entry.insert(0, str(self.DEFAULT_MAX_MATCHES))

        #label for the first 2 filter, set as default
        tk.Label(defaults, text=f"sesso: {self.network_manager.payload['sesso']}", font=FONT).grid(row=0, column=4, sticky="ew", padx=(0, 15))
        tk.Label(defaults, text="tessera: dilettante IBA", font=FONT).grid(row=0, column=5, sticky="ew")

        #submit button to start the research on fpi.com and write the final excel file
        submit_btn = tk.Button(content, text="cerca atleti", font=FONT, padx=20, command=self.__validate_inputs)
        submit_btn.pack(side="bottom")

        #combobox for the first filter (italian regions)
        self.comitati = self.add_comitato(container=content)
        self.comitati.set(list(self.network_manager.get_comitati().keys())[0])
        self.comitati.pack(pady=10)
        self.comitati.bind("<<ComboboxSelected>>", lambda event: self.__update_comitato(event))

        #combobox for the second filter (athlete's age)
        self.qualifiche = self.add_qualifica(container=content)
        self.qualifiche.pack(pady=10)
        self.qualifiche.bind("<<ComboboxSelected>>", lambda event: self.__update_qualifica(event, content))

        #combobox for the third filter (athlete's wheight) set as none, available only if the second filter is set
        self.pesi_combobox = None

        #label and input for the final excel filename
        self.file_name_frame = tk.Frame(content)
        self.file_name_frame.pack(side="bottom", pady=10)
        tk.Label(self.file_name_frame, text="Nome file Excel:", font=FONT).pack(side="left")
        self.file_name_entry = tk.Entry(self.file_name_frame, width=20, font=FONT)
        self.file_name_entry.pack(side="left", padx=(0, 10))

    #checks if the value of the entry for min and max matches is a number
    def __validate_int(self, value: str) -> bool:
        return value.isdigit() or value == ""

    #checks if min and max matches are valid inputs
    def __validate_inputs(self) -> None:
        min_matches = self.min_matches_entry.get()
        max_matches = self.max_matches_entry.get()

        if not min_matches.isdigit():
            self.min_matches_entry.delete(0, tk.END)
            self.min_matches_entry.insert(0, str(self.DEFAULT_MIN_MATCHES))
            min_matches = str(self.DEFAULT_MIN_MATCHES)
        if not max_matches.isdigit():
            self.max_matches_entry.delete(0, tk.END)
            self.max_matches_entry.insert(0, str(self.DEFAULT_MAX_MATCHES))
            max_matches = str(self.DEFAULT_MAX_MATCHES)

        self.MIN_MATCHES = int(min_matches)
        self.MAX_MATCHES = int(max_matches)

        self.__validate_file_name()

    #checks if excel filename has a valid input
    def __validate_file_name(self) -> None:
        file_name = self.file_name_entry.get().strip()

        if not file_name:
            qualifica = self.qualifiche.get() if self.qualifiche else "NA"
            peso = self.pesi_combobox.get() if self.pesi_combobox else "NA"
            file_name = f"{qualifica}_{peso}"

        if not self.__is_valid_filename(file_name):
            messagebox.showerror("Errore", "Il nome del file contiene caratteri non validi.")
            return

        self.file_name = file_name
        self.__search()

    #checks if the filename contains invalid characters
    def __is_valid_filename(self, filename: str) -> bool:
        return bool(re.match(r'^[\w\-. ]+$', filename))

    #gets the int value of the selected option using the dict containing all the options, it will be used to update the payload
    def __set_value(self, value: str, all_values: dict) -> (int | str):
        try:
            return int(all_values.get(value, 0))
        except:
            return ""

    #gets available italian regions list and uses it to return the first filter combobox
    def add_comitato(self, container: tk.Frame) -> ttk.Combobox:
        comitati = list(self.network_manager.get_comitati().keys())
        return ttk.Combobox(container, values=comitati, state='readonly', width=30, font=FONT)

    #if the value of the first filter combobox is set or changed, the value of the relative key is updated in the payload
    def __update_comitato(self, event: any) -> None:
        selected_comitato = event.widget.get()
        self.network_manager.payload["id_comitato_atleti"] = self.__set_value(selected_comitato, self.network_manager.get_comitati())
        if selected_comitato == "comitato":
            self.network_manager.payload.pop("id_comitato_atleti")

    #gets available ages list and uses it to return the second filter combobox
    def add_qualifica(self, container: tk.Frame) -> ttk.Combobox:
        qualifiche = list(self.network_manager.get_options(self.network_manager.URL_QUALIFICHE).keys())
        return ttk.Combobox(container, values=qualifiche, state='readonly', width=30, font=FONT)

    #if the value of the second filter combobox is set or changed, the value of the relative key is updated in the payload
    #if the value is equal to Schoolboy, wheights combobox is not available. if it already exists, it gets deleted
    def __update_qualifica(self, event: any, container: tk.Frame) -> None:

        if self.network_manager.payload.get("qualifica") is not None:
            self.network_manager.payload.pop("qualifica")
        if self.network_manager.payload.get("id_qualifica") is not None:
            self.network_manager.payload.pop("id_qualifica")
        if self.network_manager.payload.get("id_peso") is not None:
            self.network_manager.payload.pop("id_peso")


        selected_qualifica = event.widget.get()
        self.network_manager.payload["qualifica"] = self.__set_value(selected_qualifica, self.network_manager.get_options(self.network_manager.URL_QUALIFICHE))

        if self.pesi_combobox is not None:
            self.pesi_combobox.pack_forget()
            self.pesi_combobox = None

        if self.network_manager.payload["qualifica"] != 17:  #Schoolboy
            self.pesi_combobox = self.add_peso(container)
            self.pesi_combobox.pack(pady=10)
            self.pesi_combobox.bind("<<ComboboxSelected>>", lambda event: self.__update_pesi(event))

    #gets available wheights list (based off the age set in the previous combobox) and uses it to return the third filter combobox
    def add_peso(self, container: tk.Frame) -> ttk.Combobox:
        pesi = list(self.network_manager.get_options(self.network_manager.URL_PESO).keys())
        return ttk.Combobox(container, values=pesi, state='readonly', width=30, font=("sans serif", 10))
    
    #if the value of the first filter combobox is set or changed, the value of the relative key is updated in the payload
    def __update_pesi(self, event: any) -> None:
        selected_peso = event.widget.get()
        self.network_manager.payload["id_peso"] = self.__set_value(selected_peso, self.network_manager.get_options(self.network_manager.URL_PESO))

    #modifies the payload in order to make the right request to the server
    def __search(self) -> None:
        qualifica = self.network_manager.payload.pop("qualifica", None)
        if qualifica is not None:
            self.network_manager.payload["id_qualifica"] = qualifica
    
            id_peso = self.network_manager.payload.get("id_peso")
            if id_peso is not None:
                if qualifica == 20 and id_peso == 114:
                    self.network_manager.payload["id_peso"] = 468
                elif qualifica == 97 and id_peso == 159:
                    self.network_manager.payload["id_peso"] = 429
    
        self.network_manager.payload["page"] = "1"
        Thread(target=self.__fetch_and_display_athletes).start()

    #gets the result pages, scraps and filter every athlete, and finally, writes the excel file
    def __fetch_and_display_athletes(self) -> None:
        filtered_athletes = []
        while True:
            athlete_divs = self.network_manager.fetch_athletes(self.network_manager.URL_ATLETI)
            if len(athlete_divs) != 0:
                athletes = [parse_athlete_data(div, self.network_manager) for div in athlete_divs]
                for atleta in filter_athletes(athletes, self.MIN_MATCHES, self.MAX_MATCHES):
                    filtered_athletes.append(atleta)
                page = int(self.network_manager.payload["page"]) + 1
                self.network_manager.payload["page"] = str(page)
            else:
                save_to_excel(filtered_athletes, self.file_name)
                self.network_manager.payload["page"] = "1"
                break
