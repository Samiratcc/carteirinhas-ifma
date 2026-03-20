def capturar_foto(matricula):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Câmera não abriu")
        return None

    print("📷 Pressione ESPAÇO para tirar foto")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Erro ao capturar frame")
            continue

        cv2.imshow("Camera", frame)
        tecla = cv2.waitKey(1)

        if tecla == 32:  # espaço
            nome_arquivo = f"{matricula}.png"
            caminho = os.path.join(PASTA_FOTOS, nome_arquivo)

            # 🔥 GARANTE QUE A PASTA EXISTE
            os.makedirs(PASTA_FOTOS, exist_ok=True)

            # 🔥 TENTA SALVAR
            sucesso = cv2.imwrite(caminho, frame)

            if not sucesso:
                print("❌ OpenCV NÃO conseguiu salvar a imagem!")
                return None

            print(f"📁 Tentando salvar em: {caminho}")

            # 🔥 ESPERA ATÉ EXISTIR
            tentativas = 0
            while not os.path.exists(caminho) and tentativas < 20:
                time.sleep(0.2)
                tentativas += 1

            if os.path.exists(caminho):
                print("✅ Foto salva com sucesso!")
                break
            else:
                print("❌ Arquivo NÃO apareceu na pasta!")
                return None

    cap.release()
    cv2.destroyAllWindows()

    return caminho