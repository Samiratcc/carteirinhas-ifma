import sqlite3

conn = sqlite3.connect("presencas.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM presencas")

conn.commit()

print("Presenças apagadas!")

conn.close()

exit()