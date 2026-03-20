from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os
import subprocess
import cv2
import time  # 🔥 NOVO

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

os.makedirs(PASTA_ALUNOS, exist_ok=True)
os.makedirs("fotos", exist_ok=True)

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
# 📷 CAPTURA FOTO
# =========================
def capturar_foto(caminho_saida):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Erro ao abrir câmera")
        return False

    print("📷 Pressione ESPAÇO para tirar foto")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Camera", frame)
        tecla = cv2.waitKey(1)

        if tecla == 32:
            cv2.imwrite(caminho_saida, frame)
            print("✅ Foto capturada!")
            break

        elif tecla == 27:
            print("❌ Cancelado")
            break

    cap.release()
    cv2.destroyAllWindows()
    return True

# =========================
# ESPERA FOTO EXISTIR
# =========================
def esperar_foto(caminho, tentativas=10):
    for _ in range(tentativas):
        if os.path.exists(caminho):
            return True
        time.sleep(0.5)
    return False

# =========================
# RESTO DO CÓDIGO (igual)
# =========================
def gradient_rect(draw, x1, y1, x2, y2, c1, c2):
    for i in range(y2 - y1):
        t = i / (y2 - y1)
        cor = (
            int(c1[0] * (1 - t) + c2[0] * t),
            int(c1[1] * (1 - t) + c2[1] * t),
            int(c1[2] * (1 - t) + c2[2] * t),
        )
        draw.line((x1, y1 + i, x2, y1 + i), fill=cor)

def criar_base_pvc():
    fundo = Image.new("RGB", (W + 50, H + 50), (240, 240, 240))
    cartao = Image.new("RGBA", (W, H), BRANCO)
    fundo.paste(cartao, (25, 25))
    return fundo

def aplicar_mascara(img, radius=55):
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W, H), radius=radius, fill=255)
    img.putalpha(mask)
    return img

def gerar_qrcode(link):
    return qrcode.make(link).resize((320, 320))

def gerar_html_aluno(matricula):
    with open(f"alunos/{matricula}.html", "w") as f:
        f.write(f"<img src='{matricula}_frente.png'><img src='{matricula}_verso.png'>")

def atualizar_index(matricula):
    with open("index.html", "a") as f:
        f.write(f"<p><a href='alunos/{matricula}.html'>{matricula}</a></p>")

def enviar_para_github(matricula):
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", matricula])
    subprocess.run(["git", "push"])

def gerar_frente(nome, matricula, curso, turno, email, foto):
    img = criar_base_pvc()
    cartao = Image.new("RGBA", (W, H), BRANCO)

    foto = foto.resize((290, 300))
    cartao.paste(foto, (70, 220))

    draw = ImageDraw.Draw(cartao)
    draw.text((410, 220), nome, fill=PRETO, font=f_texto)

    img.paste(cartao, (25, 25))
    img.save(f"alunos/{matricula}_frente.png")

def gerar_verso(matricula):
    img = criar_base_pvc()
    cartao = Image.new("RGBA", (W, H), BRANCO)

    link = f"https://{USUARIO_GITHUB}.github.io/{REPO_GITHUB}/alunos/{matricula}.html"
    qr = gerar_qrcode(link)

    cartao.paste(qr, (350, 200))
    img.paste(cartao, (25, 25))
    img.save(f"alunos/{matricula}_verso.png")

# =========================
# MAIN
# =========================
def main():

    nome = input("Nome: ")
    matricula = input("Matrícula: ")
    curso = input("Curso: ")
    turno = input("Turno: ")
    email = input("Email: ")

    foto_path = f"fotos/{matricula}.png"

    capturar_foto(foto_path)

    # 🔥 ESPERA A FOTO EXISTIR
    if not esperar_foto(foto_path):
        print("❌ Foto não encontrada a tempo")
        return

    foto = Image.open(foto_path).convert("RGBA")

    gerar_frente(nome, matricula, curso, turno, email, foto)
    gerar_verso(matricula)
    gerar_html_aluno(matricula)
    atualizar_index(matricula)
    enviar_para_github(matricula)

    print("✅ PRONTO!")

if __name__ == "__main__":
    main()