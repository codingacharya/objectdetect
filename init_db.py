import sqlite3

# Connect and create the database file
conn = sqlite3.connect('detections.db')

# Create table
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        object_label TEXT NOT NULL,
        action_label TEXT NOT NULL,
        confidence REAL,
        bbox_xmin INTEGER,
        bbox_ymin INTEGER,
        bbox_xmax INTEGER,
        bbox_ymax INTEGER
    )
''')

conn.commit()
conn.close()

print("detections.db created successfully!")
