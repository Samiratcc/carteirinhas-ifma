from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os
import subprocess
import cv2

# =========================
# CONFIGURAÇÕES DO SITE
# =========================
USUARIO_GITHUB = "samiratcc"
REPO_GITHUB = "carteirinhas-ifma"

# =========================
# TAMANHO PADRÃO
# =========================
W, H = 1016, 638

# =========================
# CORES
# =========================
VERDE1 = (0, 130, 60)
VERDE2 = (0, 95, 45)
VERMELHO = (210, 35, 50)

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

CINZA_FUNDO = (245, 245, 245)
CINZA_BORDA = (210, 210, 210)
CINZA_BORDA2 = (235, 235, 235)
CINZA_LINHA = (175, 175, 175)

# =========================
# CAMINHOS
# =========================
BASE_DIR = os.path.dirname(__file__)
PASTA_FONTES = os.path.join(BASE_DIR, "fonts")
PASTA_ALUNOS = os.path.join(BASE_DIR, "alunos")
PASTA_FOTOS = os.path.join(BASE_DIR, "fotos")

os.makedirs(PASTA_ALUNOS, exist_ok=True)
os.makedirs(PASTA_FOTOS, exist_ok=True)

# =========================
# FONTES
# =========================
try:
    f_titulo_frente = ImageFont.truetype(os.path.join(PASTA_FONTES, "Montserrat-Bold.ttf"), 44)
    f_subtitulo_frente = ImageFont.truetype(os.path.join(PASTA_FONTES, "Montserrat-SemiBold.ttf"), 30)

    f_label = ImageFont.truetype(os.path.join(PASTA_FONTES, "Montserrat-Bold.ttf"), 30)
    f_texto = ImageFont.truetype(os.path.join(PASTA_FONTES, "Montserrat-Medium.ttf"), 28)

    f_titulo_verso = ImageFont.truetype(os.path.join(PASTA_FONTES, "Montserrat-Bold.ttf"), 48)
    f_subtitulo_verso = ImageFont.truetype(os.path.join(PASTA_FONTES, "Montserrat-SemiBold.ttf"), 34)

except:
    f_titulo_frente = ImageFont.load_default()
    f_subtitulo_frente = ImageFont.load_default()
    f_label = ImageFont.load_default()
    f_texto = ImageFont.load_default()
    f_titulo_verso = ImageFont.load_default()
    f_subtitulo_verso = ImageFont.load_default()

# =========================
# 📷 CAPTURA DE FOTO
# =========================
def capturar_foto(caminho_saida):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Erro ao acessar a câmera")
        return

    print("📷 Pressione ESPAÇO para tirar foto")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Camera", frame)

        tecla = cv2.waitKey(1)

        if tecla % 256 == 32:
            cv2.imwrite(caminho_saida, frame)
            print("✅ Foto capturada!")
            break

        elif tecla % 256 == 27:
            print("❌ Cancelado")
            break

    cap.release()
    cv2.destroyAllWindows()

# =========================
# GRADIENTE
# =========================
def gradient_rect(draw, x1, y1, x2, y2, c1, c2):
    altura = y2 - y1
    for i in range(altura):
        t = i / altura
        cor = (
            int(c1[0] * (1 - t) + c2[0] * t),
            int(c1[1] * (1 - t) + c2[1] * t),
            int(c1[2] * (1 - t) + c2[2] * t),
        )
        draw.line((x1, y1 + i, x2, y1 + i), fill=cor)

# =========================
# BASE PVC
# =========================
def criar_base_pvc():
    fundo = Image.new("RGB", (W + 50, H + 50), (240, 240, 240))

    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    ds.rounded_rectangle((0, 0, W, H), radius=55, fill=(0, 0, 0, 130))
    sombra = sombra.filter(ImageFilter.GaussianBlur(20))
    fundo.paste(sombra, (25, 25), sombra)

    cartao = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(cartao)

    d.rounded_rectangle((0, 0, W, H), radius=55, outline=CINZA_BORDA, width=6)
    d.rounded_rectangle((10, 10, W - 10, H - 10), radius=48, outline=CINZA_BORDA2, width=4)

    fundo.paste(cartao, (25, 25), cartao)
    return fundo

