import reflex as rx
from typing import Optional

class Outlet(rx.Model, table=True):
    """Model untuk menyimpan daftar cabang/mitra laundry"""
    nama_outlet: str
    lokasi: str

class TransaksiLaundry(rx.Model, table=True):
    """Model untuk menyimpan data transaksi impor dari Excel"""
    no_nota: str
    outlet_id: Optional[int] = None
    tgl_terima: str
    total_harga: int