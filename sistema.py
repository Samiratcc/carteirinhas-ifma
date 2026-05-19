import customtkinter as ctk
from carteirinha import *

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
conteudo = ctk.CTkFrame(app)

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

    print("CARTEIRINHA GERADA!")
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
        text="Cadastro de Carteirinhas",
        font=("Arial", 30, "bold")
    )

    titulo.pack(pady=30)

    entrada_nome = ctk.CTkEntry(
        conteudo,
        placeholder_text="Nome do aluno",
        width=400,
        height=40
    )

    entrada_nome.pack(pady=10)

    entrada_matricula = ctk.CTkEntry(
        conteudo,
        placeholder_text="Matrícula",
        width=400,
        height=40
    )

    entrada_matricula.pack(pady=10)

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
        conteudo,
        values=cursos,
        width=400,
        height=40
    )

    combo_curso.pack(pady=10)

    botao = ctk.CTkButton(
        conteudo,
        text="Gerar Carteirinha",
        width=300,
        height=45,
        command=gerar_carteirinha
    )

    # TURNO
    turnos = [
        "Matutino",
        "Vespertino",
        "Noturno"
    ]

    combo_turno = ctk.CTkComboBox(
        conteudo,
        values=turnos,
        width=400,
        height=40
    )

    combo_turno.pack(pady=10)

    # EMAIL
    entrada_email = ctk.CTkEntry(
        conteudo,
        placeholder_text="Início do email",
        width=400,
        height=40
    )
    entrada_email.pack(pady=10)

    botao.pack(pady=30)

# =========================
# TELA PAINEL
# =========================
def tela_painel():

    limpar_tela()

    titulo = ctk.CTkLabel(
        conteudo,
        text="Painel de Presenças",
        font=("Arial", 30, "bold")
    )

    titulo.pack(pady=30)

    texto = ctk.CTkLabel(
        conteudo,
        text="Aqui aparecerão as presenças registradas",
        font=("Arial", 18)
    )

    texto.pack(pady=20)

# =========================
# MENU LATERAL
# =========================
menu = ctk.CTkFrame(
    app,
    width=250,
    corner_radius=0
)

menu.pack(side="left", fill="y")

# título
titulo = ctk.CTkLabel(
    menu,
    text="IFMA\nSistema",
    font=("Arial", 28, "bold")
)

titulo.pack(pady=40)

# botões
btn_cadastro = ctk.CTkButton(
    menu,
    text="Cadastrar Carteirinha",
    command=tela_cadastro
)

btn_cadastro.pack(pady=10, padx=20)

btn_painel = ctk.CTkButton(
    menu,
    text="Painel de Presenças",
    command=tela_painel
)

btn_painel.pack(pady=10, padx=20)

btn_relatorios = ctk.CTkButton(
    menu,
    text="Relatórios"
)

btn_relatorios.pack(pady=10, padx=20)

btn_sair = ctk.CTkButton(
    menu,
    text="Sair",
    fg_color="red",
    hover_color="#aa0000"
)

btn_sair.pack(side="bottom", pady=20, padx=20)

tela_cadastro()
app.mainloop()