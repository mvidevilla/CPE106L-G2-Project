import tkinter as tk
import sqlite3
import os
from tkinter import scrolledtext, messagebox
from CRUD import init_db, create_note, load_note, delete_note
from sorting import get_sorted_notes
from group import get_grouped_notes

init_db()

def load_notes():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT category FROM notes")
    categories = ["Group by"] + [row[0] for row in cursor.fetchall()]
    conn.close()

    menu = grouping["menu"]
    menu.delete(0, tk.END)
    for category in categories:
        menu.add_command(label=category, command=lambda value=category: groupVar.set(value))

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

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()
        metadata = lines[:3]

    else:
        metadata = ["Note: Unknown\n", "Category: Unknown\n", "Created: Unknown\n"]
    
    with open(file_path, "w") as file:
        file.writelines(metadata)
        file.write("\n" + updated_content + "\n")
    saveButton.config(state=tk.ACTIVE)
    discardButton.config(state=tk.ACTIVE)
    disableFuncs()

def discard_changes():
    saveButton.config(state=tk.ACTIVE)
    discardButton.config(state=tk.ACTIVE)
    tEditor.delete(1.0, tk.END)
    disableFuncs()

def disableFuncs():
    tEditor.delete(1.0, tk.END)
    
    noteInfo.config(state=tk.NORMAL)
    noteInfo.delete(1.0, tk.END)
    noteInfo.config(state=tk.DISABLED)

    saveButton.config(state=tk.DISABLED)
    deleteButton.config(state=tk.DISABLED)
    discardButton.config(state=tk.DISABLED)
    updateNoteDetails.config(state=tk.DISABLED)
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
    
    lines = content.split("\n")

    noteInfo.config(state=tk.NORMAL)
    noteInfo.delete(1.0, tk.END)
    noteInfo.insert(tk.END, "\n".join(lines[:3]) + "\n")
    noteInfo.config(state=tk.DISABLED)

    tEditor.config(state=tk.NORMAL)
    tEditor.delete(1.0, tk.END)
    tEditor.insert(tk.END, "\n".join(lines[4:]))

    deleteButton.config(state=tk.NORMAL)
    saveButton.config(state=tk.NORMAL, command=lambda: save_changes(file_path))
    discardButton.config(state=tk.NORMAL, command=discard_changes)
    updateNoteDetails.config(state=tk.NORMAL, command=update_details)

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
        disableFuncs()

def update_details():
    findTarget = notesList.curselection()
    if not findTarget:
        messagebox.showerror("Error, No note Selected. Select a note to edit")
        return
    
    selectedNote = notesList.get(findTarget)
    oldName, oldCat = selectedNote.split(" | ")

    updateWindow = tk.Toplevel()
    updateWindow.minsize(230, 100)
    updateWindow.title("Update")

    tk.Label(updateWindow, text="New Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
    tk.Label(updateWindow, text="New Category").grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)

    noteIn = tk.Entry(updateWindow)
    noteIn.grid(row=0, column=1, padx=5, pady=5)
    noteIn.insert(0, oldName)
    catIn = tk.Entry(updateWindow)
    catIn.grid(row=1, column=1, padx=5, pady=5)
    catIn.insert(0, oldCat)

    def save():
        newName = noteIn.get().strip()
        newCat = catIn.get().strip()

        if not newName or not newCat:
            messagebox.showerror("Error", "Both fields must be filled")
            return
        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM notes WHERE noteName = ?", (newName,))
        if cursor.fetchone() and newName != oldName:
            messagebox("Error", "A note with this name already exists. Choose a different dame")
            conn.close()
            return
        
        cursor.execute("SELECT filePath from notes WHERE noteName = ?", (oldName,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Note not in database")
            conn.close()
            return
        
        old_path = result[0]
        new_path = old_path.replace(oldName, newName)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        with open(new_path, "r+") as file:
            lines = file.readlines()
            if len(lines)>=2:
                lines[0] = f"Note: {newName}\n"
                lines[1] = f"Note: {newCat}\n"
            file.seek(0)
            file.writelines(lines)
            file.truncate()

        cursor.execute("""
            UPDATE notes 
            SET noteName = ?, category = ?, filePath = ? 
            WHERE noteName = ?
        """, (newName, newCat, new_path, oldName))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Note {oldName} updated to {newName}.")
        updateWindow.destroy()
        disableFuncs()
        load_notes()

    def discard():
        updateWindow.destroy()
        load_notes()

    tk.Button(updateWindow, text="Save", command=save).grid(row=2, column=1, sticky=tk.NW, padx=10)
    tk.Button(updateWindow, text="Discard", command=discard).grid(row=2, column=1, sticky=tk.NE, padx=10)

root = tk.Tk()
root.title("Notes Organization System")

frame = tk.Frame(root)
frame.grid()
root.minsize(560,635)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)

createButton = tk.Button(frame, text="Create Note", command=lambda: create_note(load_notes))
createButton.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
createButton.config(width=25)

deleteButton = tk.Button(frame, text="Delete Note", command=deleteTarget, state=tk.DISABLED)
deleteButton.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
deleteButton.config(width=25)

tk.Label(frame, text="Note Information:").grid(row=0, column=1, sticky=tk.NW)
noteInfo = tk.Text(frame, width=41, height=3)
noteInfo.grid(padx=5,sticky=tk.SW, row=0, column=1, rowspan=2, columnspan=2)
noteInfo.config(state=tk.DISABLED)

tEditor = scrolledtext.ScrolledText(frame, width=41, height=32)
tEditor.grid(padx=5, sticky=tk.NE, row=2, column=1, rowspan=7, columnspan=2, pady=5)
tEditor.config(state=tk.DISABLED)

saveButton = tk.Button(frame, text="Save Changes", state=tk.DISABLED)
saveButton.grid(sticky=tk.SE, row=8, column=2, padx=10)

discardButton = tk.Button(frame, text="Discard Changes", state=tk.DISABLED)
discardButton.grid(sticky=tk.SW, row=8, column=1, padx=3)

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

updateNoteDetails = tk.Button(frame, text="Update Note Details", command=update_details, state=tk.DISABLED)
updateNoteDetails.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
updateNoteDetails.config(width=25)

def find_in_notes(search_term):
    """Searches for notes that contain the given term, ignoring the first 4 lines."""
    if not search_term:
        messagebox.showerror("Error", "Please enter a search term.")
        load_notes()
        return

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT noteName, category, filePath FROM notes")
    notes = cursor.fetchall()
    conn.close()

    matching_notes = []

    for note_name, category, file_path in notes:
        if os.path.exists(file_path):  # Check if the file exists
            with open(file_path, "r") as file:
                lines = file.readlines()  # Read all lines
                
                # Ignore the first 4 lines
                content = "".join(lines[4:]) if len(lines) > 4 else ""

                if search_term.lower() in content.lower():
                    matching_notes.append(f"{note_name} | {category}")

    notesList.delete(0, tk.END)  # Clear the listbox
    if matching_notes:
        for note in matching_notes:
            notesList.insert(tk.END, note)
    else:
        messagebox.showinfo("No Results", "No notes contain the searched term.")
        load_notes()

searchBox = tk.Text(frame, width=22,height=2)
searchBox.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
searchBox.config(yscrollcommand=scrollbar.set)
scrollbar.grid(column=0, row=5, sticky=tk.E)
scrollbar.config(command=searchBox.yview)

findButton = tk.Button(frame, text="Find in Notes", command=lambda: find_in_notes(searchBox.get("1.0", tk.END).strip()))
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
