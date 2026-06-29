import reflex as rx
from datetime import datetime
from typing import Optional

# 1. Tabel Pengguna (Sistem Fleksibel untuk Owner & Mitra)
class User(rx.Model):
    username: Optional[str] = None  # Hanya diisi oleh Owner (misal: "admin")
    password: Optional[str] = None  # Hanya diisi oleh Owner
    
    # Kunci login untuk Mitra (Ibu-ibu cukup masukkan 4 digit belakang nomor HP)
    kode_akses: str  # Contoh: "1969"
    
    role: str  # "owner" atau "mitra"
    outlet_id: Optional[int] = None  # Menyambungkan akun mitra ke outletnya sendiri

# 2. Tabel Master Outlet
class Outlet(rx.Model):
    nama_outlet: str  # Contoh: "Laundry IN Outlet 5 (Mitra 001-Semampir)"
    lokasi: str

# 3. Tabel Detail Transaksi (Menggunakan No Nota sebagai Kunci Unik)
class TransaksiLaundry(rx.Model):
    no_nota: str  # Ini acuan agar tidak terjadi duplikasi saat upload ulang
    outlet_id: int
    tgl_terima: datetime
    total_tagihan: int
    status_proses: str  # Diambil dari kolom "Progres Pengerjaan" di Excel (misal: "11%")