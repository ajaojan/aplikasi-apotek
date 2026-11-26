import tkinter as tk
from tkinter import messagebox, Toplevel
import ttkbootstrap as ttk
from ttkbootstrap import Style
from datetime import datetime
from login import WindowLogin
from koneksi import buat_koneksi

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AplikasiApotekDashboard:
    def __init__(self, root, role_user):
        self.root = root
        self.root.title(f"Apotek Sehat - Dashboard ({role_user})")
        self.root.geometry("1350x780")
        
        self.role_user = role_user
        self.style = Style(theme="darkly")
        
        self.bg_dark = "#12121c"
        self.card_dark = "#1c1c2e"
        self.sidebar_bg = "#161622"
        self.root.configure(bg=self.bg_dark)

        # --- LAYOUT UTAMA (Sidebar Kiri & Main Content Kanan) ---
        self.sidebar = tk.Frame(self.root, bg=self.sidebar_bg, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_container = tk.Frame(self.root, bg=self.bg_dark)
        self.main_container.pack(side="right", fill="both", expand=True)

        # --- SIDEBAR BRANDING & MENU ---
        brand_lbl = tk.Label(self.sidebar, text="💊 APOTEK SEHAT", fg="white", bg=self.sidebar_bg, font=("Helvetica", 14, "bold"))
        brand_lbl.pack(pady=25, anchor="w", padx=20)

        tk.Label(self.sidebar, text="MAIN MENU", fg="#6c6c8c", bg=self.sidebar_bg, font=("Arial", 8, "bold")).pack(anchor="w", padx=20, pady=(10, 5))

        nav_btn_style = {"font": ("Arial", 10, "bold"), "bg": self.sidebar_bg, "fg": "#a0a0c0", "activebackground": "#2a2a40", "activeforeground": "white", "bd": 0, "anchor": "w", "padx": 20, "pady": 10, "cursor": "hand2"}

        tk.Button(self.sidebar, text="🏠  Overview", command=self.tampilkan_menu_overview, **nav_btn_style).pack(fill="x")
        tk.Button(self.sidebar, text="📦  Data Obat", command=self.tampilkan_menu_obat, **nav_btn_style).pack(fill="x")
        tk.Button(self.sidebar, text="🗄️  Kotak & Rak", command=self.tampilkan_menu_rak, **nav_btn_style).pack(fill="x")
        tk.Button(self.sidebar, text="🛒  Kasir & Transaksi", command=self.tampilkan_menu_kasir, **nav_btn_style).pack(fill="x")
        tk.Button(self.sidebar, text="📊  Riwayat Transaksi", command=self.tampilkan_riwayat, **nav_btn_style).pack(fill="x")

        # Info User di Bawah Sidebar
        user_card = tk.Frame(self.sidebar, bg="#1f1f33", padx=15, pady=12)
        user_card.pack(side="bottom", fill="x", padx=15, pady=20)
        tk.Label(user_card, text=f"User: {self.role_user}", fg="white", bg="#1f1f33", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(user_card, text="Status: Online", fg="#00b894", bg="#1f1f33", font=("Arial", 8)).pack(anchor="w")

        # --- KONTEN UTAMA ---
        self.content_area = tk.Frame(self.main_container, bg=self.bg_dark)
        self.content_area.pack(fill="both", expand=True, padx=25, pady=20)

        self.tampilkan_menu_overview()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ==================== 0. MENU OVERVIEW (DASHBOARD STATS & GRAFIK) ====================
    def tampilkan_menu_overview(self):
        self.clear_content()

        # Header Title & Tombol Reset Grafik
        header_frame = tk.Frame(self.content_area, bg=self.bg_dark)
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="Dashboard Overview", fg="white", bg=self.bg_dark, font=("Helvetica", 18, "bold")).pack(side="left")
        ttk.Button(header_frame, text="🔄 Reset / Refresh Grafik", bootstyle="outline-info", command=self.tampilkan_menu_overview).pack(side="right")

        total_obat = 0
        total_terjual = 0
        total_expired = 0
        total_rak = 0
        
        nama_obat_list = []
        qty_list = []
        
        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM obat")
                res_obat = cursor.fetchone()
                total_obat = res_obat[0] if res_obat[0] else 0

                cursor.execute("SELECT SUM(qty) FROM detail_penjualan")
                res_terjual = cursor.fetchone()
                total_terjual = res_terjual[0] if res_terjual and res_terjual[0] else 0

                cursor.execute("SELECT COUNT(*) FROM obat WHERE tanggal_kedaluwarsa <= CURDATE()")
                res_exp = cursor.fetchone()
                total_expired = res_exp[0] if res_exp[0] else 0

                cursor.execute("SELECT COUNT(*) FROM rak")
                res_rak = cursor.fetchone()
                total_rak = res_rak[0] if res_rak[0] else 0

                cursor.execute("SELECT nama_obat, SUM(qty) as total_qty FROM detail_penjualan GROUP BY nama_obat ORDER BY total_qty DESC LIMIT 5")
                for row in cursor.fetchall():
                    nama_obat_list.append(row[0])
                    qty_list.append(row[1])
            except Exception as e:
                print("Error stats:", e)
            finally:
                cursor.close()
                conn.close()

        # Baris 1: 4 Kartu Statistik Ringkas
        stats_frame1 = tk.Frame(self.content_area, bg=self.bg_dark)
        stats_frame1.pack(fill="x", pady=5)

        def create_stat_card(parent, title, value, color):
            card = tk.Frame(parent, bg=self.card_dark, padx=12, pady=12, highlightbackground=color, highlightthickness=2)
            card.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(card, text=title, fg="#a0a0c0", bg=self.card_dark, font=("Arial", 9, "bold")).pack(anchor="w")
            tk.Label(card, text=str(value), fg="white", bg=self.card_dark, font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(5, 0))

        create_stat_card(stats_frame1, "Total Jenis Obat", total_obat, "#6c5ce7")
        create_stat_card(stats_frame1, "Total Obat Terjual", total_terjual, "#00b894")
        create_stat_card(stats_frame1, "Obat Kedaluwarsa", total_expired, "#ff7675")
        create_stat_card(stats_frame1, "Total Kotak & Rak", total_rak, "#0984e3")

        # Baris 2: Grafik Batang Statistik Penjualan Terbanyak
        chart_card = tk.Frame(self.content_area, bg=self.card_dark, padx=15, pady=15, highlightbackground="#3d3d5c", highlightthickness=1)
        chart_card.pack(fill="both", expand=True, pady=10)

        tk.Label(chart_card, text="📈 Grafik Statistik Penjualan Obat Terbanyak", fg="white", bg=self.card_dark, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))

        fig, ax = plt.subplots(figsize=(10, 3.2), dpi=100)
        fig.patch.set_facecolor('#1c1c2e')
        ax.set_facecolor('#1c1c2e')

        if nama_obat_list:
            colors = ['#6c5ce7', '#00b894', '#0984e3', '#fdcb6e', '#ff7675']
            bars = ax.bar(nama_obat_list, qty_list, color=colors[:len(nama_obat_list)], width=0.5)
            
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', color='white', fontweight='bold', fontsize=9)
        else:
            ax.text(0.5, 0.5, "Belum ada data transaksi penjualan", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, color='gray', fontsize=11)

        ax.spines['bottom'].set_color('#a0a0c0')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#a0a0c0')
        ax.tick_params(colors='white', labelsize=9)
        ax.yaxis.grid(True, linestyle='--', alpha=0.2, color='white')
        ax.set_axisbelow(True)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ==================== 1. MENU DATA OBAT ====================
    def tampilkan_menu_obat(self):
        self.clear_content()

        tk.Label(self.content_area, text="Manajemen Data Obat", fg="white", bg=self.bg_dark, font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(0, 15))

        form_card = tk.Frame(self.content_area, bg=self.card_dark, padx=20, pady=15)
        form_card.pack(fill="x", pady=5)

        lbl_style = {"fg": "#a0a0c0", "bg": self.card_dark, "font": ("Arial", 9, "bold")}
        
        tk.Label(form_card, text="NAMA OBAT", **lbl_style).grid(row=0, column=0, sticky="w", pady=5)
        self.ent_nama = ttk.Entry(form_card, width=25)
        self.ent_nama.grid(row=1, column=0, padx=(0, 15), pady=(0, 10))

        tk.Label(form_card, text="KATEGORI", **lbl_style).grid(row=0, column=1, sticky="w", pady=5)
        self.ent_kategori = ttk.Entry(form_card, width=25)
        self.ent_kategori.grid(row=1, column=1, padx=(0, 15), pady=(0, 10))

        tk.Label(form_card, text="HARGA JUAL (Rp)", **lbl_style).grid(row=0, column=2, sticky="w", pady=5)
        self.ent_harga = ttk.Entry(form_card, width=20)
        self.ent_harga.grid(row=1, column=2, padx=(0, 15), pady=(0, 10))

        tk.Label(form_card, text="STOK", **lbl_style).grid(row=2, column=0, sticky="w", pady=5)
        self.ent_stok = ttk.Entry(form_card, width=25)
        self.ent_stok.grid(row=3, column=0, padx=(0, 15), pady=(0, 5))

        tk.Label(form_card, text="ID RAK", **lbl_style).grid(row=2, column=1, sticky="w", pady=5)
        self.ent_id_rak = ttk.Entry(form_card, width=25)
        self.ent_id_rak.insert(0, "1")
        self.ent_id_rak.grid(row=3, column=1, padx=(0, 15), pady=(0, 5))

        tk.Label(form_card, text="TGL EXP (YYYY-MM-DD)", **lbl_style).grid(row=2, column=2, sticky="w", pady=5)
        self.ent_exp = ttk.Entry(form_card, width=20)
        self.ent_exp.grid(row=3, column=2, padx=(0, 15), pady=(0, 5))

        btn_box = tk.Frame(form_card, bg=self.card_dark)
        btn_box.grid(row=4, column=0, columnspan=3, sticky="w", pady=(15, 0))
        ttk.Button(btn_box, text="Simpan Obat", bootstyle="success", command=self.simpan_obat).pack(side="left", padx=(0, 10))
        ttk.Button(btn_box, text="Reset Form", bootstyle="secondary", command=self.reset_form_obat).pack(side="left")

        table_card = tk.Frame(self.content_area, bg=self.card_dark, padx=15, pady=15)
        table_card.pack(fill="both", expand=True, pady=15)

        columns = ("ID", "Nama Obat", "Kategori", "Harga Jual", "Stok", "ID Rak", "Kedaluwarsa")
        self.tree_obat = ttk.Treeview(table_card, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree_obat.heading(col, text=col)
            self.tree_obat.column(col, width=120, anchor="center")
        self.tree_obat.pack(fill="both", expand=True)
        self.load_data_obat()

    def load_data_obat(self):
        for item in self.tree_obat.get_children():
            self.tree_obat.delete(item)
        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id_obat, nama_obat, kategori, harga_jual, stok, id_rak, tanggal_kedaluwarsa FROM obat")
                for row in cursor.fetchall():
                    self.tree_obat.insert("", "end", values=row)
            except Exception as e:
                print("Error load obat:", e)
            finally:
                cursor.close()
                conn.close()

    def simpan_obat(self):
        nama = self.ent_nama.get()
        kategori = self.ent_kategori.get()
        harga = self.ent_harga.get()
        stok = self.ent_stok.get()
        id_rak = self.ent_id_rak.get()
        exp = self.ent_exp.get()

        if not nama or not harga or not stok:
            messagebox.showerror("Error", "Nama, Harga, dan Stok wajib diisi!")
            return

        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            try:
                query = "INSERT INTO obat (nama_obat, kategori, harga_jual, stok, id_rak, tanggal_kedaluwarsa) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (nama, kategori, harga, stok, id_rak if id_rak else 1, exp if exp else None))
                conn.commit()
                messagebox.showinfo("Sukses", "Data obat berhasil disimpan!")
                self.reset_form_obat()
                self.load_data_obat()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan: {e}")
            finally:
                cursor.close()
                conn.close()

    def reset_form_obat(self):
        self.ent_nama.delete(0, 'end')
        self.ent_kategori.delete(0, 'end')
        self.ent_harga.delete(0, 'end')
        self.ent_stok.delete(0, 'end')
        self.ent_id_rak.delete(0, 'end')
        self.ent_id_rak.insert(0, "1")
        self.ent_exp.delete(0, 'end')

    # ==================== 2. MENU KOTAK & RAK ====================
    def tampilkan_menu_rak(self):
        self.clear_content()

        tk.Label(self.content_area, text="Manajemen Kotak & Rak Penyimpanan", fg="white", bg=self.bg_dark, font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(0, 15))

        form_card = tk.Frame(self.content_area, bg=self.card_dark, padx=20, pady=15)
        form_card.pack(fill="x", pady=5)

        tk.Label(form_card, text="NAMA RAK", fg="#a0a0c0", bg=self.card_dark, font=("Arial", 9, "bold")).pack(side="left", padx=5)
        self.ent_nama_rak = ttk.Entry(form_card, width=22)
        self.ent_nama_rak.pack(side="left", padx=5)

        tk.Label(form_card, text="KETERANGAN", fg="#a0a0c0", bg=self.card_dark, font=("Arial", 9, "bold")).pack(side="left", padx=5)
        self.ent_ket = ttk.Entry(form_card, width=28)
        self.ent_ket.pack(side="left", padx=5)

        ttk.Button(form_card, text="Simpan Rak", bootstyle="success", command=self.simpan_rak).pack(side="left", padx=15)

        self.grid_rak_frame = tk.Frame(self.content_area, bg=self.card_dark, padx=20, pady=20)
        self.grid_rak_frame.pack(fill="both", expand=True, pady=15)

        self.load_grid_rak()

    def load_grid_rak(self):
        for widget in self.grid_rak_frame.winfo_children():
            widget.destroy()

        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM rak")
                rak_list = cursor.fetchall()
                
                if not rak_list:
                    cursor.execute("INSERT INTO rak (id_rak, nama_rak, keterangan) VALUES (1, 'Rak A-1', 'Zona Obat Bebas'), (2, 'Rak B-2', 'Zona Antibiotik')")
                    conn.commit()
                    cursor.execute("SELECT * FROM rak")
                    rak_list = cursor.fetchall()

                row_idx, col_idx = 0, 0
                for rak in rak_list:
                    card = tk.Frame(self.grid_rak_frame, bg="#26263e", padx=15, pady=15, highlightbackground="#3d3d5c", highlightthickness=1)
                    card.grid(row=row_idx, column=col_idx, padx=15, pady=15, sticky="nsew")

                    tk.Label(card, text=f"📦  {rak['nama_rak']}", fg="white", bg="#26263e", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=2)
                    tk.Label(card, text=f"Zona: {rak['keterangan']}", fg="#a0a0c0", bg="#26263e", font=("Arial", 9)).pack(anchor="w", pady=2)

                    ttk.Button(card, text="Masuk Kotak ➔", bootstyle="info-outline", command=lambda r=rak: self.buka_detail_rak(r)).pack(anchor="e", pady=(10, 0))

                    col_idx += 1
                    if col_idx > 2:
                        col_idx = 0
                        row_idx += 1

            except Exception as e:
                print("Error load rak:", e)
            finally:
                cursor.close()
                conn.close()

    def simpan_rak(self):
        nama = self.ent_nama_rak.get().strip()
        ket = self.ent_ket.get().strip()

        if not nama:
            messagebox.showerror("Error", "Nama rak wajib diisi!")
            return

        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO rak (nama_rak, keterangan) VALUES (%s, %s)", (nama, ket))
                conn.commit()
                messagebox.showinfo("Sukses", f"Rak '{nama}' berhasil ditambahkan!")
                self.ent_nama_rak.delete(0, 'end')
                self.ent_ket.delete(0, 'end')
                self.load_grid_rak()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal: {e}")
            finally:
                cursor.close()
                conn.close()

    def buka_detail_rak(self, rak):
        top = Toplevel(self.root)
        top.title(f"Kotak: {rak['nama_rak']}")
        top.geometry("800x480")

        tk.Label(top, text=f"Daftar Obat dalam {rak['nama_rak']} ({rak['keterangan']})", font=("Helvetica", 14, "bold")).pack(pady=12)

        cols = ("ID", "Nama Obat", "Kategori", "Harga", "Stok", "Kedaluwarsa", "Status")
        tree_isi = ttk.Treeview(top, columns=cols, show="headings", height=10)
        for c in cols:
            tree_isi.heading(c, text=c)
            tree_isi.column(c, width=105, anchor="center")
        tree_isi.pack(fill="both", expand=True, padx=12, pady=5)

        def load_isi_rak():
            for item in tree_isi.get_children():
                tree_isi.delete(item)

            conn = buat_koneksi()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute("SELECT * FROM obat WHERE id_rak = %s", (rak['id_rak'],))
                    obat_list = cursor.fetchall()
                    
                    hari_ini = datetime.now().date()
                    for o in obat_list:
                        exp_date = o['tanggal_kedaluwarsa']
                        status = "Aman"
                        if exp_date:
                            if exp_date <= hari_ini:
                                status = "⚠️ KEDALUWARSA!"
                            elif (exp_date - hari_ini).days <= 30:
                                status = "⚠️ Segera Exp!"

                        tree_isi.insert("", "end", values=(
                            o['id_obat'], o['nama_obat'], o['kategori'], 
                            f"Rp {o['harga_jual']:,}", o['stok'], exp_date, status
                        ))
                except Exception as e:
                    print("Error detail rak:", e)
                finally:
                    cursor.close()
                    conn.close()

        load_isi_rak()

        def buang_obat_exp():
            selected = tree_isi.selection()
            if not selected:
                messagebox.showerror("Error", "Pilih obat di tabel yang ingin dibuang!", parent=top)
                return

            item_val = tree_isi.item(selected[0])['values']
            id_obat = item_val[0]
            nama_obat = item_val[1]

            confirm = messagebox.askyesno("Konfirmasi", f"Yakin ingin membuang obat '{nama_obat}'?", parent=top)
            if confirm:
                conn = buat_koneksi()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("DELETE FROM obat WHERE id_obat = %s", (id_obat,))
                        conn.commit()
                        messagebox.showinfo("Sukses", "Obat berhasil dibuang.", parent=top)
                        load_isi_rak()
                    except Exception as e:
                        messagebox.showerror("Error", f"Gagal: {e}", parent=top)
                    finally:
                        cursor.close()
                        conn.close()

        ttk.Button(top, text="🗑️ Buang / Hapus Obat Terpilih", bootstyle="danger", command=buang_obat_exp).pack(pady=12)

    # ==================== 3. MENU KASIR ====================
    def tampilkan_menu_kasir(self):
        self.clear_content()

        tk.Label(self.content_area, text="Kasir & Transaksi Penjualan", fg="white", bg=self.bg_dark, font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(0, 10))

        top_card = tk.Frame(self.content_area, bg=self.card_dark, padx=15, pady=10)
        top_card.pack(fill="x", pady=5)

        tk.Label(top_card, text="NAMA PEMBELI:", fg="#a0a0c0", bg=self.card_dark, font=("Arial", 9, "bold")).pack(side="left", padx=5)
        self.ent_pembeli = ttk.Entry(top_card, width=30)
        self.ent_pembeli.pack(side="left", padx=5)

        kasir_layout = tk.Frame(self.content_area, bg=self.bg_dark)
        kasir_layout.pack(fill="both", expand=True, pady=10)

        left_box = tk.Frame(kasir_layout, bg=self.card_dark, padx=15, pady=15)
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_box, text="Daftar Obat Tersedia", fg="white", bg=self.card_dark, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))
        cols_o = ("ID", "Nama", "Harga", "Stok")
        self.tree_pilih = ttk.Treeview(left_box, columns=cols_o, show="headings", height=8)
        for c in cols_o:
            self.tree_pilih.heading(c, text=c)
            self.tree_pilih.column(c, width=75, anchor="center")
        self.tree_pilih.pack(fill="both", expand=True)
        self.load_pilih_obat()

        ctrl = tk.Frame(left_box, bg=self.card_dark)
        ctrl.pack(fill="x", pady=10)
        tk.Label(ctrl, text="Qty:", fg="#a0a0c0", bg=self.card_dark).pack(side="left", padx=5)
        self.ent_qty = ttk.Entry(ctrl, width=8)
        self.ent_qty.insert(0, "1")
        self.ent_qty.pack(side="left", padx=5)
        ttk.Button(ctrl, text="Tambah ➔", bootstyle="success", command=self.tambah_keranjang).pack(side="left", padx=10)

        right_box = tk.Frame(kasir_layout, bg=self.card_dark, padx=15, pady=15)
        right_box.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(right_box, text="Keranjang Belanja", fg="white", bg=self.card_dark, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))
        cols_k = ("Nama Obat", "Harga", "Qty", "Subtotal")
        self.tree_cart = ttk.Treeview(right_box, columns=cols_k, show="headings", height=8)
        for c in cols_k:
            self.tree_cart.heading(c, text=c)
            self.tree_cart.column(c, width=85, anchor="center")
        self.tree_cart.pack(fill="both", expand=True)

        self.cart_items = []

        pay_box = tk.Frame(self.content_area, bg=self.card_dark, padx=15, pady=12)
        pay_box.pack(fill="x", pady=5)

        self.lbl_total = tk.Label(pay_box, text="Total: Rp 0", fg="#00b894", bg=self.card_dark, font=("Helvetica", 14, "bold"))
        self.lbl_total.pack(side="left", padx=10)

        tk.Label(pay_box, text="Bayar (Rp):", fg="#a0a0c0", bg=self.card_dark, font=("Arial", 9, "bold")).pack(side="left", padx=(30, 5))
        self.ent_bayar = ttk.Entry(pay_box, width=15)
        self.ent_bayar.pack(side="left", padx=5)

        ttk.Button(pay_box, text="Proses Pembayaran", bootstyle="primary", command=self.proses_transaksi).pack(side="left", padx=15)

    def load_pilih_obat(self):
        for item in self.tree_pilih.get_children():
            self.tree_pilih.delete(item)
        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_obat, nama_obat, harga_jual, stok FROM obat WHERE stok > 0")
            for row in cursor.fetchall():
                self.tree_pilih.insert("", "end", values=row)
            cursor.close()
            conn.close()

    def tambah_keranjang(self):
        selected = self.tree_pilih.selection()
        if not selected:
            messagebox.showerror("Error", "Pilih obat dulu dari tabel!")
            return
        
        item_data = self.tree_pilih.item(selected[0])['values']
        id_obat, nama, harga, stok_sisa = item_data[0], item_data[1], item_data[2], item_data[3]

        try:
            qty = int(self.ent_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Jumlah beli harus angka positif!")
            return

        if qty > stok_sisa:
            messagebox.showerror("Error", f"Stok tidak cukup! Sisa stok: {stok_sisa}")
            return

        subtotal = harga * qty
        self.cart_items.append({"id": id_obat, "nama": nama, "harga": harga, "qty": qty, "subtotal": subtotal})
        self.tree_cart.insert("", "end", values=(nama, harga, qty, subtotal))
        
        total = sum(item["subtotal"] for item in self.cart_items)
        self.lbl_total.config(text=f"Total: Rp {total:,}")

    def proses_transaksi(self):
        if not self.cart_items:
            messagebox.showerror("Error", "Keranjang masih kosong!")
            return
        
        pembeli = self.ent_pembeli.get().strip()
        if not pembeli:
            pembeli = "Umum"

        total_belanja = sum(item["subtotal"] for item in self.cart_items)

        try:
            bayar = int(self.ent_bayar.get())
            if bayar < total_belanja:
                messagebox.showerror("Error", "Uang pembayaran kurang!")
                return
        except ValueError:
            messagebox.showerror("Error", "Masukkan nominal uang bayar yang valid!")
            return

        kembalian = bayar - total_belanja
        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            try:
                query_penjualan = "INSERT INTO penjualan (nama_pembeli, total_harga) VALUES (%s, %s)"
                cursor.execute(query_penjualan, (pembeli, total_belanja))
                id_penjualan_baru = cursor.lastrowid

                for item in self.cart_items:
                    query_detail = "INSERT INTO detail_penjualan (id_penjualan, nama_obat, harga, qty, subtotal) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(query_detail, (id_penjualan_baru, item["nama"], item["harga"], item["qty"], item["subtotal"]))
                    cursor.execute("UPDATE obat SET stok = stok - %s WHERE id_obat = %s", (item["qty"], item["id"]))
                
                conn.commit()

                struk = f"""
==================================
          APOTEK SEHAT
==================================
Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Pembeli : {pembeli}
----------------------------------
"""
                for item in self.cart_items:
                    struk += f"{item['nama']} x{item['qty']} = Rp {item['subtotal']:,}\n"
                
                struk += f"""----------------------------------
Total     : Rp {total_belanja:,}
Bayar     : Rp {bayar:,}
Kembalian : Rp {kembalian:,}
==================================
     TERIMA KASIH & LEKAS SEMBUH
==================================
"""
                messagebox.showinfo("Struk Pembelian", struk)

                self.cart_items = []
                self.tree_cart.delete(*self.tree_cart.get_children())
                self.ent_bayar.delete(0, 'end')
                self.ent_pembeli.delete(0, 'end')
                self.lbl_total.config(text="Total: Rp 0")
                self.load_pilih_obat()

            except Exception as e:
                messagebox.showerror("Database Error", f"Gagal transaksi: {e}")
            finally:
                cursor.close()
                conn.close()

    # ==================== 4. MENU RIWAYAT TRANSAKSI ====================
    def tampilkan_riwayat(self):
        self.clear_content()

        tk.Label(self.content_area, text="Riwayat Transaksi Penjualan", fg="white", bg=self.bg_dark, font=("Helvetica", 18, "bold")).pack(anchor="w", pady=(0, 10))

        pane = tk.PanedWindow(self.content_area, orient="vertical", bg=self.bg_dark, sashwidth=4)
        pane.pack(fill="both", expand=True, pady=5)

        top_frame = tk.Frame(pane, bg=self.card_dark, padx=10, pady=10)
        pane.add(top_frame)

        tk.Label(top_frame, text="Daftar Transaksi", fg="white", bg=self.card_dark, font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
        cols_trans = ("ID", "Nama Pembeli", "Tanggal & Waktu", "Total Harga")
        self.tree_trans = ttk.Treeview(top_frame, columns=cols_trans, show="headings", height=5)
        for c in cols_trans:
            self.tree_trans.heading(c, text=c)
            self.tree_trans.column(c, width=150, anchor="center")
        self.tree_trans.pack(fill="both", expand=True)
        self.tree_trans.bind("<<TreeviewSelect>>", self.load_detail_transaksi)

        bottom_frame = tk.Frame(pane, bg=self.card_dark, padx=10, pady=10)
        pane.add(bottom_frame)

        tk.Label(bottom_frame, text="Detail Obat yang Dibeli", fg="white", bg=self.card_dark, font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
        cols_detail = ("Nama Obat", "Harga Satuan", "Jumlah (Qty)", "Subtotal")
        self.tree_detail = ttk.Treeview(bottom_frame, columns=cols_detail, show="headings", height=5)
        for c in cols_detail:
            self.tree_detail.heading(c, text=c)
            self.tree_detail.column(c, width=150, anchor="center")
        self.tree_detail.pack(fill="both", expand=True)

        self.load_data_transaksi()

    def load_data_transaksi(self):
        for item in self.tree_trans.get_children():
            self.tree_trans.delete(item)
            
        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id_penjualan, nama_pembeli, tanggal_penjualan, total_harga FROM penjualan ORDER BY tanggal_penjualan DESC")
                for row in cursor.fetchall():
                    formatted_row = (row[0], row[1], row[2], f"Rp {row[3]:,}")
                    self.tree_trans.insert("", "end", values=formatted_row)
            except Exception as e:
                print("Error load transaksi:", e)
            finally:
                cursor.close()
                conn.close()

    def load_detail_transaksi(self, event):
        for item in self.tree_detail.get_children():
            self.tree_detail.delete(item)

        selected = self.tree_trans.selection()
        if not selected:
            return

        trans_data = self.tree_trans.item(selected[0])['values']
        id_penjualan = trans_data[0]

        conn = buat_koneksi()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT nama_obat, harga, qty, subtotal FROM detail_penjualan WHERE id_penjualan = %s", (id_penjualan,))
                for row in cursor.fetchall():
                    formatted_row = (row[0], f"Rp {row[1]:,}", row[2], f"Rp {row[3]:,}")
                    self.tree_detail.insert("", "end", values=formatted_row)
            except Exception as e:
                print("Error load detail:", e)
            finally:
                cursor.close()
                conn.close()

# Main Program Eksekusi
def main():
    root = ttk.Window(themename="darkly")
    
    def on_login_success(role):
        main_window = ttk.Window(themename="darkly")
        AplikasiApotekDashboard(main_window, role)
        main_window.mainloop()

    WindowLogin(root, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    main()