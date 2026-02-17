from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os
import subprocess

# =========================
# CONFIGURAÇÕES DO SITE
# =========================
USUARIO_GITHUB = "samirattc"   # <-- TROQUE AQUI
REPO_GITHUB = "carteirinhas-ifma"

# =========================
# TAMANHO PADRÃO CARTEIRA
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

except Exception as e:
    print("⚠ ERRO ao carregar fontes:", e)
    f_titulo_frente = ImageFont.load_default()
    f_subtitulo_frente = ImageFont.load_default()
    f_label = ImageFont.load_default()
    f_texto = ImageFont.load_default()
    f_titulo_verso = ImageFont.load_default()
    f_subtitulo_verso = ImageFont.load_default()

# =========================
# FUNÇÃO: GRADIENTE
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
# BASE PVC COM SOMBRA
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

    brilho = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    db = ImageDraw.Draw(brilho)
    db.ellipse((-250, -250, W + 300, 320), fill=(255, 255, 255, 70))
    brilho = brilho.filter(ImageFilter.GaussianBlur(30))

    cartao = Image.alpha_composite(cartao, brilho)

    fundo.paste(cartao, (25, 25), cartao)
    return fundo

# =========================
# FUNÇÃO: APLICAR MÁSCARA ARREDONDADA
# =========================
def aplicar_mascara(img, radius=55):
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle((0, 0, W, H), radius=radius, fill=255)

    img.putalpha(mask)
    return img

# =========================
# FUNÇÃO: CARREGAR LOGO DO TOPO
# =========================
def carregar_logo():
    try:
        logo = Image.open(os.path.join(BASE_DIR, "logo_simbolo_if.jpeg")).convert("RGBA")
        logo = logo.resize((90, 110))
        return logo
    except Exception as e:
        print("⚠ Não foi possível carregar logo_simbolo_if.jpeg:", e)
        return None

