import tkinter as tk 
import customtkinter as ctk  # Import CustomTkinter
from tkinter import messagebox  # Import messagebox for pop-up dialogs
import sqlite3
import os
from CRUD import init_db, create_note, load_note, delete_note
from sorting import get_sorted_notes
from group import get_grouped_notes

init_db()

# Set CustomTkinter theme and appearance
ctk.set_appearance_mode("light")  # Light mode
ctk.set_default_color_theme("green")  # Green theme

def load_notes():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT category FROM notes")
    categories = ["Group by"] + [row[0] for row in cursor.fetchall()]
    conn.close()

    # Updated the grouping OptionMenu with new categories
    grouping.configure(values=categories)

    category = groupVar.get()
    order_by = sortVar.get()
    if category != "Group by":
        notes = get_grouped_notes(category)
    else:
        notes = get_sorted_notes(order_by)
    
    notesList.delete(0, "end")
    for note in notes:
        # Format the note name and category with consistent spacing
        note_name = note[0].ljust(20)  # Left-justify the note name with a fixed width
        note_category = note[1].ljust(20)  # Left-justify the category with a fixed width
        notesList.insert("end", f"{note_name} : {note_category}")  # Use ":" as the separator

def save_changes(file_path):
    updated_content = tEditor.get("1.0", "end").strip()

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()
        metadata = lines[:3]

    else:
        metadata = ["Note: Unknown\n", "Category: Unknown\n", "Created: Unknown\n"]
    
    with open(file_path, "w") as file:
        file.writelines(metadata)
        file.write("\n" + updated_content + "\n")
    saveButton.configure(state="normal")
    discardButton.configure(state="normal")
    disableFuncs()

# Function to discard changes
def discard_changes():
    saveButton.configure(state="normal")
    discardButton.configure(state="normal")
    tEditor.delete("1.0", "end")
    disableFuncs()

def disableFuncs():
    tEditor.delete("1.0", "end")
    
    noteInfo.configure(state="normal")
    noteInfo.delete("1.0", "end")
    noteInfo.configure(state="disabled")

    saveButton.configure(state="disabled")
    deleteButton.configure(state="disabled")
    discardButton.configure(state="disabled")
    updateNoteDetails.configure(state="disabled")
    tEditor.configure(state="disabled")
    notesList.selection_clear(0, "end")

# Function to load the selected note into the editor
def loadEditorBox(*event):
    selected_index = notesList.curselection()
    if not selected_index:
        return

    selected_note = notesList.get(selected_index)
    note_name = selected_note.split(" : ")[0].strip()  # Used ":" as the separator

    content, file_path = load_note(note_name)
    if content is None:
        return
    
    lines = content.split("\n")

    noteInfo.configure(state="normal")
    noteInfo.delete("1.0", "end")
    noteInfo.insert("end", "\n".join(lines[:3]) + "\n")
    noteInfo.configure(state="disabled")

    tEditor.configure(state="normal")
    tEditor.delete("1.0", "end")
    tEditor.insert("end", "\n".join(lines[4:]))

    deleteButton.configure(state="normal")
    saveButton.configure(state="normal", command=lambda: save_changes(file_path))
    discardButton.configure(state="normal", command=discard_changes)
    updateNoteDetails.configure(state="normal", command=update_details)

def createButtonFunc():
    create_note()

def deleteTarget():
    index = notesList.curselection()
    if not index:
        messagebox.showerror("Error", "No note selected")
        return
    
    note = notesList.get(index)
    name = note.split(" : ")[0].strip()  # Used ":" as the separator

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?")
    if confirm:
        delete_note(name)
        load_notes()
        disableFuncs()

# Function to update note details
def update_details():
    findTarget = notesList.curselection()
    if not findTarget:
        messagebox.showerror("Error, No note Selected. Select a note to edit")
        return
    
    selectedNote = notesList.get(findTarget)
    oldName, oldCat = selectedNote.split(" : ")  # Use ":" as the separator
    oldName = oldName.strip()
    oldCat = oldCat.strip()

    updateWindow = ctk.CTkToplevel()
    updateWindow.minsize(230, 100)
    updateWindow.title("Update")

    ctk.CTkLabel(updateWindow, text="New Name:").grid(row=0, column=0, padx=5, pady=5, sticky="nw")
    ctk.CTkLabel(updateWindow, text="New Category").grid(row=1, column=0, padx=5, pady=5, sticky="nw")

    noteIn = ctk.CTkEntry(updateWindow)
    noteIn.grid(row=0, column=1, padx=5, pady=5)
    noteIn.insert(0, oldName)
    catIn = ctk.CTkEntry(updateWindow)
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
            messagebox("Error", "A note with this name already exists. Choose a different name")
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

    ctk.CTkButton(updateWindow, text="Save", command=save).grid(row=2, column=1, sticky="nw", padx=10)
    ctk.CTkButton(updateWindow, text="Discard", command=discard).grid(row=2, column=1, sticky="ne", padx=10)

