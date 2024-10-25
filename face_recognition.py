import cv2
import face_recognition  # Pastikan sudah di-install

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')

def load_known_face(image_path):
    known_image = face_recognition.load_image_file(image_path)
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    return known_face_encoding

def recognize_face(known_face_encoding):
    video_capture = cv2.VideoCapture(0)
    authorized = False

    while not authorized:
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]  # Ubah BGR ke RGB

        # Dapatkan encoding wajah dari frame kamera
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            # Cek kecocokan dengan wajah yang terdaftar
            matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
            if True in matches:
                authorized = True
                break

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return authorized
