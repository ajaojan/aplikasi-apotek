import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from koneksi import buat_koneksi

class WindowLogin:
    def __init__(self, root, callback_sukses):
        self.root = root
        self.root.title("Apotek Sehat - Login System")
        
        # Bikin Fullscreen / maximized
        self.root.state("zoomed")  # Untuk Windows agar langsung fullscreen
        
        self.callback_sukses = callback_sukses

        # Warna Tema
        self.bg_left = "#ffffff"
        self.bg_right = "#eef2f7"
        self.text_dark = "#1e293b"
        self.accent_color = "#3b82f6"

        # --- CONTAINER UTAMA (Split Screen 2 Kolom) ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # 1. SISI KIRI (Form Login)
        self.left_frame = tk.Frame(self.main_frame, bg=self.bg_left, padx=80, pady=60)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Konten di dalam Sisi Kiri (dibuat di tengah secara vertikal)
        content_box = tk.Frame(self.left_frame, bg=self.bg_left)
        content_box.place(relx=0.5, rely=0.5, anchor="center")

        # Judul & Sambutan
        tk.Label(content_box, text="Hello there !", fg=self.text_dark, bg=self.bg_left, font=("Helvetica", 28, "bold")).pack(anchor="w", pady=(0, 5))
        tk.Label(content_box, text="Silakan masuk ke akun sistem apotek Anda.", fg="#64748b", bg=self.bg_left, font=("Arial", 11)).pack(anchor="w", pady=(0, 30))

        # Input Username
        tk.Label(content_box, text="User name", fg="#475569", bg=self.bg_left, font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.ent_username = ttk.Entry(content_box, width=32, font=("Arial", 11))
        self.ent_username.pack(anchor="w", ipady=5, pady=(0, 20))

        # Input Password
        tk.Label(content_box, text="Password", fg="#475569", bg=self.bg_left, font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.ent_password = ttk.Entry(content_box, width=32, font=("Arial", 11), show="•")
        self.ent_password.pack(anchor="w", ipady=5, pady=(0, 25))

        # Tombol Login
        btn_login = tk.Button(content_box, text="LOG IN", bg=self.accent_color, fg="white", font=("Arial", 10, "bold"), bd=0, relief="flat", cursor="hand2", width=28, command=self.proses_login)
        btn_login.pack(anchor="w", ipady=10, pady=(0, 15))

        # Footer kecil di bawah form
        footer_lbl = tk.Label(content_box, text="New there ? Hubungi Administrator sistem", fg="#94a3b8", bg=self.bg_left, font=("Arial", 9))
        footer_lbl.pack(anchor="w", pady=(10, 0))

        # 2. SISI KANAN (Ilustrasi Pemandangan / Gambar Estetik)
        self.right_frame = tk.Frame(self.main_frame, bg=self.bg_right)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Kanvas atau Panel Dekorasi Pemandangan Estetik di Sisi Kanan
        self.create_scenery_background()

    def create_scenery_background(self):
        # Membuat ilustrasi pemandangan buatan / gradasi alam yang menenangkan di sisi kanan
        canvas = tk.Canvas(self.right_frame, bg="#dbeafe", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Bind event agar saat layar diubah ukurannya, latar belakang menyesuaikan
        canvas.bind("<Configure>", lambda event: self.draw_scenery(canvas, event.width, event.height))

    def draw_scenery(self, canvas, width, height):
        canvas.delete("all")
        
        # Gradasi Langit / Background Pemandangan
        canvas.create_rectangle(0, 0, width, height, fill="#e0f2fe", outline="")
        
        # Gunung / Perbukitan Belakang
        canvas.create_polygon(0, height, 0, height*0.6, width*0.3, height*0.35, width*0.6, height*0.55, width, height*0.4, width, height, fill="#cbd5e1", outline="")
        
        # Gunung / Perbukitan Depan
        canvas.create_polygon(0, height, 0, height*0.75, width*0.25, height*0.5, width*0.55, height*0.7, width*0.8, height*0.55, width, height*0.7, width, height, fill="#94a3b8", outline="")

        # Elemen Pohon / Hijau Pemandangan
        canvas.create_polygon(width*0.15, height, width*0.15, height*0.7, width*0.2, height, fill="#334155", outline="")
        canvas.create_polygon(width*0.22, height, width*0.22, height*0.65, width*0.27, height, fill="#1e293b", outline="")
        canvas.create_polygon(width*0.75, height, width*0.75, height*0.68, width*0.8, height, fill="#334155", outline="")

        # Teks Judul Estetik di Pemandangan
        canvas.create_text(width*0.5, height*0.2, text="APOTEK SEHAT DIGITAL", fill="#1e293b", font=("Helvetica", 20, "bold"))
        canvas.create_text(width*0.5, height*0.25, text="Sistem Manajemen Modern & Terpadu", fill="#475569", font=("Arial", 11))

    def proses_login(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username dan Password tidak boleh kosong!")
            return

        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()

                if user:
                    role = user['role']
                    messagebox.showinfo("Sukses", f"Login Berhasil! Selamat datang, {role}")
                    self.root.destroy()
                    self.callback_sukses(role)
                else:
                    messagebox.showerror("Gagal", "Username atau Password salah!")
            except Exception as e:
                messagebox.showerror("Database Error", f"Terjadi kesalahan: {e}")
            finally:
                cursor.close()
                conn.close()

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    WindowLogin(root, lambda r: print(f"Login sukses sebagai: {r}"))
    root.mainloop()