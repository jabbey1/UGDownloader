import requests
from tkinter import *

window = Tk()
textVar = StringVar()
label = Label(window, textvariable=textVar)
textVar.set("Enter artist name:")

textBox = Entry(window)
button = Button(window, text ='Download')
label.pack()
textBox.pack()
button.pack()
window.mainloop()

