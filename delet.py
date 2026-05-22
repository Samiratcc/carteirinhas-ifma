import os
import shutil
import sqlite3

matriculas = [
    "20241AUA0004",
]

# apagar arquivos e pastas
pastas = ["alunos", "fotos"]

for pasta in pastas:
    if os.path.exists(pasta):
        for item in os.listdir(pasta):
            for matricula in matriculas:
                if matricula.upper() in item.upper():
                    caminho = os.path.join(pasta, item)

                    if os.path.isdir(caminho):
                        shutil.rmtree(caminho)
                    else:
                        os.remove(caminho)

                    print(f"Removido: {caminho}")

# apagar do banco de presenças
if os.path.exists("presencas.db"):
    conn = sqlite3.connect("presencas.db")
    cursor = conn.cursor()

    for matricula in matriculas:
        cursor.execute(
            "DELETE FROM presencas WHERE UPPER(matricula) = ?",
            (matricula.upper(),)
        )

    conn.commit()
    conn.close()

    print("Registros removidos do banco presencas.db")

# limpar links do index.html
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        linhas = f.readlines()

    novas_linhas = []
    for linha in linhas:
        manter = True
        for matricula in matriculas:
            if matricula.upper() in linha.upper():
                manter = False
                break
        if manter:
            novas_linhas.append(linha)

    with open("index.html", "w", encoding="utf-8") as f:
        f.writelines(novas_linhas)

    print("Links removidos do index.html")

print("Limpeza concluída!")