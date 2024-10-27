import cv2
import os
import numpy as np
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import threading
import time
import psutil  # Module tambahan untuk menutup aplikasi

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

# Fungsi untuk mencari aplikasi yang terinstal di direktori Program Files
def cari_aplikasi(nama_aplikasi):
    program_files = ["C:\\Program Files", "C:\\Program Files (x86)", "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"]
    for directory in program_files:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().startswith(nama_aplikasi.lower()) and file.endswith(".exe"):
                    return os.path.join(root, file)
    return None

# Fungsi untuk membuka aplikasi
def buka_aplikasi(nama_aplikasi):
    path = cari_aplikasi(nama_aplikasi)
    if path:
        os.startfile(path)
        print(f"{nama_aplikasi} berhasil dibuka.")
        bicara(f"Aplikasi {nama_aplikasi} berhasil dibuka.")
    else:
        print(f"{nama_aplikasi} tidak ditemukan.")
        bicara(f"Aplikasi {nama_aplikasi} tidak ditemukan.")

# Fungsi untuk menutup aplikasi
def tutup_aplikasi(nama_aplikasi):
    for proc in psutil.process_iter():
        if nama_aplikasi.lower() in proc.name().lower():
            proc.terminate()
            print(f"{nama_aplikasi} berhasil ditutup.")
            bicara(f"Aplikasi {nama_aplikasi} berhasil ditutup.")
            return
    print(f"{nama_aplikasi} tidak ditemukan.")
    bicara(f"Aplikasi {nama_aplikasi} tidak ditemukan.")

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

    # Simpan contoh suara untuk verifikasi suara
    bicara("Silakan sebutkan kata sandi suara untuk verifikasi.")
    suara_kata_sandi = dengar_perintah()
    if suara_kata_sandi:
        with open(f"{nama}_{nim}_suara.txt", "w") as file:
            file.write(suara_kata_sandi)
        print("Kata sandi suara telah disimpan.")
        bicara("Kata sandi suara telah disimpan.")
    else:
        print("Gagal merekam kata sandi suara.")

# Fungsi verifikasi suara
def verifikasi_suara(nama, nim):
    file_suara = f"{nama}_{nim}_suara.txt"
    if not os.path.exists(file_suara):
        print("Kata sandi suara tidak ditemukan.")
        return False

    with open(file_suara, "r") as file:
        kata_sandi_terdaftar = file.read().strip()

    print("Silakan sebutkan kata sandi suara.")
    bicara("Silakan sebutkan kata sandi suara.")
    suara = dengar_perintah()
    if suara == kata_sandi_terdaftar:
        print("Verifikasi suara berhasil.")
        return True
    else:
        print("Verifikasi suara gagal.")
        bicara("Verifikasi suara gagal.")
        return False

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
    elif pilihan == '2':
        nama = input("Masukkan nama: ")
        nim = input("Masukkan NIM: ")
        if verifikasi_wajah(nama, nim) and verifikasi_suara(nama, nim):
            print("Akses diterima.")
            tampilkan_pesan()
            while True:
                bicara("Apa perintah anda?")
                perintah = dengar_perintah()
                if perintah:
                    if perintah.startswith("buka"):
                        nama_aplikasi = perintah.replace("buka ", "")
                        buka_aplikasi(nama_aplikasi)
                    elif perintah.startswith("tutup program"):
                        print("Menutup program utama.")
                        bicara("Menutup program utama.")
                        break  # Mengakhiri loop utama dan menutup program
                    elif perintah.startswith("tutup"):
                        nama_aplikasi = perintah.replace("tutup ", "")
                        tutup_aplikasi(nama_aplikasi)
                    else:
                        print("Perintah tidak dikenali.")
                        bicara("Perintah tidak dikenali.")
        else:
            print("Akses ditolak.")
    else:
        print("Pilihan tidak valid.")

if __name__ == "__main__":
    utama()
