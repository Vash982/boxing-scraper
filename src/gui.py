from networkManager import NetworkManager
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import dataManager
from threading import Thread
import re

DEFAULT_FONT = ("sans serif", 14)

#initialize an instance of network manager to connect the gui with http requests
net_manager = NetworkManager()

class Application:
    min_matches = 0
    max_matches = 10
    file_name = str()
    comitati = net_manager.getComitati()
    qualifiche = net_manager.getOptions(net_manager.URL_QUALIFICHE)
    pesi = dict[str, int]()

    def __init__(self, window: tk.Tk) -> None:
        window.title("RICERCA PUGILI")
        window.geometry("1200x900")

        #main body the same size as the window
        body = tk.Frame(window, bg="black")
        body.pack(fill="both", expand=True)

        #content occupied by the application
        content = tk.Frame(body, width=1000, height=800, padx=10, pady=10, bg="blue")
        content.place(relx=0.5, rely=0.5, anchor="center")
        content.pack_propagate(False)

        #container for default filters (such as: sesso_id, min_matches and max matches)
        defaults = tk.Frame(content, bg="light blue", padx=50)
        defaults.pack(fill="x")

        #input for min and max matches with 0 and 10 as default (row 9 and 10)
        min_matches_item = tk.Frame(defaults)
        min_matches_lab = tk.Label(min_matches_item, text="Incontri minimi:", font=DEFAULT_FONT, bg="light blue")
        self.min_matches_input = tk.Entry(min_matches_item, width=5, font=DEFAULT_FONT, validate="key", validatecommand=(window.register(self.__validateInt), '%P'))
        self.min_matches_input.insert(0, str(self.min_matches))
        min_matches_lab.pack(side="left")
        self.min_matches_input.pack(side="left")
        min_matches_item.pack(side="left")

        max_matches_item = tk.Frame(defaults)
        max_matches_lab = tk.Label(max_matches_item, text="Incontri massimi:", font=DEFAULT_FONT, bg="light blue")
        self.max_matches_input = tk.Entry(max_matches_item, width=5, font=DEFAULT_FONT, validate="key", validatecommand=(window.register(self.__validateInt), '%P'))
        self.max_matches_input.insert(0, str(self.max_matches))
        max_matches_lab.pack(side="left")
        self.max_matches_input.pack(side="left")
        max_matches_item.pack(side="right")

        #combobox for the first filter (italian regions)
        self.comitati_options = ttk.Combobox(content, values=list(self.comitati.keys()), state='readonly', width=30, font=DEFAULT_FONT)
        self.comitati_options.set(list(self.comitati.keys())[0])
        self.comitati_options.pack(pady=10)
        self.comitati_options.bind("<<ComboboxSelected>>", lambda event: self.__update_comitato(event))

        #combobox for the second filter (athlete's age)
        self.qualifiche_options = ttk.Combobox(content, values=list(self.qualifiche.keys()), state='readonly', width=30, font=DEFAULT_FONT)
        self.qualifiche_options.pack(pady=10)
        self.qualifiche_options.bind("<<ComboboxSelected>>", lambda event: self.__updateQualifica(event, content))

        #combobox for the third filter (athlete's wheight) set as none, available only if the second filter is set
        self.pesi_options = None

        #submit button to start the research on fpi.com and write the final excel file
        submit_btn = tk.Button(content, text="cerca atleti", font=DEFAULT_FONT, padx=20, command=self.__validate_inputs)
        submit_btn.pack(side="bottom")

        #label and input for the final excel filename
        self.file_name_frame = tk.Frame(content)
        self.file_name_frame.pack(side="bottom", pady=10)
        tk.Label(self.file_name_frame, text="Nome file Excel:", font=DEFAULT_FONT).pack(side="left")
        self.file_name_input = tk.Entry(self.file_name_frame, width=20, font=DEFAULT_FONT)
        self.file_name_input.pack(side="left", padx=(0, 10))


    #checks if the value of the entry for min and max matches is a number
    def __validateInt(self, value: str) -> bool:
        return value.isdigit() or value == ""
    
    #gets the int value of the selected option using the dict containing all the options, it will be used to update the payload
    def __set_value(self, value: str, all_values: dict) -> (int | str):
        try:
            return int(all_values.get(value, 0))
        except:
            return ""

    #if the value of the first filter combobox is set or changed, the value of the relative key is updated in the payload
    def __update_comitato(self, event: any) -> None:
        selected_comitato = event.widget.get()
        net_manager.payload["id_comitato_atleti"] = self.__set_value(selected_comitato, self.comitati)
        if selected_comitato == "comitato":
            net_manager.payload.pop("id_comitato_atleti")

    #if the value of the second filter combobox is set or changed, the value of the relative key is updated in the payload
    #if the value is equal to Schoolboy, wheights combobox is not available. if it already exists, it gets deleted
    def __updateQualifica(self, event: any, container: tk.Frame) -> None:
        net_manager.cleanQualifica()
        if self.pesi_options is not None:
            self.pesi_options.pack_forget()
            self.pesi_options = None
        selected_qualifica = event.widget.get()
        net_manager.payload["qualifica"] = self.__set_value(selected_qualifica, self.qualifiche)
        if net_manager.payload["qualifica"] != 17:  #Schoolboy
            self.pesi = net_manager.getOptions(net_manager.URL_PESO)
            self.pesi_options = ttk.Combobox(container, values=list(self.pesi.keys()), state='readonly', width=30, font=("sans serif", 10))
            self.pesi_options.pack(pady=10)
            self.pesi_options.bind("<<ComboboxSelected>>", lambda event: self.__update_pesi(event))
    
    #if the value of the first filter combobox is set or changed, the value of the relative key is updated in the payload
    def __update_pesi(self, event: any) -> None:
        selected_peso = event.widget.get()
        net_manager.payload["id_peso"] = self.__set_value(selected_peso, self.pesi)
        

    #checks if min and max matches are valid inputs
    def __validate_inputs(self) -> None:
        self.min_matches = self.min_matches_input.get()
        self.max_matches = self.max_matches_input.get()
        if not self.min_matches.isdigit():
            self.min_matches_input.delete(0, tk.END)
            self.min_matches_input.insert(0, str(0))
            self.min_matches = 0
        else:
            self.min_matches = int(self.min_matches)
        if not self.max_matches.isdigit():
            self.max_matches_input.delete(0, tk.END)
            self.max_matches_input.insert(0, str(10))
            self.max_matches = 10
        else:
            self.max_matches = int(self.max_matches)
        self.__validate_file_name()

    # Checks if excel filename has a valid input
    def __validate_file_name(self) -> None:
        file_name = self.file_name_input.get().strip()
        if file_name == "":
            qualifica = self.qualifiche_options.get() if self.qualifiche_options.get() != "" else "NA"
            peso = self.pesi_options.get() if self.pesi_options and self.pesi_options.get() != "" else "NA"
            file_name = f"{qualifica}_{peso}"
            file_name = file_name.replace(",", ".")
            file_name = file_name.replace("M", "")
        
        # Ensure the filename is valid before setting it
        file_name = re.sub(r'[^\w\-.]', '', file_name)
        
        if not self.__is_valid_filename(file_name):
            messagebox.showerror("Errore", "Il nome del file contiene caratteri non validi.")
            return
        
        self.file_name = file_name
        self.__search()

    # Checks if the filename contains invalid characters
    def __is_valid_filename(self, filename: str) -> bool:
        return bool(re.match(r'^[\w\-.]+$', filename))
    
    #modifies the payload in order to make the right request to the server
    def __search(self) -> None:
        qualifica = net_manager.payload.pop("qualifica", None)
        if qualifica is not None:
            net_manager.payload["id_qualifica"] = qualifica
            id_peso = net_manager.payload.get("id_peso")
            if id_peso is not None:
                if qualifica == 20 and id_peso == 114:
                    net_manager.payload["id_peso"] = 468
                elif qualifica == 97 and id_peso == 159:
                    net_manager.payload["id_peso"] = 429
        net_manager.payload["page"] = "1"
        Thread(target=self.__fetch_and_display_athletes).start()

    #gets the result pages, scraps and filter every athlete, and finally, writes the excel file
    def __fetch_and_display_athletes(self) -> None:
        filtered_athletes = []
        while True:
            athlete_divs = net_manager.fetch_athletes(net_manager.URL_ATLETI)
            if len(athlete_divs) != 0:
                athletes = [dataManager.parse_athlete_data(div, net_manager) for div in athlete_divs]
                for atleta in dataManager.filter_athletes(athletes, self.min_matches, self.max_matches):
                    filtered_athletes.append(atleta)
                page = int(net_manager.payload["page"]) + 1
                net_manager.payload["page"] = str(page)
            else:
                dataManager.save_to_excel(filtered_athletes, self.file_name)
                net_manager.payload.pop("page")
                net_manager.session = net_manager.initSession()
                break
