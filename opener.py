#!/bin/python3

# Tom Trebisky  9-29-2021
# Just an experiment to see if I can make a simple file
# open dialog -- and I can!
# Best of all, it works perfectly without any fiddling
# on windows, which is exactly what we hope for with Python.

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

print ( file_path )
