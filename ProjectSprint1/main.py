import tkinter as tk
from tkinter import scrolledtext
from CRUD import load_note, save_note, fetch_notes, init_db

init_db()

def load_selected_note():
    """Loads the selected note into the text editor."""
    noteName = nBox.get(tk.ACTIVE)

    if not noteName:
        return

    cont, fPath = load_note(noteName)

    if cont is not None:
        tEditor.delete("1.0", tk.END)
        tEditor.insert(tk.END, cont)
        tEditor.fPath = fPath
        saveButton.config(state=tk.NORMAL)

def save_changes():
    fPath = getattr(tEditor, "fPath", None)
    if fPath:
        cont = tEditor.get("1.0", tk.END)
        save_note(fPath, cont)

def refresh_notes():
    nBox.delete(0, tk.END)
    for note in fetch_notes():
        nBox.insert(tk.END, note)

root = tk.Tk()
root.title("Note Editor")

frame = tk.Frame(root)
frame.pack(pady=10)

nBox = tk.Listbox(frame, width=40, height=10)
nBox.pack(side=tk.LEFT, padx=10)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

nBox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=nBox.yview)

loadButton = tk.Button(root, text="Load Note", command=load_selected_note)
loadButton.pack(pady=5)

tEditor = scrolledtext.ScrolledText(root, width=60, height=20)
tEditor.pack(pady=10)

saveButton = tk.Button(root, text="Save Changes", command=save_changes, state=tk.DISABLED)
saveButton.pack(pady=5)

refresh_notes()

root.mainloop()