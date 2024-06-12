import tkinter as tk
from tkinter import ttk
from typing import Any
from threading import Thread
from session_manager import SessionManager
from atleti_manager import AtletiManager
from form_helper import FormHelper

class Application:
    MIN_MATCHES = 0
    MAX_MATCHES = 20
    
    def __init__(self, window: tk.Tk):
        window.title("RICERCA PUGILI")
        window.geometry("800x700")

        body = tk.Frame(window)
        body.pack(fill="both", expand=True)

        content = tk.Frame(body, width=700, height=600, padx=10, pady=10, bg="green")
        content.place(relx=0.5, rely=0.5, anchor="center")
        content.pack_propagate(False)

        defaults = tk.Frame(content)
        defaults.pack(fill="x")
        
        labels = [
            f"incontri minimi: {self.MIN_MATCHES}",
            f"incontri massimi: {self.MAX_MATCHES}",
            f"sesso: {FormHelper.payload['sesso']}",
            "tessera: dilettante IBA"
        ]

        for i, text in enumerate(labels):
            label = tk.Label(defaults, text=text, font=("sans serif", 12))
            label.grid(row=0, column=i, sticky="ew")
            defaults.columnconfigure(i, weight=1)

        submit_btn = tk.Button(content, text="cerca atleti", font=("sans serif", 12), padx=20, command=self.__search)
        submit_btn.pack(side="bottom")

        self.session = SessionManager.init_session()
        self.form_helper = FormHelper(self.session)

        self.comitati = self.addComitato(container=content)
        self.comitati.set(list(self.form_helper.get_comitati().keys())[0])
        self.comitati.pack(pady=10)
        self.comitati.bind("<<ComboboxSelected>>", lambda event: self.__updateComitato(event))

        self.qualifiche = self.addQualifica(container=content)
        self.qualifiche.pack(pady=10)
        self.qualifiche.bind("<<ComboboxSelected>>", lambda event: self.__updateQualifica(event, content))

        self.pesi_combobox = None

    def addComitato(self, container: tk.Frame) -> ttk.Combobox:
        comitati = list(self.form_helper.get_comitati().keys())
        return ttk.Combobox(container, values=comitati, state='readonly', width=30, font=("sans serif", 10))

    def __updateComitato(self, event: Any) -> None:
        selected_comitato = event.widget.get()
        self.form_helper.update_comitato(selected_comitato)
    
    def addQualifica(self, container: tk.Frame) -> ttk.Combobox:
        qualifiche = list(self.form_helper.get_qualifiche().keys())
        return ttk.Combobox(container, values=qualifiche, state='readonly', width=30, font=("sans serif", 10))
    
    def __updateQualifica(self, event: Any, container: tk.Frame) -> None:
        selected_qualifica = event.widget.get()
        self.form_helper.update_qualifica(selected_qualifica)

        if self.pesi_combobox is not None:
            self.pesi_combobox.pack_forget()
            self.pesi_combobox = None
            if self.form_helper.payload.get("id_peso"):
                self.form_helper.payload.pop("id_peso")
        
        if self.form_helper.payload["qualifica"] != 17:  # Schoolboy
            self.pesi_combobox = self.addPeso(container)
            self.pesi_combobox.pack(pady=10)
            self.pesi_combobox.bind("<<ComboboxSelected>>", lambda event: self.__updatePesi(event))

    def addPeso(self, container: tk.Frame) -> ttk.Combobox:
        pesi = list(self.form_helper.get_pesi().keys())
        return ttk.Combobox(container, values=pesi, state='readonly', width=30, font=("sans serif", 10))
    
    def __updatePesi(self, event) -> None:
        selected_peso = event.widget.get()
        self.form_helper.update_pesi(selected_peso)

    def __search(self) -> None:
        Thread(target=self.__fetchAndDisplayAthletes).start()
    
    def __fetchAndDisplayAthletes(self):
        athletes = AtletiManager(self.form_helper.payload, self.session).get_filtered_athletes()
        for athlete in athletes:
            print(athlete)

if __name__ == "__main__":
    window = tk.Tk()
    app = Application(window)
    window.mainloop()
