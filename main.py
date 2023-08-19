import cv2
import mediapipe as mp
import numpy as np
import time
import pygame
from pynput.keyboard import Key, Controller
import tkinter as tk

# Inicializando o módulo de desenho e mãos do MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_face_detection = mp.solutions.face_detection

# Inicialize o detector de rosto
face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.1)

#Boas Vindas
pygame.mixer.init()
sound = pygame.mixer.Sound('tutorial/sistemas.mp3')

#Obtendo a resolução da Tela (se quiser a tela inteira)
#root = tk.Tk()
#screen_width = root.winfo_screenwidth()
#screen_height = root.winfo_screenheight()



cap = cv2.VideoCapture(0) #Selecionar a WebCam
kb = Controller()


# Coordenadas iniciais da mão
x, y = 0, 0

positivo_detectado_direita = False
positivo_detectado_esquerda = False
start_time_direita = None
start_time_esquerda = None

cooldown_frames = 30  # Definir quantos quadros esperar antes de permitir que o som seja tocado novamente
cooldown_counter = 0  # Contador de quadros desde a última vez que o som foi tocado
sound_played = False  # Adicionado para garantir que o som seja tocado apenas uma vez

with mp_hands.Hands(min_detection_confidence=0.7, 
                    min_tracking_confidence=0.7) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignora se não tiver câmera.")
            continue

        #Imagem horizontalmente para uma exibição posterior de visualização de selfie
        image = cv2.flip(image, 1)
        #image = cv2.resize(image, (screen_width, screen_height)) #Resolução da Tela
        image = cv2.resize(image, None, fx=2, fy=2) #Tamanho da tela: dobro do default
        image_height, image_width, _ = image.shape
   
        # Converte BGR imagem para RGB após processamento
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Desenha os pontos nas mãos
        image.flags.writeable = True


        face_results = face_detector.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        num_faces = 0

        if face_results.detections:
            num_faces = len(face_results.detections)
            #print("Rosto detectado!")

            for detection in face_results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = image.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if num_faces > 1:
            cv2.putText(image, 'Certifique-se de que apenas um rosto esteja na camera.', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.imshow('MediaPipe Hands', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break
            continue


        if results.multi_hand_landmarks:

           

            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):


                # Detectando o gesto de "vitória" para o tutorial
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                
                index_finger_base = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
                middle_finger_base = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
                ring_finger_base = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
                pinky_base = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
                
                if (index_finger_tip.y < index_finger_base.y and 
                    middle_finger_tip.y < middle_finger_base.y and 
                    ring_finger_tip.y > ring_finger_base.y and 
                    pinky_tip.y > pinky_base.y and 
                    not sound_played and 
                    cooldown_counter == 0 and not pygame.mixer.get_busy()):
                    
                    sound.play()
                    sound_played = True  # Marque como verdadeiro após tocar o som
                    cooldown_counter = cooldown_frames #contagem frames
                
                elif cooldown_counter > 0:
                        cooldown_counter -= 1 #Decrementar o contador de cooldown
                   
                else: 
                    sound_played = False
                        
                 # Identificando qual mão foi detectada
                handness = results.multi_handedness[idx].classification[0].label

                # Adicionando o título ao retângulo
                title = handness

                # Verificando o gesto positivo
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                
                #Contador de mãos
                num_hands = len(results.multi_hand_landmarks)
               
                if num_hands > 1:
                    print('Uma das mãos apenas')
                    cv2.putText(image, 'Por favor, use apenas uma mao de cada vez.', 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 
                               2, cv2.LINE_AA)


                # Se a mão for a direita e o polegar estiver acima dos outros dedos, 
                # é um gesto positivo
                if (handness == 'Right' and 
                    thumb_tip.y < index_finger_tip.y and
                    thumb_tip.y < middle_finger_tip.y and
                    thumb_tip.y < ring_finger_tip.y and
                    thumb_tip.y < pinky_tip.y  and
                    num_hands == 1):

                    # Se este é o primeiro quadro no qual o gesto "positivo" é detectado, armazene o tempo atual e aciona a tecla direita
                    if (not positivo_detectado_direita and not
                        positivo_detectado_esquerda):

                        start_time_direita = time.time()
                        print('Começou o tempo')
                        kb.press(Key.right)
                        kb.release(Key.right)

                    positivo_detectado_direita = True
                    title = " Direita - Passar"
                    print('.')

                     # Se o gesto "positivo" tem sido mantido por mais de 1 segundo, exibir a mensagem
                    if (positivo_detectado_direita and 
                        start_time_direita is not 
                        None and time.time() - start_time_direita >= 1):

                        title = " - Abra a Palma"
                        print('Abra a Palma')

                else:
                    # Se o gesto "positivo" não está mais sendo detectado, 
                    # resete a variável de controle e o tempo de início
                    positivo_detectado_direita = False
                    start_time_direita = None

               

               
                if (handness == 'Left' and 
                    thumb_tip.y < index_finger_tip.y and 
                    thumb_tip.y < middle_finger_tip.y and 
                    thumb_tip.y < ring_finger_tip.y and 
                    thumb_tip.y < pinky_tip.y and 
                    num_hands == 1):

                    if (not positivo_detectado_esquerda and not 
                        positivo_detectado_direita): 

                        start_time_esquerda = time.time()
                        print('Começou o tempo')
                        kb.press(Key.left)
                        kb.release(Key.left)

                    title = "Esquerda - Voltar"
                    positivo_detectado_esquerda = True
                    print('.')

                    
                    if (positivo_detectado_esquerda and 
                        start_time_esquerda is not None and 
                        time.time() - start_time_esquerda >= 1):

                        title = "Abra a Palma"
                        print('Abre a palma') 
                   
                else:
                 
                    positivo_detectado_esquerda = False
                    start_time_esquerda = None

    
                # Atualiza as coordenadas da mão
                x_prev, y_prev = x, y
                x = int(thumb_tip.x * image_width)
                y = int(thumb_tip.y * image_height)

                # Desenhando um retângulo verde ao redor da mão
                landmarks = [[int(landmark.x * image_width), 
                            int(landmark.y * image_height)] for landmark in 
                            hand_landmarks.landmark]
                
                landmarks = np.array(landmarks)
                x_min, y_min = np.min(landmarks, axis=0)
                x_max, y_max = np.max(landmarks, axis=0)
                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), 
                              (0, 255, 0), 2)

                cv2.putText(image, title, (x_min, y_min-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, 
                            (0, 255, 0), 2)

                mp_drawing.draw_landmarks(image, hand_landmarks, 
                                          mp_hands.HAND_CONNECTIONS)

        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:#Tecla ESC
            break

cap.release()