# =========================
# FUNÇÃO: GERAR QR COM LOGO NO MEIO
# =========================
def gerar_qrcode_com_logo(dados, logo_path="ifma_logo.png"):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(dados)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    try:
        logo = Image.open(os.path.join(BASE_DIR, logo_path)).convert("RGBA")
    except:
        print("⚠ Logo ifma_logo.png não encontrada. QR será gerado sem logo.")
        return img_qr.resize((320, 320))

    largura_qr, altura_qr = img_qr.size
    tamanho_logo = largura_qr // 4

    logo = logo.resize((tamanho_logo, tamanho_logo), Image.LANCZOS)

    mask = Image.new("L", logo.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)

    fundo = Image.new("RGBA", (tamanho_logo + 20, tamanho_logo + 20), (255, 255, 255, 0))
    mask_fundo = Image.new("L", fundo.size, 0)
    draw_fundo = ImageDraw.Draw(mask_fundo)
    draw_fundo.ellipse((0, 0, fundo.size[0], fundo.size[1]), fill=255)

    fundo.paste((255, 255, 255, 255), (0, 0), mask=mask_fundo)
    fundo.paste(logo, (10, 10), mask=mask)

    pos = ((largura_qr - fundo.size[0]) // 2, (altura_qr - fundo.size[1]) // 2)
    img_qr.paste(fundo, pos, mask=fundo)

    return img_qr.resize((320, 320))

# =========================
# GERAR HTML DO ALUNO
# =========================
def gerar_html_aluno(matricula):
    html_path = os.path.join(PASTA_ALUNOS, f"{matricula}.html")

    html = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Carteirinha {matricula}</title>

  <style>
    body {{
      background:#f2f2f2;
      font-family: Arial;
      text-align:center;
      padding:20px;
    }}
    img {{
      width: 90%;
      max-width: 900px;
      margin: 20px;
      border-radius: 15px;
      box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
    }}
  </style>
</head>

<body>
  <h1>Carteirinha do Aluno</h1>
  <h2>Matrícula: {matricula}</h2>

  <img src="{matricula}_frente.png">
  <img src="{matricula}_verso.png">

</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML criado: alunos/{matricula}.html")

# =========================
# ATUALIZAR INDEX.HTML
# =========================
def atualizar_index(matricula):
    index_path = os.path.join(BASE_DIR, "index.html")

    if not os.path.exists(index_path):
        html_base = """<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Carteirinhas IFMA</title>
</head>

<body style="font-family: Arial; text-align:center; background:#f2f2f2; padding:40px;">
  <h1>📌 Carteirinhas IFMA</h1>
  <p>Lista de carteirinhas disponíveis:</p>

</body>
</html>
"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_base)

    with open(index_path, "r", encoding="utf-8") as f:
        conteudo = f.read()

    link = f'<p><a href="alunos/{matricula}.html">Carteirinha - {matricula}</a></p>'

    if link in conteudo:
        print("⚠ Esse aluno já está no index.html")
        return

    conteudo = conteudo.replace("</body>", f"{link}\n</body>")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print("✅ index.html atualizado!")

# =========================
# FUNÇÃO: GERAR FRENTE
# =========================
def gerar_frente(nome, matricula, curso, turno, email):
    img_final = criar_base_pvc().convert("RGBA")
    ox, oy = 25, 25

    cartao = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(cartao)

    gradient_rect(draw, 0, 155, W, 190, VERDE1, VERDE2)
    gradient_rect(draw, 0, H - 85, W, H - 55, VERDE2, VERDE1)
    draw.rectangle((0, H - 55, W, H), fill=VERMELHO)

    logo_if = carregar_logo()
    if logo_if:
        cartao.paste(logo_if, (90, 40), logo_if)

    draw.text((205, 45), "INSTITUTO FEDERAL", fill=(20, 20, 20), font=f_titulo_frente)
    draw.line((205, 95, 560, 95), fill=(30, 30, 30), width=2)
    draw.text((205, 105), "Maranhão", fill=VERDE2, font=f_subtitulo_frente)

    foto_x1, foto_y1 = 70, 220
    foto_x2, foto_y2 = 360, 520

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    ds.rounded_rectangle((foto_x1 + 6, foto_y1 + 8, foto_x2 + 8, foto_y2 + 10),
                         radius=28, fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    cartao = Image.alpha_composite(cartao, shadow)

    draw = ImageDraw.Draw(cartao)

    draw.rounded_rectangle((foto_x1 - 8, foto_y1 - 8, foto_x2 + 8, foto_y2 + 8),
                           radius=32, fill=(230, 230, 230))

    draw.rounded_rectangle((foto_x1, foto_y1, foto_x2, foto_y2),
                           radius=28, fill=CINZA_FUNDO)

    draw.text((foto_x1 + 105, foto_y1 + 150), "FOTO", fill=(160, 160, 160), font=f_label)

    def campo(label, valor, y):
        label_w = 190
        draw.rectangle((410, y, 410 + label_w, y + 50), fill=VERDE2)
        draw.text((425, y + 7), label, fill=BRANCO, font=f_label)
        draw.text((610, y + 12), valor, fill=PRETO, font=f_texto)
        draw.line((410, y + 55, 950, y + 55), fill=CINZA_LINHA, width=2)

    y0 = 210
    gap = 66

    campo("Nome:", nome, y0)
    campo("Matrícula:", matricula, y0 + gap)
    campo("Curso:", curso, y0 + gap * 2)
    campo("Turno:", turno, y0 + gap * 3)
    campo("E-mail:", email, y0 + gap * 4)

    cartao = aplicar_mascara(cartao, radius=55)
    img_final.paste(cartao, (ox, oy), cartao)

    nome_frente = os.path.join(PASTA_ALUNOS, f"{matricula}_frente.png")
    img_final.convert("RGB").save(nome_frente)
    print("🔥 Frente criada:", nome_frente)

# =========================
# FUNÇÃO: GERAR VERSO
# =========================
def gerar_verso(matricula):
    img_final = criar_base_pvc().convert("RGBA")
    ox, oy = 25, 25

    cartao = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(cartao)

    gradient_rect(draw, 0, 155, W, 190, VERDE1, VERDE2)
    gradient_rect(draw, 0, H - 85, W, H - 55, VERDE2, VERDE1)
    draw.rectangle((0, H - 55, W, H), fill=VERMELHO)

    logo_if = carregar_logo()
    if logo_if:
        cartao.paste(logo_if, (90, 40), logo_if)

    draw.text((205, 45), "INSTITUTO FEDERAL", fill=(20, 20, 20), font=f_titulo_verso)
    draw.line((205, 95, 560, 95), fill=(30, 30, 30), width=2)
    draw.text((205, 105), "Maranhão", fill=VERDE2, font=f_subtitulo_verso)

    # LINK REAL DO GITHUB PAGES
    link_site = f"https://{USUARIO_GITHUB}.github.io/{REPO_GITHUB}/alunos/{matricula}.html"

    qr_img = gerar_qrcode_com_logo(link_site, "ifma_logo.png")

    qr_x = (W - qr_img.width) // 2
    qr_y = 220

    shadow_qr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow_qr)
    ds.rounded_rectangle((qr_x + 8, qr_y + 10, qr_x + qr_img.width + 8, qr_y + qr_img.height + 10),
                         radius=20, fill=(0, 0, 0, 120))
    shadow_qr = shadow_qr.filter(ImageFilter.GaussianBlur(12))
    cartao = Image.alpha_composite(cartao, shadow_qr)

    draw = ImageDraw.Draw(cartao)

    draw.rounded_rectangle((qr_x - 18, qr_y - 18, qr_x + qr_img.width + 18, qr_y + qr_img.height + 18),
                           radius=25, fill=(255, 255, 255))

    draw.rounded_rectangle((qr_x - 18, qr_y - 18, qr_x + qr_img.width + 18, qr_y + qr_img.height + 18),
                           radius=25, outline=(210, 210, 210), width=4)

    cartao.paste(qr_img, (qr_x, qr_y), qr_img)

    cartao = aplicar_mascara(cartao, radius=55)
    img_final.paste(cartao, (ox, oy), cartao)

    nome_verso = os.path.join(PASTA_ALUNOS, f"{matricula}_verso.png")
    img_final.convert("RGB").save(nome_verso)
    print("🔥 Verso criado:", nome_verso)

# =========================
# GIT PUSH AUTOMÁTICO
# =========================
def enviar_para_github(matricula):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Nova carteirinha {matricula}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Enviado para GitHub com sucesso!")
    except subprocess.CalledProcessError as e:
        print("❌ Erro no git:", e)

# =========================
# MAIN
# =========================
def main():
    print("\n===== GERADOR DE CARTEIRINHA IFMA =====\n")

    nome = input("Nome: ")
    matricula = input("Matrícula: ")
    curso = input("Curso: ")
    turno = input("Turno: ")
    email = input("Email: ")

    gerar_frente(nome, matricula, curso, turno, email)
    gerar_html_aluno(matricula)
    gerar_verso(matricula)
    atualizar_index(matricula)

    enviar_para_github(matricula)

    print("\n✅ Carteirinha criada e publicada automaticamente!")
    print(f"🌐 Link do aluno:")
    print(f"https://{USUARIO_GITHUB}.github.io/{REPO_GITHUB}/alunos/{matricula}.html")

if __name__ == "__main__":
    main()
