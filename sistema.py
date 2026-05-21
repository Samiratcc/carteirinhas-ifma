import customtkinter as ctk
from carteirinha import *
from PIL import Image
from PIL import Image as PILImage
import sqlite3
from tkinter import ttk
from datetime import datetime
from openpyxl import Workbook
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="white",
    foreground="black",
    rowheight=38,
    fieldbackground="white",
    font=("Arial", 11),
    borderwidth=0
)

style.configure(
    "Treeview.Heading",
    background="#14532d",
    foreground="white",
    font=("Arial", 12, "bold"),
    relief="flat"
)

style.map(
    "Treeview.Heading",
    background=[("active", "#14532d")],
    foreground=[("active", "white")]
)
style.layout("Treeview.Heading", [
    ('Treeheading.cell', {'sticky': 'nswe'}),
    ('Treeheading.border', {'sticky': 'nswe', 'children': [
        ('Treeheading.padding', {'sticky': 'nswe', 'children': [
            ('Treeheading.image', {'side': 'right', 'sticky': ''}),
            ('Treeheading.text', {'sticky': 'we'})
        ]})
    ]}),
])

conn = sqlite3.connect("presencas.db")
cursor = conn.cursor()

# aparência
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# janela
app = ctk.CTk()
app.title("Sistema IFMA")
app.geometry("1200x700")

# =========================
# ÁREA PRINCIPAL
# =========================
conteudo = ctk.CTkFrame(app, fg_color="#f5f5f5")

conteudo.pack(
    side="right",
    expand=True,
    fill="both"
)

# =========================
# LIMPAR TELA
# =========================
def limpar_tela():

    for widget in conteudo.winfo_children():
        widget.destroy()
# =========================
# GERAR CARTEIRINHA
# =========================
def gerar_carteirinha():

    nome = entrada_nome.get()
    matricula = entrada_matricula.get()
    curso = combo_curso.get()
    turno = combo_turno.get()

    inicio_email = entrada_email.get()
    email = f"{inicio_email}@acad.ifma.edu.br"

    # captura foto
    caminho_foto = capturar_foto(matricula)

    if caminho_foto is None:
        return

    foto = Image.open(caminho_foto).convert("RGBA")

    gerar_frente(
        nome,
        matricula,
        curso,
        turno,
        email,
        foto
    )

    gerar_html_aluno(matricula)
    gerar_verso(matricula)
    atualizar_index(matricula)
    enviar_para_github(matricula)

    mensagem_sucesso = ctk.CTkLabel(
        conteudo,
        text="✅ Carteirinha cadastrada com sucesso!",
        font=("Arial", 18, "bold"),
        text_color="#14532d"
    )
    mensagem_sucesso.pack(pady=10)

    app.after(3000, tela_cadastro)
