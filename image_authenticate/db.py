"""
db.py — SQLite database layer for face authentication.

Manages the 'residents' table which stores each person's name
and their averaged ArcFace embedding (512-dim float32 vector).

Usage:
    from db import init_db, insert_resident, get_all_residents
    init_db()
    insert_resident("john", embedding_array)
    residents = get_all_residents()  # [(name, np.ndarray), ...]
"""

import sqlite3
import numpy as np
import os

# Database file lives next to the scripts
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_auth.db")


def _connect():
    """Create and return a new database connection."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the residents table if it doesn't exist."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"[db] Database initialized at {DB_PATH}")


def insert_resident(name, embedding):
    """
    Store a resident's name and face embedding.

    Args:
        name: Person's name (string)
        embedding: 512-dim numpy float32 array
    """
    conn = _connect()
    cursor = conn.cursor()
    blob = embedding.astype(np.float32).tobytes()
    cursor.execute("INSERT INTO residents (name, embedding) VALUES (?, ?)", (name, blob))
    conn.commit()
    conn.close()
    print(f"[db] Stored embedding for '{name}'")


def get_all_residents():
    """
    Load all residents from the database.

    Returns:
        List of (name, embedding) tuples where embedding is a numpy float32 array.
    """
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name, embedding FROM residents")
    rows = cursor.fetchall()
    conn.close()

    residents = []
    for name, blob in rows:
        embedding = np.frombuffer(blob, dtype=np.float32)
        residents.append((name, embedding))

    return residents


def delete_resident(name):
    """
    Delete a specific resident by name.

    Args:
        name: Person's name to remove
    """
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents WHERE name = ?", (name,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted > 0:
        print(f"[db] Deleted resident '{name}' ({deleted} row(s))")
    else:
        print(f"[db] No resident found with name '{name}'")


def clear_db():
    """Wipe all residents from the database. Use for testing."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"[db] Cleared all residents ({deleted} row(s) deleted)")


def list_residents():
    """Print all enrolled residents (for quick inspection)."""
    residents = get_all_residents()
    if not residents:
        print("[db] No residents enrolled.")
        return
    print(f"[db] {len(residents)} resident(s) enrolled:")
    for name, emb in residents:
        print(f"  - {name} (embedding dim: {emb.shape[0]})")


# ---- Quick self-test ----
if __name__ == "__main__":
    print("Running db.py self-test...\n")

    init_db()

    # Insert a fake resident
    fake_embedding = np.random.randn(512).astype(np.float32)
    insert_resident("test_user", fake_embedding)

    # List residents
    list_residents()

    # Retrieve and verify
    residents = get_all_residents()
    assert len(residents) == 1, f"Expected 1 resident, got {len(residents)}"
    assert residents[0][0] == "test_user"
    assert residents[0][1].shape == (512,)
    print("\n[test] Read-back verified: name and embedding match.")

    # Delete specific resident
    delete_resident("test_user")
    assert len(get_all_residents()) == 0
    print("[test] Delete verified.")

    # Clean up
    clear_db()
    os.remove(DB_PATH)
    print("\n[test] All tests passed! Database file cleaned up.")
