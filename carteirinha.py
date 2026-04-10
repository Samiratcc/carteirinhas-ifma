from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os
import subprocess
import cv2
import time

# =========================
# CONFIGURAÇÕES
# =========================
USUARIO_GITHUB = "samiratcc"
REPO_GITHUB = "carteirinhas-ifma"

W, H = 1016, 638

VERDE1 = (0, 130, 60)
VERDE2 = (0, 95, 45)
VERMELHO = (210, 35, 50)

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

# =========================
# CAMINHOS
# =========================
BASE_DIR = os.path.dirname(__file__)
PASTA_ALUNOS = os.path.join(BASE_DIR, "alunos")
PASTA_FOTOS = os.path.join(BASE_DIR, "fotos")

os.makedirs(PASTA_ALUNOS, exist_ok=True)
os.makedirs(PASTA_FOTOS, exist_ok=True)

# =========================
# 📷 CAPTURA FOTO (CORRIGIDO DE VERDADE)
# =========================
def capturar_foto(caminho_saida):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Não conseguiu abrir a câmera")
        return False

    print("📷 Pressione ESPAÇO para tirar foto")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("❌ Erro ao capturar frame")
            break

        cv2.imshow("Camera", frame)
        tecla = cv2.waitKey(1)

        if tecla == 32:  # espaço
            print("📸 Salvando foto...")

            # 🔥 GARANTE QUE O CAMINHO EXISTE
            pasta = os.path.dirname(caminho_saida)
            os.makedirs(pasta, exist_ok=True)

            sucesso = cv2.imwrite(caminho_saida, frame)

            if sucesso:
                print("✅ Foto salva com sucesso!")
            else:
                print("❌ Falha ao salvar")
                return False

            break

        elif tecla == 27:
            print("❌ Cancelado")
            return False

    cap.release()
    cv2.destroyAllWindows()
    return True


# =========================
# ESPERAR FOTO
# =========================
def esperar_foto(caminho):
    for _ in range(10):
        if os.path.exists(caminho):
            return True
        time.sleep(0.5)
    return False


# =========================
# BASE SIMPLES
# =========================
def criar_base():
    return Image.new("RGB", (W, H), BRANCO)


# =========================
# QR CODE
# =========================
def gerar_qr(link):
    return qrcode.make(link).resize((250, 250))


# =========================
# GERAR FRENTE
# =========================
def gerar_frente(nome, matricula, curso, turno, email, foto):
    img = criar_base()
    draw = ImageDraw.Draw(img)

    foto = foto.resize((300, 300))
    img.paste(foto, (50, 150))

    draw.text((400, 150), f"Nome: {nome}", fill=PRETO)
    draw.text((400, 200), f"Matrícula: {matricula}", fill=PRETO)
    draw.text((400, 250), f"Curso: {curso}", fill=PRETO)
    draw.text((400, 300), f"Turno: {turno}", fill=PRETO)
    draw.text((400, 350), f"Email: {email}", fill=PRETO)

    img.save(os.path.join(PASTA_ALUNOS, f"{matricula}_frente.png"))


# =========================
# GERAR VERSO
# =========================
def gerar_verso(matricula):
    img = criar_base()

    link = f"https://{USUARIO_GITHUB}.github.io/{REPO_GITHUB}/alunos/{matricula}.html"
    qr = gerar_qr(link)

    img.paste(qr, (350, 200))
    img.save(os.path.join(PASTA_ALUNOS, f"{matricula}_verso.png"))


# =========================
# HTML
# =========================
def gerar_html(matricula):
    caminho = os.path.join(PASTA_ALUNOS, f"{matricula}.html")

    html = f"""
    <h1>Carteirinha</h1>
    <img src="{matricula}_frente.png"><br>
    <img src="{matricula}_verso.png">
    """

    with open(caminho, "w") as f:
        f.write(html)


# =========================
# GITHUB
# =========================
def enviar_para_github(matricula):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"{matricula}"], check=True)
        subprocess.run(["git", "push"], check=True)
    except Exception as e:
        print("⚠ Erro no git:", e)


# =========================
# MAIN
# =========================
def main():
    print("\n===== CARTEIRINHA =====\n")

    nome = input("Nome: ")
    matricula = input("Matrícula: ")
    curso = input("Curso: ")
    turno = input("Turno: ")
    email = input("Email: ")

    caminho_foto = os.path.join(PASTA_FOTOS, f"{matricula}.png")

    # 🔥 CAPTURA
    if not capturar_foto(caminho_foto):
        print("❌ Falha na captura")
        return

    # 🔥 ESPERA FOTO EXISTIR
    if not esperar_foto(caminho_foto):
        print("❌ Foto não apareceu a tempo")
        return

    # 🔥 ABRE FOTO
    foto = Image.open(caminho_foto).convert("RGB")

    gerar_frente(nome, matricula, curso, turno, email, foto)
    gerar_verso(matricula)
    gerar_html(matricula)
    enviar_para_github(matricula)

    print("✅ TUDO PRONTO!")


if __name__ == "__main__":
    main()