import tkinter as tk
import sqlite3
import os
from tkinter import scrolledtext, messagebox
from CRUD import init_db, create_note, save_note, load_note, delete_note
from sorting import get_sorted_notes
from group import get_grouped_notes

init_db()

def load_notes():
    category = groupVar.get()
    order_by = sortVar.get()

    if category != "Group by":
        notes = get_grouped_notes(category)
    else:
        notes = get_sorted_notes(order_by)
    
    notesList.delete(0, tk.END)
    for note in notes:
        notesList.insert(tk.END, f"{note[0]} | {note[1]}")

def save_changes(file_path):
    updated_content = tEditor.get(1.0, tk.END).strip()
    saveButton.config(state=tk.ACTIVE)
    discardButton.config(state=tk.ACTIVE)
    save_note(file_path, updated_content)
    tEditor.delete(1.0, tk.END)
    disableFuncs()

def discard_changes():
    saveButton.config(state=tk.ACTIVE)
    discardButton.config(state=tk.ACTIVE)
    tEditor.delete(1.0, tk.END)
    disableFuncs()

def disableFuncs():
    saveButton.config(state=tk.DISABLED)
    discardButton.config(state=tk.DISABLED)
    tEditor.config(state=tk.DISABLED)
    notesList.selection_clear(0, tk.END)

def loadEditorBox(*event):
    selected_index = notesList.curselection()
    if not selected_index:
        return

    selected_note = notesList.get(selected_index)
    note_name = selected_note.split(" | ")[0]

    content, file_path = load_note(note_name)
    if content is None:
        return
    tEditor.config(state=tk.NORMAL)
    tEditor.delete(1.0, tk.END)
    tEditor.insert(tk.END, content)

    saveButton.config(state=tk.NORMAL, command=lambda: save_changes(file_path))
    discardButton.config(state=tk.NORMAL, command=discard_changes)


def createButtonFunc():
    create_note()

def deleteTarget():
    index = notesList.curselection()
    if not index:
        messagebox.showerror("Error", "No note selected")
        return
    
    note = notesList.get(index)
    name = note.split(" | ")[0]

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?")
    if confirm:
        delete_note(name)
        load_notes()

def update_details(refresh_callback=None):
    new_window = tk.Toplevel()

    selected_index = notesList.curselection()
    if not selected_index:
        return
    else:
        selected_note = notesList.get(selected_index)
        note_name, note_cat = selected_note.split(" | ")

        new_window.title("Update ")

        tk.Label(new_window, text="Note Name:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(new_window, text="Category:").grid(row=1, column=0, padx=5, pady=5)

        note_name_entry = tk.Entry(new_window)
        category_entry = tk.Entry(new_window)
        note_name_entry.config(textvariable='f{note_name}')
        category_entry.config(textvariable='f{note_cat}')

        note_name_entry.grid(row=0, column=1, padx=5, pady=5)
        category_entry.grid(row=1, column=1, padx=5, pady=5)

        def save_note():
            note_name = note_name_entry.get().strip()
            category = category_entry.get().strip()

            if not note_name or not category:
                messagebox.showerror("Error", "Both fields must be filled!")
                return

            conn = sqlite3.connect("notes.db")
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM notes WHERE noteName = ?", (note_name,))
            if cursor.fetchone():
                messagebox.showerror("Error", "A note with this name already exists. Choose a different name.")
                conn.close()
                return

            file_path = os.path.join("motes.db", f"{note_name}.txt")

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Note '{note_name}' updated successfully!")
            new_window.destroy()

            if refresh_callback:
                refresh_callback()

        tk.Button(new_window, text="Save Changes", command=save_note).grid(row=2, columnspan=2, pady=10)

root = tk.Tk()
root.title("Notes Organization System")

frame = tk.Frame(root)
frame.grid()
root.minsize(560,635)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)

createButton = tk.Button(frame, text="Create Note", command=lambda: create_note(load_notes))
createButton.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
createButton.config(width=25)

deleteButton = tk.Button(frame, text="Delete Note", command=deleteTarget)
deleteButton.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
deleteButton.config(width=25)

tEditor = scrolledtext.ScrolledText(root, width=41, height=37)
tEditor.grid(padx=5, sticky=tk.NE, row=0, column=1, rowspan=7, columnspan=2)
tEditor.config(state=tk.DISABLED)

saveButton = tk.Button(root, text="Save Changes", state=tk.DISABLED)
saveButton.grid(sticky=tk.SE, row=0, column=2)

discardButton = tk.Button(root, text="Discard Changes", state=tk.DISABLED)
discardButton.grid(sticky=tk.SW, row=0, column=1)

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

updateNoteDetails = tk.Button(frame, text="Update Note Details", command=update_details)
updateNoteDetails.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
updateNoteDetails.config(width=25)

searchBox = tk.Text(frame, width=22,height=2)
searchBox.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
searchBox.config(yscrollcommand=scrollbar.set)
scrollbar.grid(column=0, row=5, sticky=tk.E)
scrollbar.config(command=searchBox.yview)

findButton = tk.Button(frame, text="Find in Notes")
findButton.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
findButton.config(width=25)

header = tk.Label(frame, text="Name          |          Category")
header.grid(row=7,column=0,sticky=tk.W, padx=5)

notesList = tk.Listbox(frame, width=30, height=20)
notesList.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
notesList.bind("<Double-Button-1>", loadEditorBox)

sortVar.trace_add("write", lambda *args: load_notes())
groupVar.trace_add("write", lambda *args: load_notes())

load_notes()
loadEditorBox()
root.mainloop()
