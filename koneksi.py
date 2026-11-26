import mysql.connector

def buat_koneksi():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_manajemen_apotek"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Gagal terhubung ke database: {err}")
        return None