# =========================
# TELA CADASTRO
# =========================
def tela_cadastro():

    global entrada_nome
    global entrada_matricula
    global combo_curso
    global combo_turno
    global entrada_email

    limpar_tela()

    titulo = ctk.CTkLabel(
        conteudo,
        text="Cadastro de Carteirinha",
        font=("Arial", 34, "bold"),
        text_color="#14532d"
    )
    titulo.pack(pady=(30, 5))

    subtitulo = ctk.CTkLabel(
        conteudo,
        text="Preencha os dados do aluno para gerar a carteirinha",
        font=("Arial", 16),
        text_color="#333333"
    )
    subtitulo.pack(pady=(0, 20))

    area = ctk.CTkFrame(
        conteudo,
        fg_color="transparent"
    )
    area.pack(pady=10)

    card_dados = ctk.CTkFrame(
        area,
        width=500,
        height=430,
        corner_radius=18,
        fg_color="white"
    )
    card_dados.grid(row=0, column=0, padx=15)
    card_dados.pack_propagate(False)

    card_foto = ctk.CTkFrame(
        area,
        width=260,
        height=430,
        corner_radius=18,
        fg_color="white"
    )
    card_foto.grid(row=0, column=1, padx=15)
    card_foto.pack_propagate(False)

    ctk.CTkLabel(
        card_dados,
        text="Dados do Aluno",
        font=("Arial", 20, "bold"),
        text_color="#14532d"
    ).pack(anchor="w", padx=30, pady=(25, 10))

    entrada_nome = ctk.CTkEntry(
        card_dados,
        placeholder_text="Nome completo",
        width=420,
        height=42
    )
    entrada_nome.pack(pady=8)

    entrada_matricula = ctk.CTkEntry(
        card_dados,
        placeholder_text="Matrícula",
        width=420,
        height=42
    )
    entrada_matricula.pack(pady=8)

    cursos = [
        "Automação Industrial",
        "Eletromecânica",
        "Alimentos",
        "Meio Ambiente",
        "Informática",
        "Química",
        "Matemática",
        "Biologia"
    ]

    combo_curso = ctk.CTkComboBox(
        card_dados,
        values=cursos,
        width=420,
        height=42
    )
    combo_curso.set("Selecione o curso")
    combo_curso.pack(pady=8)

    turnos = [
        "Matutino",
        "Vespertino",
        "Noturno"
    ]

    combo_turno = ctk.CTkComboBox(
        card_dados,
        values=turnos,
        width=420,
        height=42
    )
    combo_turno.set("Selecione o turno")
    combo_turno.pack(pady=8)

    entrada_email = ctk.CTkEntry(
        card_dados,
        placeholder_text="Início do e-mail institucional",
        width=420,
        height=42
    )
    entrada_email.pack(pady=8)

    ctk.CTkLabel(
        card_dados,
        text="@acad.ifma.edu.br será adicionado automaticamente",
        font=("Arial", 12),
        text_color="#555555"
    ).pack(pady=5)

    ctk.CTkLabel(
        card_foto,
        text="Foto do Aluno",
        font=("Arial", 20, "bold"),
        text_color="#14532d"
    ).pack(pady=(25, 15))

    preview_foto = ctk.CTkFrame(
        card_foto,
        width=170,
        height=200,
        corner_radius=15,
        fg_color="#dcdcdc"
    )

    preview_foto.pack(pady=10)
    preview_foto.pack_propagate(False)

    preview_foto_label = ctk.CTkLabel(
        preview_foto,
        text="Foto\ncapturada\npela câmera",
        font=("Arial", 15),
        text_color="#555555"
    )

    preview_foto_label.pack(expand=True)

    ctk.CTkButton(
        card_foto,
        text="Capturar Foto e Gerar",
        width=190,
        height=45,
        font=("Arial", 14, "bold"),
        fg_color="#14532d",
        hover_color="#1f7a3f",
        command=gerar_carteirinha
    ).pack(pady=25)

    btn_voltar = ctk.CTkButton(
        conteudo,
        text="Voltar ao Início",
        width=180,
        fg_color="#14532d",
        hover_color="#1f7a3f",
        command=tela_inicio
    )
    btn_voltar.pack(pady=20)