def aplicar_mascara(img, radius=55):
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle((0, 0, W, H), radius=radius, fill=255)
    img.putalpha(mask)
    return img

# =========================
# QR CODE
# =========================
def gerar_qrcode(link):
    qr = qrcode.make(link)
    return qr.resize((320, 320))

# =========================
# HTML
# =========================
def gerar_html_aluno(matricula):
    caminho = os.path.join(PASTA_ALUNOS, f"{matricula}.html")

    html = f"""
    <html><body style="text-align:center">
    <h1>Carteirinha</h1>
    <img src="{matricula}_frente.png"><br>
    <img src="{matricula}_verso.png">
    </body></html>
    """

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)

# =========================
# INDEX
# =========================
def atualizar_index(matricula):
    index = os.path.join(BASE_DIR, "index.html")

    if not os.path.exists(index):
        with open(index, "w") as f:
            f.write("<html><body><h1>Carteirinhas</h1></body></html>")

    with open(index, "r") as f:
        conteudo = f.read()

    link = f'<p><a href="alunos/{matricula}.html">{matricula}</a></p>'

    if link not in conteudo:
        conteudo = conteudo.replace("</body>", link + "</body>")

        with open(index, "w") as f:
            f.write(conteudo)

# =========================
# GITHUB
# =========================
def enviar_para_github(matricula):
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", matricula])
    subprocess.run(["git", "push"])

# =========================
# FRENTE
# =========================
def gerar_frente(nome, matricula, curso, turno, email, foto):

    img = criar_base_pvc().convert("RGBA")
    cartao = Image.new("RGBA", (W, H), BRANCO)
    draw = ImageDraw.Draw(cartao)

    gradient_rect(draw, 0, 155, W, 190, VERDE1, VERDE2)

    # FOTO
    foto = foto.resize((290, 300))
    cartao.paste(foto, (70, 220))

    draw.text((410, 220), f"Nome: {nome}", fill=PRETO, font=f_texto)
    draw.text((410, 280), f"Matrícula: {matricula}", fill=PRETO, font=f_texto)
    draw.text((410, 340), f"Curso: {curso}", fill=PRETO, font=f_texto)
    draw.text((410, 400), f"Turno: {turno}", fill=PRETO, font=f_texto)
    draw.text((410, 460), f"Email: {email}", fill=PRETO, font=f_texto)

    cartao = aplicar_mascara(cartao)
    img.paste(cartao, (25, 25), cartao)

    caminho = os.path.join(PASTA_ALUNOS, f"{matricula}_frente.png")
    img.save(caminho)

# =========================
# VERSO
# =========================
def gerar_verso(matricula):

    img = criar_base_pvc().convert("RGBA")
    cartao = Image.new("RGBA", (W, H), BRANCO)

    link = f"https://{USUARIO_GITHUB}.github.io/{REPO_GITHUB}/alunos/{matricula}.html"
    qr = gerar_qrcode(link)

    cartao.paste(qr, (350, 200))

    cartao = aplicar_mascara(cartao)
    img.paste(cartao, (25, 25), cartao)

    caminho = os.path.join(PASTA_ALUNOS, f"{matricula}_verso.png")
    img.save(caminho)

# =========================
# MAIN
# =========================
def main():

    nome = input("Nome: ")
    matricula = input("Matrícula: ")
    curso = input("Curso: ")
    turno = input("Turno: ")
    email = input("Email: ")

    foto_path = os.path.join(PASTA_FOTOS, f"{matricula}.png")

    capturar_foto(foto_path)

    foto = Image.open(foto_path).convert("RGBA")

    gerar_frente(nome, matricula, curso, turno, email, foto)
    gerar_verso(matricula)
    gerar_html_aluno(matricula)
    atualizar_index(matricula)
    enviar_para_github(matricula)

    print("✅ Tudo pronto!")
    print(f"https://{USUARIO_GITHUB}.github.io/{REPO_GITHUB}/alunos/{matricula}.html")


if __name__ == "__main__":
    main()