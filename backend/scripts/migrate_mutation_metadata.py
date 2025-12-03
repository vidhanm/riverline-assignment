"""
Migration script to add mutation_metadata and reasoning_prompt columns to mutation_attempts table
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(mutation_attempts)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'mutation_metadata' not in columns:
        print("Adding mutation_metadata column...")
        cursor.execute("ALTER TABLE mutation_attempts ADD COLUMN mutation_metadata TEXT")
    else:
        print("mutation_metadata column already exists")

    if 'reasoning_prompt' not in columns:
        print("Adding reasoning_prompt column...")
        cursor.execute("ALTER TABLE mutation_attempts ADD COLUMN reasoning_prompt TEXT")
    else:
        print("reasoning_prompt column already exists")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