# =========================
# TELA PAINEL
# =========================
def tela_painel():

    limpar_tela()

    painel_scroll = ctk.CTkScrollableFrame(
        conteudo,
        fg_color="#f5f5f5"
    )
    painel_scroll.pack(fill="both", expand=True)

    titulo = ctk.CTkLabel(
        painel_scroll,
        text="Painel de Presenças",
        font=("Arial", 30, "bold")
    )

    titulo.pack(pady=20)

    hoje = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("SELECT COUNT(*) FROM presencas WHERE data = ?", (hoje,))
    presentes_hoje = cursor.fetchone()[0]

    total_alunos = len([
        nome for nome in os.listdir("fotos")
        if os.path.isdir(os.path.join("fotos", nome))
    ])

    cursor.execute("SELECT COUNT(DISTINCT turma || ano) FROM presencas")
    turmas_ativas = cursor.fetchone()[0]

    if total_alunos > 0:
        taxa = int((presentes_hoje / total_alunos) * 100)
    else:
        taxa = 0

    # =========================
    # CARDS
    # =========================

    frame_cards = ctk.CTkFrame(
        painel_scroll,
        fg_color="transparent"
    )

    frame_cards.pack(pady=15)

    # CARD 1
    card1 = ctk.CTkFrame(
        frame_cards,
        width=180,
        height=120,
        corner_radius=15
    )
    card1.grid(row=0, column=0, padx=15)

    ctk.CTkLabel(
        card1,
        text="Presentes Hoje",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        card1,
        text=str(presentes_hoje),
        font=("Arial", 36, "bold"),
        text_color="green"
    ).pack()

    # CARD 2
    card2 = ctk.CTkFrame(
        frame_cards,
        width=180,
        height=120,
        corner_radius=15
    )
    card2.grid(row=0, column=1, padx=15)

    ctk.CTkLabel(
        card2,
        text="Total de Alunos",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        card2,
        text=str(total_alunos),
        font=("Arial", 36, "bold"),
        text_color="#1f6aa5"
    ).pack()

    # CARD 3
    card3 = ctk.CTkFrame(
        frame_cards,
        width=180,
        height=120,
        corner_radius=15
    )
    card3.grid(row=0, column=2, padx=15)

    ctk.CTkLabel(
        card3,
        text="Turmas",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        card3,
        text=str(turmas_ativas),
        font=("Arial", 36, "bold"),
        text_color="#a56a1f"
    ).pack()

    # CARD 4
    card4 = ctk.CTkFrame(
        frame_cards,
        width=180,
        height=120,
        corner_radius=15
    )
    card4.grid(row=0, column=3, padx=15)

    ctk.CTkLabel(
        card4,
        text="Taxa Presença",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    ctk.CTkLabel(
        card4,
        text=f"{taxa}%",
        font=("Arial", 36, "bold"),
        text_color="#7a1fa5"
    ).pack()

        # =========================
    # FILTROS
    # =========================

    frame_filtros = ctk.CTkFrame(
        painel_scroll,
        corner_radius=15,
        fg_color="white"
    )

    frame_filtros.pack(
        fill="x",
        padx=25,
        pady=10
    )

    ctk.CTkLabel(
        frame_filtros,
        text="Filtros de Pesquisa",
        font=("Arial", 16, "bold"),
        text_color="#14532d"
    ).grid(row=0, column=0, columnspan=5, sticky="w", padx=15, pady=(10, 5))

    entrada_data = ctk.CTkEntry(
        frame_filtros,
        placeholder_text="Data",
        width=160
    )
    entrada_data.grid(row=1, column=0, padx=10, pady=10)

    combo_curso = ctk.CTkComboBox(
        frame_filtros,
        values=[
            "Automação",
            "Alimentos",
            "Eletromecânica",
            "Meio Ambiente",
            "Informática",
            "Química",
            "Matemática",
            "Biologia"
        ],
        width=170
    )
    combo_curso.grid(row=1, column=1, padx=10, pady=10)

    combo_ano = ctk.CTkComboBox(
        frame_filtros,
        values=["2024", "2025", "2026", "2027"],
        width=140
    )
    combo_ano.grid(row=1, column=2, padx=10, pady=10)

    # =========================
    # FRAME DA TABELA
    # =========================

    frame_tabela = ctk.CTkFrame(
        painel_scroll,
        corner_radius=20,
        fg_color="#dcdcdc"
    )

    frame_tabela.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=20
    )

    titulo_tabela = ctk.CTkLabel(
        frame_tabela,
        text="Presenças Registradas",
        font=("Arial", 18, "bold"),
        text_color="black"
    )

    titulo_tabela.pack(pady=15)

    scrollbar = ttk.Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")
    tabela = ttk.Treeview(
        frame_tabela,
        columns=("matricula", "turma", "ano", "hora", "status"),
        show="headings",
        height=7,
        yscrollcommand=scrollbar.set
    )
    scrollbar.config(command=tabela.yview)

    tabela.heading("matricula", text="Matrícula")
    tabela.heading("turma", text="Curso")
    tabela.heading("ano", text="Turma/Ano")
    tabela.heading("hora", text="Entrada")
    tabela.heading("status", text="Status")

    tabela.column("matricula", width=180, anchor="center")
    tabela.column("turma", width=160, anchor="center")
    tabela.column("ano", width=120, anchor="center")
    tabela.column("hora", width=140, anchor="center")
    tabela.column("status", width=140, anchor="center")

    tabela.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    # =========================
    # FUNÇÃO BUSCAR
    # =========================

    def buscar():

        for item in tabela.get_children():
            tabela.delete(item)

        data = entrada_data.get()
        curso = combo_curso.get()
        ano = combo_ano.get()

        cursor.execute("""
        SELECT matricula, turma, ano, hora, status
        FROM presencas
        WHERE data = ?
        AND turma = ?
        AND ano = ?
        """, (data, curso, ano))

        resultados = cursor.fetchall()

        for linha in resultados:
            tabela.insert("", "end", values=linha)

    def exportar_excel():

        wb = Workbook()
        ws = wb.active
        ws.title = "Presenças"

        ws.append(["Matrícula", "Turma", "Ano", "Horário", "Status"])

        for item in tabela.get_children():
            valores = tabela.item(item)["values"]
            ws.append(valores)

        wb.save("relatorio_presencas.xlsx")

        messagebox.showinfo(
            "Exportado",
            "Relatório salvo como relatorio_presencas.xlsx"
        )

    botao_buscar = ctk.CTkButton(
        frame_filtros,
        text="Buscar",
        command=buscar
    )
    botao_buscar.grid(row=1, column=3, padx=10, pady=10)

    botao_exportar = ctk.CTkButton(
        frame_filtros,
        text="Exportar Excel",
        command=exportar_excel
    )
    botao_exportar.grid(row=1, column=4, padx=10, pady=10)

        # =========================
    # GRÁFICOS
    # =========================

    frame_graficos = ctk.CTkFrame(
        painel_scroll,
        fg_color="transparent"
    )
    frame_graficos.pack(fill="x", padx=25, pady=10)

    grafico1 = ctk.CTkFrame(
        frame_graficos,
        corner_radius=15,
        fg_color="white"
    )
    grafico1.grid(row=0, column=0, padx=10, sticky="nsew")

    grafico2 = ctk.CTkFrame(
        frame_graficos,
        corner_radius=15,
        fg_color="white"
    )
    grafico2.grid(row=0, column=1, padx=10, sticky="nsew")

    frame_graficos.grid_columnconfigure(0, weight=1)
    frame_graficos.grid_columnconfigure(1, weight=1)

    # gráfico de barras por curso
    cursos = [
        "Automação",
        "Alimentos",
        "Eletromecânica",
        "Meio Ambiente",
        "Informática",
        "Química",
        "Matemática",
        "Biologia"
    ]

    quantidades = []

    for curso in cursos:

        cursor.execute("""
        SELECT COUNT(*)
        FROM presencas
        WHERE data = ?
        AND turma = ?
        """, (hoje, curso))

        total = cursor.fetchone()[0]

        quantidades.append(total)
    fig1 = Figure(figsize=(7, 4), dpi=100)
    ax1 = fig1.add_subplot(111)

    ax1.bar(cursos, quantidades)
    ax1.set_title("Presenças por Curso (Hoje)")
    ax1.set_ylim(0, 40)
    ax1.set_yticks([0, 10, 20, 30, 40])
    ax1.tick_params(axis="x", rotation=25, labelsize=9)
    fig1.tight_layout()

    canvas1 = FigureCanvasTkAgg(fig1, master=grafico1)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # gráfico de pizza taxa de presença
    presentes = presentes_hoje
    ausentes = max(total_alunos - presentes_hoje, 0)

    fig2 = Figure(figsize=(5, 3), dpi=100)
    ax2 = fig2.add_subplot(111)

    ax2.pie(
        [presentes, ausentes],
        labels=["Presentes", "Ausentes"],
        autopct="%1.0f%%",
        startangle=90
    )

    ax2.set_title("Taxa de Presença (Hoje)")

    canvas2 = FigureCanvasTkAgg(fig2, master=grafico2)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

