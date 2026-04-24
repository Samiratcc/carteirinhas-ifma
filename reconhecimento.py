import face_recognition
import cv2
import os

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

                print(f"✔ Rosto carregado: {aluno}")

            except:
                print(f"❌ Erro na foto: {caminho_foto}")

# =========================
# ABRIR CÂMERA
# =========================
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, faces)

    for (top, right, bottom, left), face_encoding in zip(faces, encodings):

        matches = face_recognition.compare_faces(rostos_conhecidos, face_encoding)
        nome = "Desconhecido"

        if True in matches:
            index = matches.index(True)
            nome = nomes_conhecidos[index]

        # desenhar caixa
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, nome, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Reconhecimento Facial", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()