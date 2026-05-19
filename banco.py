import sqlite3

# cria/conecta banco
conn = sqlite3.connect("presencas.db")

# cria cursor
cursor = conn.cursor()

# cria tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS presencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula TEXT,
    data TEXT,
    hora TEXT,
    status TEXT
)
""")

# salva alterações
conn.commit()

# fecha banco
conn.close()

print("✅ Banco criado com sucesso!")