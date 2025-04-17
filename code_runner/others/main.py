import tkinter as tk
import tkinter.messagebox as messagebox

window = tk.Tk()
messagebox.showinfo("hello", "this is my tkinter app")

tk.Label(window, text="yay!").pack()
window.mainloop()