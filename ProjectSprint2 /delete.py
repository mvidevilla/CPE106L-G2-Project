import sqlite3
import os
from tkinter import messagebox

DB_FILE = "notes.db"

def delete_note(note_name):
    """Deletes a note from the database and removes its file."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT filePath FROM notes WHERE noteName = ?", (note_name,))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("Error", "Note not found.")
        conn.close()
        return

    file_path = result[0]
    if os.path.exists(file_path):
        os.remove(file_path)

    cursor.execute("DELETE FROM notes WHERE noteName = ?", (note_name,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Note '{note_name}' deleted.")
