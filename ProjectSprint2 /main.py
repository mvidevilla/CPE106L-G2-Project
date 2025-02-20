import tkinter as tk
import sqlite3
from CRUD import init_db, create_note

init_db()

def load_notes():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT noteName, noteCreate, category FROM notes")
    notes = cursor.fetchall()
    notesList.delete(0, tk.END)

    for note in notes:
        note_entry = f"{note[0]} | {note[1]} | {note[2]}"
        notesList.insert(tk.END, note_entry)
    conn.close()


def loadEditorBox():
    from tkinter import scrolledtext
    tEditor = scrolledtext.ScrolledText(root, width=41, height=37)
    tEditor.grid(padx=5, pady=5, sticky=tk.E, row=0, column=1,rowspan=7)

root = tk.Tk()
root.title("Notes Organization System")

frame = tk.Frame(root)
frame.grid()
root.minsize(560,560)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)

createButton = tk.Button(frame, text="Create Note", command=create_note)
createButton.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
createButton.config(width=25)

deleteButton = tk.Button(frame, text="Delete Note")
deleteButton.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
deleteButton.config(width=25)

sortOpt = [
    "Sort by",
    "Name (Ascending)",
    "Name (Descending)",
    "Date Created (Ascending)",
    "Date Created (Descending)"
]

groupOpt = [
    "Group by"
]

sortVar = tk.StringVar(frame)
sortVar.set(sortOpt[0])

sorting = tk.OptionMenu(frame, sortVar, *sortOpt)
sorting.grid(row=2, column=0, sticky=tk.W, padx=1, pady=5)
sorting.config(width=24)

groupVar = tk.StringVar(frame)
groupVar.set(groupOpt[0])

grouping = tk.OptionMenu(frame, groupVar, *groupOpt)
grouping.grid(row=3, column=0, sticky=tk.W, padx=1, pady=5)
grouping.config(width=24) 

manageCategories = tk.Button(frame, text="Manage Categories")
manageCategories.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
manageCategories.config(width=25)

searchBox = tk.Text(frame, width=22,height=2)
searchBox.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
searchBox.config(yscrollcommand=scrollbar.set)
scrollbar.grid(column=0, row=5, sticky=tk.E)
scrollbar.config(command=searchBox.yview)

findButton = tk.Button(frame, text="Find in Notes")
findButton.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
findButton.config(width=25)

notesList = tk.Listbox(frame, width=30, height=20)
notesList.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

load_notes()
root.mainloop()
