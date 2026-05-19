import sqlite3
import tkinter as tk
from tkinter import ttk

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect("presencas.db")
cursor = conn.cursor()

# =========================
# JANELA
# =========================
janela = tk.Tk()

janela.title("Painel de Presenças IFMA")
janela.geometry("900x500")

# =========================
# DATA
# =========================
label_data = tk.Label(janela, text="Data:")
label_data.pack()

entrada_data = tk.Entry(janela)
entrada_data.pack()

# =========================
# TURMA
# =========================
label_turma = tk.Label(janela, text="Turma:")
label_turma.pack()

combo_turma = ttk.Combobox(janela)

combo_turma["values"] = (
    "Automação",
    "Alimentos",
    "Eletromecânica",
    "Meio Ambiente",
    "Informática",
    "Química",
    "Matemática",
    "Biologia"
)

combo_turma.pack()

# =========================
# ANO
# =========================
label_ano = tk.Label(janela, text="Ano:")
label_ano.pack()

combo_ano = ttk.Combobox(janela)

combo_ano["values"] = (
    "2024",
    "2025",
    "2026"
)

combo_ano.pack()

# =========================
# TABELA
# =========================
colunas = ("matricula", "hora", "status")

tabela = ttk.Treeview(
    janela,
    columns=colunas,
    show="headings"
)

tabela.heading("matricula", text="Matrícula")
tabela.heading("hora", text="Horário")
tabela.heading("status", text="Status")

tabela.pack(fill="both", expand=True)

# =========================
# CONSULTAR
# =========================
def consultar():

    # limpa tabela
    for item in tabela.get_children():
        tabela.delete(item)

    data = entrada_data.get()
    turma = combo_turma.get()
    ano = combo_ano.get()

    cursor.execute("""
    SELECT matricula, hora, status
    FROM presencas
    WHERE data = ? AND turma = ? AND ano = ?
    """, (data, turma, ano))

    resultados = cursor.fetchall()

    for linha in resultados:
        tabela.insert("", tk.END, values=linha)

# =========================
# BOTÃO
# =========================
botao = tk.Button(
    janela,
    text="Consultar",
    command=consultar,
    bg="green",
    fg="white"
)

botao.pack(pady=10)

# =========================
# LOOP
# =========================
janela.mainloop()