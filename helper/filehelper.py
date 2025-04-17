"""
File-related helper functions.
"""
import tkinter as tk
import tkinter.filedialog as file
from os import listdir, path

def _explorer_prompt(f):
    def wrapper():
        window = tk.Tk()
        window.withdraw()

        filename = f()
        window.destroy()

        return filename
    return wrapper

@_explorer_prompt
def file_chooser(): return file.askopenfilename()

@_explorer_prompt
def folder_chooser(): return file.askdirectory()

def first_file(folder):
    l = listdir(folder)
    for f in l:
        if path.isfile(path.join(folder, f)): return f