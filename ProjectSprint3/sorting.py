import sqlite3

DB_FILE = "notes.db"

def get_sorted_notes(order_by):
    """Fetches notes sorted based on the selected order."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if order_by == "Name (Ascending)":
        cursor.execute("SELECT noteName, category FROM notes ORDER BY noteName ASC")
    elif order_by == "Name (Descending)":
        cursor.execute("SELECT noteName, category FROM notes ORDER BY noteName DESC")
    elif order_by == "Date Created (Ascending)":
        cursor.execute("SELECT noteName, category FROM notes ORDER BY noteCreate ASC")
    elif order_by == "Date Created (Descending)":
        cursor.execute("SELECT noteName, category FROM notes ORDER BY noteCreate DESC")
    else:
        cursor.execute("SELECT noteName, category FROM notes")

    notes = cursor.fetchall()
    conn.close()
    return notes
