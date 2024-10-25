import cv2
import os
import numpy as np
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import wave
import matplotlib.pyplot as plt

# Initialize text-to-speech engine
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Show welcome message in a Tkinter window
def show_yuna_ai_message():
    root = tk.Tk()
    root.title("Yuna AI")
    root.geometry("300x150")

    message = "Selamat datang! Akses diterima."
    messagebox.showinfo("Yuna AI", message)

    root.destroy()

# Listen for voice command
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Silakan bicara...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language="id-ID")
        print(f"Perintah diterima: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Maaf, tidak dapat memahami audio.")
        return None
    except sr.RequestError:
        print("Kesalahan dalam menghubungi layanan pengenalan suara.")
        return None

# Record voice to a WAV file
def record_voice(filename):
    chunk = 1024  # Sample size
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1  # Single channel for microphone
    fs = 44100  # Record at 44.1 kHz
    seconds = 5  # Duration of recording

    print("Silakan berbicara setelah suara beep...")
    
    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format, channels=channels, rate=fs, output=True, input=True)
    stream.start_stream()

    # Play a beep sound
    beep = AudioSegment.sine(frequency=1000, duration=1000)  # 1-second beep
    play(beep)

    # Start recording
    frames = []
    for _ in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

    print(f"Suara telah direkam dan disimpan di {filename}.")

# Create waveform image from audio file
def create_waveform_image(audio_file, image_file):
    # Read the audio data
    wf = wave.open(audio_file, 'rb')
    sample_rate = wf.getframerate()
    n_samples = wf.getnframes()
    t_audio = n_samples / sample_rate  # Total time of audio
    audio_data = wf.readframes(n_samples)
    wf.close()

    # Convert audio data to numpy array
    audio_data = np.frombuffer(audio_data, dtype=np.int16)

    # Create time axis
    time = np.linspace(0., t_audio, n_samples)

    # Plot the waveform
    plt.figure(figsize=(12, 4))
    plt.plot(time, audio_data)
    plt.title("Waveform")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid()

    # Save the waveform image
    plt.savefig(image_file)
    plt.close()

    print(f"Waveform image telah disimpan di {image_file}.")
    return image_file

# Register voice
def register_voice(name):
    filename = f"{name}_voice.wav"
    record_voice(filename)
    # Create waveform image after recording
    image_file = f"{name}_waveform.png"
    create_waveform_image(filename, image_file)
    print(f"Suara {name} telah terdaftar.")

# Register face
def register_face(name, nim):
    video_capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    images = []
    labels = []

    while True:
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            face_image = gray[y:y + h, x:x + w]
            face_image_resized = cv2.resize(face_image, (100, 100))
            images.append(face_image_resized)
            labels.append(name + "_" + nim)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("Video", frame)

        if len(images) >= 30:  # Capture 30 images
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if images:
        images = np.array(images)
        np.save(f"{name}_{nim}_faces.npy", images)
        np.save(f"{name}_{nim}_labels.npy", labels)
        print(f"Wajah {name} dengan NIM {nim} telah terdaftar.")
        speak(f"Wajah terdaftar untuk {name}")

    video_capture.release()
    cv2.destroyAllWindows()

# Verify face
def verify_face(name, nim):
    encoding_path = f"{name}_{nim}_faces.npy"
    labels_path = f"{name}_{nim}_labels.npy"

    if not os.path.exists(encoding_path) or not os.path.exists(labels_path):
        print("Tidak ada wajah terdaftar sebelumnya. Silakan daftar terlebih dahulu.")
        return False

    images = np.load(encoding_path, allow_pickle=True)
    labels = np.load(labels_path, allow_pickle=True)

    try:
        model = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print("Modul face tidak tersedia. Pastikan Anda telah menginstal opencv-contrib-python.")
        return False

    model.train(images, np.array(range(len(labels))))

    video_capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            face_image = gray[y:y + h, x:x + w]
            label, confidence = model.predict(face_image)

            if confidence < 100:  # Threshold bisa disesuaikan
                print("Wajah terverifikasi. Selamat datang!")
                speak("Wajah terverifikasi. Selamat datang!")

                # Listen for the command to show the Yuna AI message
                command = listen_for_command()
                if command == "tampilkan pesan yuna ai":
                    show_yuna_ai_message()

                video_capture.release()
                cv2.destroyAllWindows()
                return True
            else:
                print("Wajah tidak cocok. Akses ditolak.")
                speak("Wajah tidak cocok. Akses ditolak.")
                video_capture.release()
                cv2.destroyAllWindows()
                return False

        cv2.imshow("Verifikasi Wajah", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return False

# Main function to choose registration or login
def main():
    print("Pilih opsi:")
    print("1. Daftar")
    print("2. Login")
    choice = input("Masukkan pilihan (1/2): ")

    if choice == '1':
        name = input("Masukkan nama: ")
        nim = input("Masukkan NIM: ")
        print("Mendaftarkan wajah...")
        register_face(name, nim)

        print("Sekarang mendengarkan perintah untuk mendaftarkan suara...")
        while True:
            command = listen_for_command()
            if command == "daftar suara":
                register_voice(name)  # Register voice
                break  # Exit the loop after registering voice
    elif choice == '2':
        name = input("Masukkan nama: ")
        nim = input("Masukkan NIM: ")
        print("Melakukan verifikasi wajah...")
        verify_face(name, nim)
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
