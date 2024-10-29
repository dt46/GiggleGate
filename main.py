import cv2
import os
import numpy as np
import pyttsx3
import tkinter as tk
from tkinter import messagebox, simpledialog
import speech_recognition as sr
import psutil

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
    root.withdraw()
    messagebox.showinfo("GiggleGate", "Selamat datang! Akses diterima.")
    root.destroy()

# Fungsi meminta input menggunakan Tkinter
def input_gui(prompt):
    root = tk.Tk()
    root.withdraw()  # Menyembunyikan jendela utama
    return simpledialog.askstring("Input", prompt, parent=root)

# Fungsi mendengarkan perintah suara
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

# Fungsi mencari aplikasi
def cari_aplikasi(nama_aplikasi):
    program_files = ["C:\\Program Files", "C:\\Program Files (x86)", "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"]
    for directory in program_files:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().startswith(nama_aplikasi.lower()) and file.endswith(".exe"):
                    return os.path.join(root, file)
    return None

# Fungsi membuka aplikasi
def buka_aplikasi(nama_aplikasi):
    path = cari_aplikasi(nama_aplikasi)
    if path:
        os.startfile(path)
        bicara(f"Aplikasi {nama_aplikasi} berhasil dibuka.")
    else:
        bicara(f"Aplikasi {nama_aplikasi} tidak ditemukan.")

# Fungsi menutup aplikasi
def tutup_aplikasi(nama_aplikasi):
    for proc in psutil.process_iter():
        if nama_aplikasi.lower() in proc.name().lower():
            proc.terminate()
            bicara(f"Aplikasi {nama_aplikasi} berhasil ditutup.")
            return
    bicara(f"Aplikasi {nama_aplikasi} tidak ditemukan.")

# Fungsi pendaftaran wajah
def daftar_wajah(nama, nim):
    video_capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    wajah_terdaftar = []

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

    bicara("Silakan sebutkan kata sandi suara untuk verifikasi.")
    suara_kata_sandi = dengar_perintah()
    if suara_kata_sandi:
        with open(f"{nama}_{nim}_suara.txt", "w") as file:
            file.write(suara_kata_sandi)
        bicara("Kata sandi suara telah disimpan.")
    else:
        bicara("Gagal merekam kata sandi suara.")

# Fungsi verifikasi suara
def verifikasi_suara(nama, nim):
    file_suara = f"{nama}_{nim}_suara.txt"
    if not os.path.exists(file_suara):
        bicara("Kata sandi suara tidak ditemukan.")
        return False

    with open(file_suara, "r") as file:
        kata_sandi_terdaftar = file.read().strip()

    bicara("Silakan sebutkan kata sandi suara.")
    suara = dengar_perintah()
    return suara == kata_sandi_terdaftar

# Fungsi verifikasi wajah
def verifikasi_wajah(nama, nim):
    file_wajah = f"{nama}_{nim}_wajah.npy"
    if not os.path.exists(file_wajah):
        bicara("Wajah belum terdaftar.")
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
                video_capture.release()
                cv2.destroyAllWindows()
                return True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return False

# Fungsi utama untuk daftar atau login
def utama():
    pilihan = input_gui("Pilih opsi: 1. Daftar, 2. Login")
    if pilihan == '1':
        nama = input_gui("Masukkan nama:")
        nim = input_gui("Masukkan NIM:")
        daftar_wajah(nama, nim)
    elif pilihan == '2':
        nama = input_gui("Masukkan nama:")
        nim = input_gui("Masukkan NIM:")
        if verifikasi_wajah(nama, nim) and verifikasi_suara(nama, nim):
            tampilkan_pesan()
            
            # Tambahkan logika untuk membuka dan menutup aplikasi dengan suara
            while True:
                bicara("Silakan sebutkan perintah:")
                perintah = dengar_perintah()
                if perintah is None:
                    bicara("Saya tidak mengerti. Silakan coba lagi.")
                    continue

                if 'exit' in perintah:
                    bicara("Keluar dari program.")
                    break
                
                if 'buka' in perintah:
                    nama_aplikasi = perintah.replace('buka', '').strip()
                    buka_aplikasi(nama_aplikasi)
                elif 'tutup' in perintah:
                    nama_aplikasi = perintah.replace('tutup', '').strip()
                    tutup_aplikasi(nama_aplikasi)
                else:
                    bicara("Perintah tidak valid. Silakan coba lagi.")
        else:
            bicara("Akses ditolak.")
    else:
        bicara("Pilihan tidak valid.")

if __name__ == "__main__":
    utama()