# =========================
# TELA INICIAL
# =========================
def tela_inicio():

    limpar_tela()

    # CONTAINER PRINCIPAL
    hero = ctk.CTkFrame(
        conteudo,
        fg_color="white",
        corner_radius=25
    )
    hero.pack(fill="both", expand=True, padx=35, pady=35)

    # TEXTO ESQUERDA
    bloco_texto = ctk.CTkFrame(
        hero,
        fg_color="transparent"
    )
    bloco_texto.place(relx=0.08, rely=0.18)

    ctk.CTkLabel(
        bloco_texto,
        text="Bem-vindo(a)",
        font=("Arial", 20, "bold"),
        text_color="#0f7a2e"
    ).pack(anchor="w", pady=(0, 15))

    ctk.CTkLabel(
        bloco_texto,
        text="Sistema de Controle\nde Frequência de Discentes",
        font=("Arial", 42, "bold"),
        text_color="#102820",
        justify="left"
    ).pack(anchor="w")

    ctk.CTkLabel(
        bloco_texto,
        text="Autenticação Multifatorial\ne Processamento de Imagem",
        font=("Arial", 24),
        text_color="#5f6f6a",
        justify="left"
    ).pack(anchor="w", pady=20)

    ctk.CTkLabel(
        bloco_texto,
        text="Segurança, tecnologia e inovação\na serviço da educação.",
        font=("Arial", 16),
        text_color="#5f6f6a",
        justify="left"
    ).pack(anchor="w", pady=25)


    # CARDS INFERIORES
    frame_cards_inicio = ctk.CTkFrame(
        hero,
        fg_color="transparent"
    )
    frame_cards_inicio.place(relx=0.08, rely=0.72)

    card1 = ctk.CTkButton(
        frame_cards_inicio,
        text="Cadastrar Carteirinha\nGerar identificação do aluno",
        width=260,
        height=90,
        font=("Arial", 15, "bold"),
        fg_color="white",
        text_color="#102820",
        hover_color="#e8f5ec",
        border_width=1,
        border_color="#d0d0d0",
        command=tela_cadastro
    )
    card1.grid(row=0, column=0, padx=12)

    card2 = ctk.CTkButton(
        frame_cards_inicio,
        text="Painel de Presenças\nConsultar registros e relatórios",
        width=260,
        height=90,
        font=("Arial", 15, "bold"),
        fg_color="white",
        text_color="#102820",
        hover_color="#e8f5ec",
        border_width=1,
        border_color="#d0d0d0",
        command=tela_painel
    )
    card2.grid(row=0, column=1, padx=12)

    card3 = ctk.CTkButton(
        frame_cards_inicio,
        text="Sistema Integrado\nQR Code + reconhecimento facial",
        width=260,
        height=90,
        font=("Arial", 15, "bold"),
        fg_color="white",
        text_color="#102820",
        hover_color="#e8f5ec",
        border_width=1,
        border_color="#d0d0d0"
    )
    card3.grid(row=0, column=2, padx=12)


