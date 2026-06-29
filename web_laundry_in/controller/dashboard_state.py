import reflex as rx
import pandas as pd
import io
from ..model.models import Outlet, TransaksiLaundry

class DashboardState(rx.State):
    pesan_status: str = ""
    # Tempat menyimpan data akhir untuk disuplai ke komponen grafik Recharts
    data_grafik: list[dict] = []

    def muat_data_grafik(self):
        """Mengambil data dari DB dan menghitung total omset per outlet untuk grafik"""
        self.data_grafik = []
        
        with rx.session() as session:
            # 1. Ambil semua data outlet yang terdaftar
            daftar_outlet = session.exec(Outlet.select()).all()
            
            for outlet in daftar_outlet:
                # 2. Ambil semua transaksi milik outlet ini
                transaksi_outlet = session.exec(
                    TransaksiLaundry.select().where(TransaksiLaundry.outlet_id == outlet.id)
                ).all()
                
                # 3. Hitung total omsetnya
                total_omset = sum(t.total_harga for t in transaksi_outlet)
                
                # 4. Masukkan ke dalam format list dictionary yang dipahami Recharts
                self.data_grafik.append({
                    "name": outlet.nama_outlet,
                    "Omset": total_omset
                })

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Fungsi memproses file Excel yang diunggah oleh Owner"""
        if not files:
            self.pesan_status = "Mohon pilih berkas Excel terlebih dahulu!"
            return

        upload_file = files[0]
        try:
            file_data = await upload_file.read()
            df = pd.read_excel(io.BytesIO(file_data), sheet_name=0, skiprows=22)
            
            df.columns = df.iloc[0]
            df_clean = df.iloc[2:].copy()
            df_clean = df_clean.dropna(subset=['No Nota'])
            
            jumlah_terimpor = 0
            with rx.session() as session:
                for _, row in df_clean.iterrows():
                    no_nota = str(row['No Nota']).strip()
                    
                    existing = session.exec(
                        TransaksiLaundry.select().where(TransaksiLaundry.no_nota == no_nota)
                    ).first()
                    if existing:
                        continue
                        
                    nama_outlet_excel = str(row['Outlet']).strip()
                    outlet = session.exec(
                        Outlet.select().where(Outlet.nama_outlet == nama_outlet_excel)
                    ).first()
                    
                    if not outlet:
                        outlet = Outlet(nama_outlet=nama_outlet_excel, lokasi="-")
                        session.add(outlet)
                        session.commit()
                        session.refresh(outlet)
                    
                    total_tagihan = row.get('Total Tagihan', 0)
                    if pd.isna(total_tagihan):
                        total_tagihan = 0
                        
                    transaksi = TransaksiLaundry(
                        no_nota=no_nota,
                        outlet_id=outlet.id,
                        tgl_terima=str(row['Tgl Terima']),
                        total_harga=int(total_tagihan)
                    )
                    session.add(transaksi)
                    jumlah_terimpor += 1
                
                session.commit()
                
            self.pesan_status = f"Sukses! Berhasil mengimpor {jumlah_terimpor} data transaksi baru ke database."
            # Otomatis perbarui data grafik setelah proses impor selesai
            self.muat_data_grafik()
            
        except Exception as e:
            self.pesan_status = f"Gagal membaca file: {str(e)}"