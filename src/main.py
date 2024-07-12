import tkinter as tk
from gui import Application #imports the main app

#TODO: -prendere tutte le pagine disponibili ad ogni ricerca
#TODO: -dopo aver selezionato dei filtri il payload viene costruito,
#       per questo quando si cambia la qualifica è possibile che facendo richieste con un payload già costruito si sputtani tutto<
#       quando si cambia la qualifica bisogna azzerare completamente tutti i filtri messi in input prima di proseguire.
#       solo dopo è sicuro continuare con l'aggiornamento del payload

if __name__ == "__main__":
    print("avvio in corso, attendere qualche secondo...")
    window = tk.Tk()
    app = Application(window)
    window.mainloop()
