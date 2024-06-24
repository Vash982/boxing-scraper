import tkinter as tk
from tkinter import ttk, messagebox
import re
from threading import Thread
from networking import NetworkManager
from data_processing import parse_athlete_data, filter_athletes, save_to_excel

class Application:
    DEFAULT_MIN_MATCHES = 0
    DEFAULT_MAX_MATCHES = 10

    def __init__(self, window: tk.Tk):
        self.network_manager = NetworkManager()
        self.file_name = ""

        window.title("RICERCA PUGILI")
        window.geometry("800x700")

        body = tk.Frame(window)
        body.pack(fill="both", expand=True)

        content = tk.Frame(body, width=700, height=600, padx=10, pady=10, bg="green")
        content.place(relx=0.5, rely=0.5, anchor="center")
        content.pack_propagate(False)

        defaults = tk.Frame(content)
        defaults.pack(fill="x")

        # Entry per incontri minimi
        tk.Label(defaults, text="Incontri minimi:", font=("sans serif", 12)).grid(row=0, column=0, sticky="e")
        self.min_matches_entry = tk.Entry(defaults, width=5, validate="key", font=("sans serif", 12))
        self.min_matches_entry.grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.min_matches_entry.insert(0, str(self.DEFAULT_MIN_MATCHES))
        self.min_matches_entry.config(validatecommand=(self.min_matches_entry.register(self.__validate_int), "%P"))

        # Entry per incontri massimi
        tk.Label(defaults, text="Incontri massimi:", font=("sans serif", 12)).grid(row=0, column=2, sticky="e")
        self.max_matches_entry = tk.Entry(defaults, width=5, validate="key", font=("sans serif", 12))
        self.max_matches_entry.grid(row=0, column=3, sticky="w", padx=(0, 10))
        self.max_matches_entry.insert(0, str(self.DEFAULT_MAX_MATCHES))
        self.max_matches_entry.config(validatecommand=(self.max_matches_entry.register(self.__validate_int), "%P"))

        tk.Label(defaults, text=f"sesso: {self.network_manager.payload['sesso']}", font=("sans serif", 12)).grid(row=0, column=4, sticky="ew")
        tk.Label(defaults, text="tessera: dilettante IBA", font=("sans serif", 12)).grid(row=0, column=5, sticky="ew")

        submit_btn = tk.Button(content, text="cerca atleti", font=("sans serif", 12), padx=20, command=self.__validate_inputs)
        submit_btn.pack(side="bottom")

        self.comitati = self.add_comitato(container=content)
        self.comitati.set(list(self.network_manager.get_comitati().keys())[0])
        self.comitati.pack(pady=10)
        self.comitati.bind("<<ComboboxSelected>>", lambda event: self.__update_comitato(event))

        self.qualifiche = self.add_qualifica(container=content)
        self.qualifiche.pack(pady=10)
        self.qualifiche.bind("<<ComboboxSelected>>", lambda event: self.__update_qualifica(event, content))

        self.pesi_combobox = None

        self.file_name_frame = tk.Frame(content)
        self.file_name_frame.pack(side="bottom", pady=10)
        tk.Label(self.file_name_frame, text="Nome file Excel:", font=("sans serif", 12)).pack(side="left")
        self.file_name_entry = tk.Entry(self.file_name_frame, width=20, font=("sans serif", 12))
        self.file_name_entry.pack(side="left", padx=(0, 10))

    def __validate_int(self, value: str) -> bool:
        return value.isdigit()

    def __validate_inputs(self) -> None:
        min_matches = self.min_matches_entry.get()
        max_matches = self.max_matches_entry.get()

        if not min_matches.isdigit():
            min_matches = str(self.DEFAULT_MIN_MATCHES)
        if not max_matches.isdigit():
            max_matches = str(self.DEFAULT_MAX_MATCHES)

        self.MIN_MATCHES = int(min_matches)
        self.MAX_MATCHES = int(max_matches)

        self.__validate_file_name()

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

    def __is_valid_filename(self, filename: str) -> bool:
        return bool(re.match(r'^[\w\-. ]+$', filename))

    def __set_value(self, value: str, all_values: dict) -> (int | str):
        try:
            return int(all_values.get(value, 0))
        except:
            return ""

    def add_comitato(self, container: tk.Frame) -> ttk.Combobox:
        comitati = list(self.network_manager.get_comitati().keys())
        return ttk.Combobox(container, values=comitati, state='readonly', width=30, font=("sans serif", 10))

    def __update_comitato(self, event: any) -> None:
        selected_comitato = event.widget.get()
        self.network_manager.payload["id_comitato_atleti"] = self.__set_value(selected_comitato, self.network_manager.get_comitati())

    def add_qualifica(self, container: tk.Frame) -> ttk.Combobox:
        qualifiche = list(self.network_manager.get_options(self.network_manager.URL_QUALIFICHE).keys())
        return ttk.Combobox(container, values=qualifiche, state='readonly', width=30, font=("sans serif", 10))

    def __update_qualifica(self, event: any, container: tk.Frame) -> None:
        selected_qualifica = event.widget.get()
        self.network_manager.payload["qualifica"] = self.__set_value(selected_qualifica, self.network_manager.get_options(self.network_manager.URL_QUALIFICHE))

        if self.pesi_combobox is not None:
            self.pesi_combobox.pack_forget()
            self.pesi_combobox = None
            if self.network_manager.payload.get("id_peso"):
                self.network_manager.payload.pop("id_peso")

        if self.network_manager.payload["qualifica"] != 17:  # Schoolboy
            self.pesi_combobox = self.add_peso(container)
            self.pesi_combobox.pack(pady=10)
            self.pesi_combobox.bind("<<ComboboxSelected>>", lambda event: self.__update_pesi(event))

    def add_peso(self, container: tk.Frame) -> ttk.Combobox:
        pesi = list(self.network_manager.get_options(self.network_manager.URL_PESO).keys())
        return ttk.Combobox(container, values=pesi, state='readonly', width=30, font=("sans serif", 10))
    
    def __update_pesi(self, event) -> None:
        selected_peso = event.widget.get()
        self.network_manager.payload["id_peso"] = self.__set_value(selected_peso, self.network_manager.get_options(self.network_manager.URL_PESO))

    def __search(self) -> None:
        self.network_manager.payload["id_qualifica"] = self.network_manager.payload.get("qualifica")

        if self.network_manager.payload['id_qualifica'] == 20:
            match self.network_manager.payload["id_peso"]:
                case 114:
                    self.network_manager.payload["id_peso"] = 468

        if self.network_manager.payload["id_qualifica"] == 97:
            match self.network_manager.payload["id_peso"]:
                case 159:
                    self.network_manager.payload["id_peso"] = 429

        Thread(target=self.__fetch_and_display_athletes).start()

    def __fetch_and_display_athletes(self):
        athlete_divs = self.network_manager.fetch_athletes(self.network_manager.URL_ATLETI)
        athletes = [parse_athlete_data(div, self.network_manager) for div in athlete_divs]
        filtered_athletes = filter_athletes(athletes, self.MIN_MATCHES, self.MAX_MATCHES)
        save_to_excel(filtered_athletes, self.file_name)

if __name__ == "__main__":
    print("avvio in corso, attendere qualche secondo...")
    window = tk.Tk()
    app = Application(window)
    window.mainloop()
