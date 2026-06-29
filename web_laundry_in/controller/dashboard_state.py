import reflex as rx
import pandas as pd
import io
from datetime import datetime
from ..model.models import Outlet, TransaksiLaundry

class DashboardState(rx.State):
    pesan_status: str = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Fungsi untuk memproses file Excel yang diunggah oleh Owner"""
        if not files:
            self.pesan_status = "Tidak ada file yang dipilih."
            return

        file = files[0]
        # Membaca file mentah dari memory upload
        upload_data = await file.read()
        
        try:
            # 1. Baca Excel menggunakan Pandas (Skip 22 baris header atas sesuai format file Anda)
            df = pd.read_excel(io.BytesIO(upload_data), sheet_name=0, skiprows=22)
            
            # Rapikan nama kolom berdasarkan baris pertama
            df.columns = df.iloc[0]
            df_clean = df.iloc[2:].copy() # Ambil data transaksi asli di bawah header
            
            total_terinput = 0
            total_dilewati = 0

            with rx.session() as session:
                for _, row in df_clean.iterrows():
                    # Lewati jika baris kosong atau bukan data transaksi
                    if pd.isna(row['No Nota']) or str(row['No Nota']).strip() == "":
                        continue
                        
                    no_nota = str(row['No Nota']).strip()
                    nama_outlet_excel = str(row['Outlet']).strip()
                    
                    # 2. Cek apakah Outlet ini sudah terdaftar di database kita, jika belum, buat otomatis
                    outlet = session.query(Outlet).filter(Outlet.nama_outlet == nama_outlet_excel).first()
                    if not outlet:
                        outlet = Outlet(nama_outlet=nama_outlet_excel, lokasi="-")
                        session.add(outlet)
                        session.commit()
                        session.refresh(outlet)
                    
                    # 3. LOGIKA APPEND PINTAR: Cek apakah No Nota sudah ada di database
                    transaksi_lama = session.query(TransaksiLaundry).filter(TransaksiLaundry.no_nota == no_nota).first()
                    
                    if transaksi_lama:
                        total_dilewati += 1
                        continue # Skip ke baris berikutnya, jangan diinput lagi
                    
                    # 4. Parsing data tanggal dan harga dari Excel
                    try:
                        tgl_terima = pd.to_datetime(row['Tgl Terima'])
                    except:
                        tgl_terima = datetime.now()
                        
                    total_tagihan = int(row['Total Tagihan']) if pd.notna(row['Total Tagihan']) else 0
                    status_proses = str(row['Progres Pengerjaan']) if pd.notna(row['Progres Pengerjaan']) else "0%"

                    # 5. Masukkan data baru ke database
                    baru = TransaksiLaundry(
                        no_nota=no_nota,
                        outlet_id=outlet.id,
                        tgl_terima=tgl_terima,
                        total_tagihan=total_tagihan,
                        status_proses=status_proses
                    )
                    session.add(baru)
                    total_terinput += 1
                
                session.commit()
                
            self.pesan_status = f"Sukses! {total_terinput} transaksi baru berhasil dimasukkan. ({total_dilewati} data lama dilewati)."
            
        except Exception as e:
            self.pesan_status = f"Gagal membaca file: {str(e)}"