# =========================
# MENU LATERAL
# =========================
menu = ctk.CTkFrame(
    app,
    width=250,
    corner_radius=0,
    fg_color="#0f3d1f"
)
menu.pack(side="left", fill="y")

titulo_menu = ctk.CTkLabel(
    menu,
    text="IFMA\nSistema",
    font=("Arial", 28, "bold"),
    text_color="white"
)
titulo_menu.pack(pady=40)

btn_inicio = ctk.CTkButton(
    menu,
    text="Início",
    command=tela_inicio,
    fg_color="#14532d",
    hover_color="#1f7a3f"
)
btn_inicio.pack(pady=10, padx=20)

btn_cadastro = ctk.CTkButton(
    menu,
    text="Cadastrar Carteirinha",
    command=tela_cadastro,
    fg_color="#14532d",
    hover_color="#1f7a3f"
)
btn_cadastro.pack(pady=10, padx=20)

btn_painel = ctk.CTkButton(
    menu,
    text="Painel de Presenças",
    command=tela_painel,
    fg_color="#14532d",
    hover_color="#1f7a3f"
)
btn_painel.pack(pady=10, padx=20)

btn_sair = ctk.CTkButton(
    menu,
    text="Sair",
    fg_color="red",
    hover_color="#aa0000",
    command=app.destroy
)
btn_sair.pack(side="bottom", pady=20, padx=20)

tela_inicio()

app.mainloop()