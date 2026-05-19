import face_recognition
import cv2
import os
import time
import sqlite3
from datetime import datetime

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect("presencas.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS presencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula TEXT,
    turma TEXT,
    ano TEXT,
    data TEXT,
    hora TEXT,
    status TEXT
)
""")

conn.commit()

# =========================
# CARREGAR FOTOS DOS ALUNOS
# =========================
pasta_fotos = "fotos"

rostos_conhecidos = []
nomes_conhecidos = []

for aluno in os.listdir(pasta_fotos):
    caminho_aluno = os.path.join(pasta_fotos, aluno)

    if os.path.isdir(caminho_aluno):
        for foto in os.listdir(caminho_aluno):
            caminho_foto = os.path.join(caminho_aluno, foto)

            try:
                imagem = face_recognition.load_image_file(caminho_foto)
                encoding = face_recognition.face_encodings(imagem)[0]

                rostos_conhecidos.append(encoding)
                nomes_conhecidos.append(aluno)

            except:
                pass

# =========================
# QR CODE
# =========================
qr_detector = cv2.QRCodeDetector()

# =========================
# CÂMERA
# =========================
cap = cv2.VideoCapture(0)

ultimo_tempo = 0
intervalo = 2

ultimo_nome = "Desconhecido"
ultimo_qr = None

ultimo_registro = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    agora = time.time()

    # =========================
    # LEITURA A CADA 2s
    # =========================
    if agora - ultimo_tempo > intervalo:

        # --- ROSTO ---
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        ultimo_nome = "Desconhecido"

        for face_encoding in encodings:
            matches = face_recognition.compare_faces(rostos_conhecidos, face_encoding)

            if True in matches:
                index = matches.index(True)
                ultimo_nome = nomes_conhecidos[index]

        # --- QR CODE ---
        data, bbox, _ = qr_detector.detectAndDecode(frame)

        if data:
            # extrai matrícula do link
            # exemplo: .../alunos/20241aua0003.html
            try:
                ultimo_qr = data.split("/")[-1].replace(".html", "")
            except:
                ultimo_qr = None

        ultimo_tempo = agora

    # =========================
    # VALIDAÇÃO
    # =========================
    cor = (0, 0, 255)

    if ultimo_nome != "Desconhecido" and ultimo_qr:

        if ultimo_nome == ultimo_qr:
            cor = (0, 255, 0)

            agora_data = datetime.now().strftime("%d/%m/%Y")
            agora_hora = datetime.now().strftime("%H:%M:%S")

            # verifica se já registrou hoje
            cursor.execute("""
            SELECT * FROM presencas
            WHERE matricula = ? AND data = ?
            """, (ultimo_nome, agora_data))

            registro = cursor.fetchone()

            # só salva se NÃO existir
            if registro is None:

                agora_timestamp = time.time()

                # trava anti-duplicação
                if (
                    ultimo_nome not in ultimo_registro
                    or agora_timestamp - ultimo_registro[ultimo_nome] > 10
                ):
                    
                    # =========================
                    # DESCOBRIR TURMA
                    # =========================
                    turma = "DESCONHECIDA"

                    if "AUA" in ultimo_nome:
                        turma = "Automação"

                    elif "ALA" in ultimo_nome:
                        turma = "Alimentos"

                    elif "ELA" in ultimo_nome:
                        turma = "Eletromecânica"

                    elif "MAA" in ultimo_nome:
                        turma = "Meio Ambiente"

                    elif "INF" in ultimo_nome:
                        turma = "Informática"

                    elif "QUI" in ultimo_nome:
                        turma = "Química"

                    elif "MAT" in ultimo_nome:
                        turma = "Matemática"

                    elif "BIO" in ultimo_nome:
                        turma = "Biologia"

                    # =========================
                    # DESCOBRIR ANO
                    # =========================
                    ano = ultimo_nome[:4]

                    cursor.execute("""
                    INSERT INTO presencas (matricula, turma, ano, data, hora, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        ultimo_nome,
                        turma,
                        ano,
                        agora_data,
                        agora_hora,
                        "PRESENTE"
                    ))

                    conn.commit()
                    print("SALVOU AGORA")

                    ultimo_registro[ultimo_nome] = agora_timestamp

                    print("✅ Presença registrada!")

        else:
            cor = (0, 0, 255)

    # =========================
    # QUADRADO NO ROSTO
    # =========================
    for (top, right, bottom, left) in faces:

        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            cor,
            3
        )
    # =========================
    # DESENHO
    # =========================
    cv2.putText(frame, f"Rosto: {ultimo_nome}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)

    cv2.putText(frame, f"QR: {ultimo_qr}", (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)

    cv2.imshow("Validacao IFMA", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()