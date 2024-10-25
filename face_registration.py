import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')

def register_face(image_path, name, nim):
    # Capture gambar untuk pendaftaran wajah
    video_capture = cv2.VideoCapture(0)
    registered = False

    while not registered:
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Tandai area wajah
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_image = frame[y:y+h, x:x+w]
            
            # Simpan gambar wajah ke path yang ditentukan
            cv2.imwrite(image_path, face_image)
            print(f"Face registered for {name} with NIM {nim}")
            registered = True

        cv2.imshow('Register Face', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
