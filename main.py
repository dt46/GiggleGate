import cv2
import os
import numpy as np
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyaudio
import wave
import winsound
import time
import pyautogui
import webbrowser

# Fungsi TTS (Text-to-Speech) dalam bahasa Indonesia
def bicara(teks):
    mesin = pyttsx3.init()
    mesin.setProperty('rate', 150)
    mesin.setProperty('volume', 1)
    suara = mesin.getProperty('voices')
    mesin.setProperty('voice', suara[0].id)
    mesin.say(teks)
    mesin.runAndWait()

# Fungsi menampilkan pesan dengan Tkinter
def tampilkan_pesan():
    root = tk.Tk()
    root.title("Yuna AI")
    root.geometry("300x150")
    messagebox.showinfo("Yuna AI", "Selamat datang! Akses diterima.")
    root.destroy()

# Fungsi untuk mendengarkan perintah suara
def dengar_perintah():
    recognizer = sr.Recognizer()
    with sr.Microphone() as sumber:
        print("Silakan bicara...")
        audio = recognizer.listen(sumber)
    try:
        perintah = recognizer.recognize_google(audio, language="id-ID")
        print(f"Perintah: {perintah}")
        return perintah.lower()
    except sr.UnknownValueError:
        print("Tidak mengerti perintah.")
        return None
    except sr.RequestError:
        print("Gagal terhubung ke layanan pengenalan suara.")
        return None

# Fungsi merekam suara dan menyimpan sebagai WAV
def rekam_suara(nama_file):
    chunk = 1024
    format_sampel = pyaudio.paInt16
    saluran = 1
    frekuensi = 44100
    detik = 5

    print("Berbicara setelah bunyi beep...")
    winsound.Beep(1000, 1000)

    p = pyaudio.PyAudio()
    stream = p.open(format=format_sampel, channels=saluran, rate=frekuensi, input=True)
    frames = [stream.read(chunk) for _ in range(0, int(frekuensi / chunk * detik))]

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(nama_file, 'wb') as wf:
        wf.setnchannels(saluran)
        wf.setsampwidth(p.get_sample_size(format_sampel))
        wf.setframerate(frekuensi)
        wf.writeframes(b''.join(frames))

    print(f"Suara disimpan di {nama_file}.")

# Fungsi untuk mendaftarkan wajah menggunakan kamera
def daftar_wajah(nama, nim):
    video_capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    wajah_terdaftar = []
    print("Arahkan wajah Anda ke kamera.")

    while len(wajah_terdaftar) < 30:
        ret, frame = video_capture.read()
        abu_abu = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        wajah = face_cascade.detectMultiScale(abu_abu, 1.1, 5)

        for (x, y, w, h) in wajah:
            wajah_terpotong = abu_abu[y:y+h, x:x+w]
            wajah_terdaftar.append(cv2.resize(wajah_terpotong, (100, 100)))
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Pendaftaran Wajah", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    np.save(f"{nama}_{nim}_wajah.npy", wajah_terdaftar)
    video_capture.release()
    cv2.destroyAllWindows()
    bicara("Wajah telah terdaftar.")

# Fungsi untuk membuka aplikasi berdasarkan nama perintah
def buka_aplikasi(nama_aplikasi):
    aplikasi = {
        "whatsapp": "C:\\Program Files\\WindowsApps\\5319275A.WhatsAppDesktop_2.2440.9.0_x64__cv1g1gvanyjgm\\WhatsApp.exe",
        "visual studio code": "C:\\Users\\M. Galuh Gumelar\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    }

    if nama_aplikasi in aplikasi:
        try:
            os.startfile(aplikasi[nama_aplikasi])
            print(f"{nama_aplikasi} berhasil dibuka.")
        except FileNotFoundError:
            print(f"{nama_aplikasi} tidak ditemukan.")
    else:
        print(f"Aplikasi {nama_aplikasi} belum terdaftar.")

# Fungsi verifikasi wajah
def verifikasi_wajah(nama, nim):
    file_wajah = f"{nama}_{nim}_wajah.npy"
    if not os.path.exists(file_wajah):
        print("Wajah belum terdaftar.")
        return False

    wajah_terdaftar = np.load(file_wajah, allow_pickle=True)
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(wajah_terdaftar, np.arange(len(wajah_terdaftar)))

    video_capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = video_capture.read()
        abu_abu = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        wajah = face_cascade.detectMultiScale(abu_abu, 1.1, 5)

        for (x, y, w, h) in wajah:
            wajah_terpotong = abu_abu[y:y+h, x:x+w]
            label, kepercayaan = model.predict(wajah_terpotong)

            if kepercayaan < 100:
                print("Wajah terverifikasi.")
                bicara("Wajah terverifikasi. Aplikasi apa yang ingin Anda buka?")
                tampilkan_pesan()
                
                # Dengarkan perintah untuk membuka aplikasi
                perintah = dengar_perintah()
                if perintah:
                    buka_aplikasi(perintah)
                return True
            else:
                print("Wajah tidak dikenali.")
                bicara("Wajah tidak dikenali.")
                return False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return False

# Fungsi utama untuk Daftar atau Login
def utama():
    print("Pilih opsi:")
    print("1. Daftar")
    print("2. Login")
    pilihan = input("Masukkan pilihan (1/2): ")

    if pilihan == '1':
        nama = input("Masukkan nama: ")
        nim = input("Masukkan NIM: ")
        daftar_wajah(nama, nim)
        rekam_suara(f"{nama}_suara.wav")
    elif pilihan == '2':
        nama = input("Masukkan nama: ")
        nim = input("Masukkan NIM: ")
        if verifikasi_wajah(nama, nim):
            print("Akses diterima.")
        else:
            print("Akses ditolak.")
    else:
        print("Pilihan tidak valid.")

if __name__ == "__main__":
    utama()
