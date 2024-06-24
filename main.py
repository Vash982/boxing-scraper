import tkinter as tk
from gui import Application

if __name__ == "__main__":
    print("avvio in corso, attendere qualche secondo...")
    window = tk.Tk()
    app = Application(window)
    window.mainloop()