root = ctk.CTk()
root.title("Notes Organization System")

root.minsize(560, 635)
frame = ctk.CTkFrame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

createButton = ctk.CTkButton(frame, text="Create Note", command=lambda: create_note(load_notes), fg_color="#4CAF50")  # Green
createButton.grid(row=0, column=0, padx=5, pady=5, sticky="w")

deleteButton = ctk.CTkButton(frame, text="Delete Note", command=deleteTarget, fg_color="#F44336", state="disabled")  # Red
deleteButton.grid(row=1, column=0, padx=5, pady=5, sticky="w")

ctk.CTkLabel(frame, text="Note Information:", font=("Helvetica", 14, "bold")).grid(row=0, column=1, sticky="nw", padx=5, pady=5)

# Note Information Textbox (First Box)
noteInfo = ctk.CTkTextbox(
    frame,
    width=400,
    height=100,
    font=("Helvetica", 12),
    fg_color="#ffffff",  # White background
    border_width=2,  # Add a border
    border_color="#4CAF50",  # Green border
)
noteInfo.grid(padx=5, sticky="sw", row=1, column=1, rowspan=2, columnspan=2)
noteInfo.configure(state="disabled")

# Added space between the Note Information box and the Text Editor box
ctk.CTkLabel(frame, text="", height=10).grid(row=2, column=1, sticky="nw")  # Add a spacer

# Text Editor (Second Box)
tEditor = ctk.CTkTextbox(
    frame,
    width=400,
    height=400,
    font=("Helvetica", 12),
    fg_color="#f0f0f0",  # Light gray background
    border_width=2,  # Add a border
    border_color="#F44336",  # Red border
)
tEditor.grid(padx=5, sticky="ne", row=3, column=1, rowspan=7, columnspan=2, pady=5)
tEditor.configure(state="disabled")

saveButton = ctk.CTkButton(frame, text="Save Changes", state="disabled", fg_color="#4CAF50")  # Green
saveButton.grid(sticky="se", row=8, column=2, padx=10)

discardButton = ctk.CTkButton(frame, text="Discard Changes", state="disabled", fg_color="#F44336")  # Red
discardButton.grid(sticky="sw", row=8, column=1, padx=3)

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

sortVar = ctk.StringVar(frame)
sortVar.set(sortOpt[0])

sorting = ctk.CTkOptionMenu(frame, variable=sortVar, values=sortOpt)
sorting.grid(row=2, column=0, sticky="w", padx=1, pady=5)

groupVar = ctk.StringVar(frame)
groupVar.set(groupOpt[0])

grouping = ctk.CTkOptionMenu(frame, variable=groupVar, values=groupOpt)
grouping.grid(row=3, column=0, sticky="w", padx=1, pady=5)

updateNoteDetails = ctk.CTkButton(frame, text="Update Note Details", command=update_details, state="disabled", fg_color="#9E9E9E")  # Gray
updateNoteDetails.grid(row=4, column=0, padx=5, pady=5, sticky="w")

# Search functionality
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
                    matching_notes.append(f"{note_name.ljust(20)} : {category.ljust(20)}")

    notesList.delete(0, "end")  # Clear the listbox
    if matching_notes:
        for note in matching_notes:
            notesList.insert("end", note)
    else:
        messagebox.showinfo("No Results", "No notes contain the searched term.")
        load_notes()

searchBox = ctk.CTkEntry(frame, width=200)
searchBox.grid(row=5, column=0, padx=5, pady=5, sticky="w")

findButton = ctk.CTkButton(frame, text="Find in Notes", command=lambda: find_in_notes(searchBox.get().strip()), fg_color="#9E9E9E")  # Gray
findButton.grid(row=6, column=0, padx=5, pady=5, sticky="w")

# Updated the header text to use ":" as the separator
header = ctk.CTkLabel(frame, text="Name                : Category")
header.grid(row=7, column=0, sticky="w", padx=5)

# Create a Listbox (using tk.Listbox)
notesList = tk.Listbox(frame, width=30, height=20, bg="#ffffff", fg="#333333", font=("Helvetica", 12))  # Larger font
notesList.grid(row=8, column=0, padx=5, pady=5, sticky="w")

# Bind double-click event to loadEditorBox
notesList.bind("<Double-Button-1>", loadEditorBox)

# Trace changes to sorting and grouping variables
sortVar.trace_add("write", lambda *args: load_notes())
groupVar.trace_add("write", lambda *args: load_notes())

# Load notes and start the application
load_notes()
loadEditorBox()
root.mainloop()