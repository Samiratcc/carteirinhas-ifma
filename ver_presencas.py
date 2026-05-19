import sqlite3

conn = sqlite3.connect("presencas.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM presencas")

dados = cursor.fetchall()

for linha in dados:
    print(linha)

conn.close()