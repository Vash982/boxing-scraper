import tkinter as tk
from gui import Application #imports the main app

#TODO: -prendere tutte le pagine disponibili ad ogni ricerca

if __name__ == "__main__":
    print("avvio in corso, attendere qualche secondo...")
    window = tk.Tk()
    app = Application(window)
    window.mainloop()
