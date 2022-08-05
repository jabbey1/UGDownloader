import PySimpleGUI as sg

# sg.Window(title="Hello World", layout=[[]], margins=(100, 50)).read()

# layout = [[sg.Text("Hello from PySimpleGUI")], [sg.Button("OK")]]
#
# # Create the window
# window = sg.Window("Demo", layout, margins=(300, 300))
#
# # Create an event loop
# while True:
#     event, values = window.read()
#     # End program if user closes window or
#     # presses the OK button
#     if event == "OK" or event == sg.WIN_CLOSED:
#         break
#
# window.close()


# First the window layout in 2 columns

left_column = [
    [sg.In(size=(25, 1), enable_events=True, key="-ARTIST-")],
    [sg.In(size=(25, 1), enable_events=True, key="-USERNAME-")],
    [sg.In(size=(25, 1), enable_events=True, key="-PASSWORD-")],
    [sg.HSeparator()],
    [sg.FolderBrowse(), sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")],
]

# For now will only show the name of the file that was chosen
right_column = [
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
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
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
