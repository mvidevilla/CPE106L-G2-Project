import sqlite3

DB_FILE = "notes.db"

def get_grouped_notes(category):
    """Fetches notes that belong to the selected category."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if category == "Group by":
        cursor.execute("SELECT noteName, category FROM notes")
    else:
        cursor.execute("SELECT noteName, category FROM notes WHERE category = ?", (category,))

    notes = cursor.fetchall()
    conn.close()
    return notes
