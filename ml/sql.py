import sqlite3

conn = sqlite3.connect("recycle_materia.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM materials")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
