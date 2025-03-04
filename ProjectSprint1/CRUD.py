import sqlite3
import os
from datetime import datetime
from tkinter import messagebox

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

def create_note():
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

    noteName = input("Enter note name: ").strip()

    cursor.execute("SELECT 1 FROM notes WHERE noteName = ?", (noteName,))
    if cursor.fetchone():
        print("Error: A note with this name already exists. Please choose a different name.")
        conn.close()
        return

    categ = input("Enter note category: ").strip()

    fpath = os.path.join(NOTES_DIR, f"{noteName}.txt")

    with open(fpath, "w") as file:
        file.write(f"Note: {noteName}\nCategory: {categ}\nCreated: {datetime.now()}\n===================================\n")

    cursor.execute("INSERT INTO notes (noteName, category, filePath) VALUES (?, ?, ?)",
                   (noteName, categ, fpath))
    
    conn.commit()
    conn.close()
    
    print(f"Note '{noteName}' created successfully and saved at '{fpath}'.")

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