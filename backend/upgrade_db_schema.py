"""
Upgrade database schema to add mutation_attempts table and baseline_score column
Run this ONCE to upgrade existing database
"""
import sqlite3
import os

DB_PATH = "data.db"

def upgrade_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. No upgrade needed - will be created fresh.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Upgrading database schema...")

    # Add baseline_score column to agent_versions if it doesn't exist
    try:
        cursor.execute("ALTER TABLE agent_versions ADD COLUMN baseline_score REAL")
        print("[OK] Added baseline_score column to agent_versions")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("[SKIP] baseline_score column already exists")
        else:
            raise

    # Create mutation_attempts table if it doesn't exist
    try:
        cursor.execute("""
            CREATE TABLE mutation_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id INTEGER NOT NULL,
                mutation_index INTEGER NOT NULL,
                mutated_prompt TEXT,
                avg_score REAL,
                is_winner INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (version_id) REFERENCES agent_versions(id)
            )
        """)
        print("[OK] Created mutation_attempts table")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("[SKIP] mutation_attempts table already exists")
        else:
            raise

    conn.commit()
    conn.close()

    print("\nDatabase upgrade complete!")
    print("Note: Existing versions won't have mutation_attempts. Only new evolutions will store mutation data.")

if __name__ == "__main__":
    upgrade_schema()
