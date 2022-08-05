import PySimpleGUI as sg

# sg.Window(title="Hello World", layout=[[]], margins=(100, 50)).read()

# First the window layout in 2 columns

left_column = [
    [sg.In(size=(25, 1), enable_events=True, key="-ARTIST-")],
    [sg.In(size=(25, 1), enable_events=True, key="-USERNAME-")],
    [sg.In(size=(25, 1), enable_events=True, key="-PASSWORD-")],
    [sg.HSeparator()],
    [sg.FolderBrowse()],
    [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")],
]

# For now will only show the name of the file that was chosen
right_column = [
    [sg.Text(size=(30, 5), justification='center',
             text="Gonna put lots of notes here,Gonna put lots of notes here,Gonna put lots of notes here,"
                  "Gonna put lots of notes here,Gonna put lots of notes here,Gonna put lots of notes here,"
                  "Gonna put lots of notes here,Gonna put lots of notes here,Gonna put lots of notes here,"
                  "Gonna put lots of notes here,Gonna put lots of notes here,Gonna put lots of notes here,"
                  "Gonna put lots of notes here,Gonna put lots of notes here,Gonna put lots of notes here,"
                  "Gonna put lots of notes here,Gonna put lots of notes here,Gonna put lots of notes here,")],
    [sg.HSeparator()],
    [sg.Text('Future options can go here')],
    [sg.HSeparator()],
    [sg.Button(button_text='Exit')]
]

# ----- Full layout -----
layout = [
    [
        sg.Column(left_column),
        sg.VSeperator(),
        sg.Column(right_column),
    ]
]

window = sg.Window("Ultimate Guitar Downloader", layout)

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

window.close()
