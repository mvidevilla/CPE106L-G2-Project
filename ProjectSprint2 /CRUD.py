import sqlite3
import os
from datetime import datetime
from tkinter import messagebox
import tkinter as tk

DB_FILE = "notes.db"
NOTES_DIR = "notes"

os.makedirs(NOTES_DIR, exist_ok=True)

def init_db():
    """Initializes the database by creating the notes table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            noteID INTEGER PRIMARY KEY AUTOINCREMENT,
            noteName TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            noteCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
            filePath TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_note(refresh_callback=None):
    """Opens a new window for entering note details and saves the note to the database."""
    new_window = tk.Toplevel()
    new_window.title("Create New Note")

    # Labels and Entry Fields
    tk.Label(new_window, text="Note Name:").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(new_window, text="Category:").grid(row=1, column=0, padx=5, pady=5)

    note_name_entry = tk.Entry(new_window)
    category_entry = tk.Entry(new_window)

    note_name_entry.grid(row=0, column=1, padx=5, pady=5)
    category_entry.grid(row=1, column=1, padx=5, pady=5)

    def save_note():
        note_name = note_name_entry.get().strip()
        category = category_entry.get().strip()

        if not note_name or not category:
            messagebox.showerror("Error", "Both fields must be filled!")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM notes WHERE noteName = ?", (note_name,))
        if cursor.fetchone():
            messagebox.showerror("Error", "A note with this name already exists. Choose a different name.")
            conn.close()
            return

        file_path = os.path.join(NOTES_DIR, f"{note_name}.txt")

        # Create the note file
        with open(file_path, "w") as file:
            file.write(f"Note: {note_name}\nCategory: {category}\nCreated: {datetime.now()}\n===================================\n")

        cursor.execute("INSERT INTO notes (noteName, category, filePath) VALUES (?, ?, ?)",
                       (note_name, category, file_path))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Note '{note_name}' created successfully!")
        new_window.destroy()

        # Wow! Refreshing!
        if refresh_callback:
            refresh_callback()

    # Save Button
    tk.Button(new_window, text="Save Note", command=save_note).grid(row=2, columnspan=2, pady=10)


def read_note():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    noteName = input("Enter the note name to read: ").strip()

    cursor.execute("SELECT filePath FROM notes WHERE noteName = ?", (noteName,))
    result = cursor.fetchone()

    if not result:
        print("Error: No note found with this name.")
        conn.close()
        return

    fPath = result[0]

    if not os.path.exists(fPath):
        print("Error: Note file is missing.")
        conn.close()
        return

    with open(fPath, "r") as file:
        print("\n" + "="*30)
        print(f"Contents of '{noteName}':\n")
        print(file.read())
        print("="*30 + "\n")

    conn.close()

def delete_note():
    """Deletes a note from the database and removes its file."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    noteName = input("Enter the note name to delete: ").strip()

    cursor.execute("SELECT filePath FROM notes WHERE noteName = ?", (noteName,))
    result = cursor.fetchone()

    if not result:
        print("Error: No note found with this name.")
        conn.close()
        return

    fPath = result[0]

    if os.path.exists(fPath):
        os.remove(fPath)
        print(f"Note file '{fPath}' deleted successfully.")
    else:
        print("Warning: Note file was missing, but the database entry will be removed.")

    cursor.execute("DELETE FROM notes WHERE noteName = ?", (noteName,))
    conn.commit()
    conn.close()

    print(f"Note '{noteName}' removed from database.")

def load_note(noteName):
    """Loads the content of a note from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT filePath FROM notes WHERE noteName = ?", (noteName,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        messagebox.showerror("Error", "Note not found in the database.")
        return None, None

    fPath = result[0]

    if not os.path.exists(fPath):
        messagebox.showerror("Error", "The note file is missing.")
        return None, None

    with open(fPath, "r") as file:
        return file.read(), fPath 

def save_note(fPath, content):
    """Saves the updated content back to the note file."""
    if not fPath:
        messagebox.showerror("Error", "No note selected.")
        return

    with open(fPath, "w") as file:
        file.write(content.strip())

    messagebox.showinfo("Success", "Note updated successfully.")

def fetch_notes():
    """Fetches all note names from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT noteName FROM notes")
    notes = cursor.fetchall()
    conn.close()
    return [note[0] for note in notes]
