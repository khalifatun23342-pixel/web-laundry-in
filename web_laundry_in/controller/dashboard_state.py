import reflex as rx
import pandas as pd
import io
from ..model.models import Outlet, TransaksiLaundry

class DashboardState(rx.State):
    pesan_status: str = ""
    data_grafik: list[dict] = []
    outlet_aktif_lokal: str = ""
    daftar_outlet_warna: list[dict] = []
    total_omset_tampil: str = "Rp 0"
    rata_rata_omset_tampil: str = "Rp 0"

    # Menyimpan daftar nama outlet yang sedang dicentang oleh Owner
    outlet_terpilih: list[str] = []
    
    # Menampung list dictionary statistik individual untuk tabel bawah (Contoh: [{"nama": "Outlet 1", "total": "Rp 5M", "rata": "Rp 10jt"}])
    statistik_per_outlet: list[dict] = []

    def toggle_outlet(self, nama_outlet: str):
        """Fungsi ketika checklist outlet diklik oleh Owner"""
        # 1. Salin list aktif ke dalam variabel lokal murni Python
        list_sekarang = list(self.outlet_terpilih)
        
        # 2. Balik Logika: Jika nama outlet sudah ada di list, artinya user ingin MENCOPOT centang (mematikan)
        if nama_outlet in list_sekarang:
            list_sekarang.remove(nama_outlet)
        else:
            # Jika belum ada di list, artinya user memberikan centang baru (menyalakan)
            list_sekarang.append(nama_outlet)
            
        # 3. Kembalikan data list yang baru ke state Reflex
        self.outlet_terpilih = list_sekarang
        
        # 4. Paksa grafik dan angka di card untuk berhitung ulang otomatis
        return DashboardState.muat_data_grafik
    
    # ==============================================================================
    # GANTI MULAI DARI BARIS INI (Hapus versi dictionary yang tadi, ganti dengan ini)
    # ==============================================================================
    mode_grafik: str = "H-B"  
    
    bulan_terpilih: str = "Juni"  
    tahun_terpilih: str = "2026" 
    minggu_terpilih: str = "Minggu 1 (Tgl 1-7)"  
    
    tt_tahun_awal: str = "2023"
    tt_tahun_akhir: str = "2026"
    
    opsi_mode: list[str] = ["H-M", "H-B", "M-B", "B-T", "T-T"]
    opsi_bulan: list[str] = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    opsi_minggu: list[str] = [
        "Minggu 1 (Tgl 1-7)",
        "Minggu 2 (Tgl 8-14)",
        "Minggu 3 (Tgl 15-21)",
        "Minggu 4 (Tgl 22-Akhir)"
    ]
    
    opsi_tahun: list[str] = [str(y) for y in range(2023, 2046)]

    def ganti_filter(self, key: str, value: str):
        if key == "mode": self.mode_grafik = value
        elif key == "bulan": self.bulan_terpilih = value
        elif key == "tahun": self.tahun_terpilih = value
        elif key == "minggu": self.minggu_terpilih = value
        elif key == "tt_awal": self.tt_tahun_awal = value
        elif key == "tt_akhir": self.tt_tahun_akhir = value
        
        return DashboardState.muat_data_grafik
    # ==============================================================================
    # BATAS AKHIR LANGKAH 1 (Tepat sebelum fungsi muat_data_grafik dimulai)
    # ==============================================================================

    def muat_data_grafik(self):
        """Mesin Utama: Memproses 5 Jenis Grafik secara Dinamis & Otomatis (Anti-Crash & Aman)"""
        self.data_grafik = []
        self.daftar_outlet_warna = []
        # 📌 JURUS KUNCI: Urutkan deretan Checkbox agar rapi dari Outlet 1 sampai 6!
        self.daftar_outlet_warna.sort(key=lambda x: x["nama"])
        outlet_target = self.outlet_aktif_lokal
        
        with rx.session() as session:
            # 1. Ambil Data Master Outlet & Urutkan secara Ascending (A-Z / ID 1-6)
            daftar_outlet = session.exec(Outlet.select().order_by(Outlet.id)).all()
            semua_transaksi = session.exec(TransaksiLaundry.select()).all()
            
            if not semua_transaksi:
                return

            # 📌 SELIPKAN KODE INI DI SINI:
            # Jika aplikasi baru pertama kali dibuka (list checkbox backend masih kosong),
            # isi langsung dengan semua nama outlet agar sinkron dengan centang UI murni.
            if not self.outlet_terpilih:
                self.outlet_terpilih = [o.nama_outlet for o in daftar_outlet]

            # Pasang skema warna kontras untuk garis outlet
            warna_preset = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f43f5e"]
            self.daftar_outlet_warna = [
                {"nama": o.nama_outlet, "warna": warna_preset[i % len(warna_preset)]}
                for i, o in enumerate(daftar_outlet)
            ]

            # 2. Parsing Tanggal Transaksi ke DataFrame Pandas agar Pemrosesan Super Cepat
            data_list = []
            for t in semua_transaksi:
                tgl_raw = str(t.tgl_terima).strip().split()[0]
                tgl_konv = pd.to_datetime(tgl_raw, errors='coerce')
                
                # Jaga-jaga jika format tanggal excel aneh
                if pd.isna(tgl_konv):
                    angka_hari = ''.join(filter(str.isdigit, tgl_raw))
                    if angka_hari:
                        tgl_konv = pd.to_datetime(f"2026-06-{angka_hari.zfill(2)}", errors='coerce')
                        
                if pd.notna(tgl_konv):
                    data_list.append({
                        "tanggal": tgl_konv,
                        "outlet_id": t.outlet_id,
                        "total_harga": t.total_harga
                    })
            
            if not data_list:
                return
                
            df = pd.DataFrame(data_list)

            # ==============================================================================
            # EKSEKUSI LOGIKA 5 JENIS GRAFIK BERDASARKAN MODE YANG TERPILIH DI UI
            # ==============================================================================
            
            # Buat list referensi untuk mencari index bulan berdasarkan pilihan string murni
            list_nama_bulan = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]

            # --- MODE 1: H-M (Hari dalam 1 Minggu) ---
            if self.mode_grafik == "H-M":
                tahun = int(self.tahun_terpilih)
                bulan = list_nama_bulan.index(self.bulan_terpilih) + 1
                
                # Deteksi rentang hari berdasarkan pilihan string minggu secara cerdas
                if "Minggu 1" in self.minggu_terpilih: 
                    hari_mulai, hari_selesai = 1, 7
                elif "Minggu 2" in self.minggu_terpilih: 
                    hari_mulai, hari_selesai = 8, 14
                elif "Minggu 3" in self.minggu_terpilih: 
                    hari_mulai, hari_selesai = 15, 21
                else: 
                    hari_mulai, hari_selesai = 22, int(pd.Timestamp(year=tahun, month=bulan, day=1).days_in_month)
                
                tgl_mulai = pd.Timestamp(year=tahun, month=bulan, day=hari_mulai)
                tgl_selesai = pd.Timestamp(year=tahun, month=bulan, day=hari_selesai)
                
                deret_tgl = pd.date_range(start=tgl_mulai, end=tgl_selesai).strftime('%Y-%m-%d').tolist()
                peta_omset = {tgl: {o.id: 0 for o in daftar_outlet} for tgl in deret_tgl}
                
                df_filtered = df[(df['tanggal'] >= tgl_mulai) & (df['tanggal'] <= tgl_selesai)]
                for _, row in df_filtered.iterrows():
                    tgl_str = row['tanggal'].strftime('%Y-%m-%d')
                    peta_omset[tgl_str][row['outlet_id']] += row['total_harga']
                    
                for tgl in deret_tgl:
                    nama_hari = pd.to_datetime(tgl).day_name()
                    hari_indo = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}[nama_hari]
                    data_baris = {"Tanggal": f"{hari_indo} ({tgl.split('-')[2]})"}
                    self._susun_baris_peran(data_baris, peta_omset[tgl], daftar_outlet, outlet_target)

            # --- MODE 2: H-B (Hari dalam 1 Bulan) ---
            elif self.mode_grafik == "H-B":
                tahun = int(self.tahun_terpilih)
                bulan = list_nama_bulan.index(self.bulan_terpilih) + 1
                
                tgl_mulai = pd.Timestamp(year=tahun, month=bulan, day=1)
                tgl_selesai = tgl_mulai + pd.offsets.MonthEnd(0)
                
                deret_tgl = pd.date_range(start=tgl_mulai, end=tgl_selesai).strftime('%Y-%m-%d').tolist()
                peta_omset = {tgl: {o.id: 0 for o in daftar_outlet} for tgl in deret_tgl}
                
                df_filtered = df[(df['tanggal'] >= tgl_mulai) & (df['tanggal'] <= tgl_selesai)]
                for _, row in df_filtered.iterrows():
                    tgl_str = row['tanggal'].strftime('%Y-%m-%d')
                    peta_omset[tgl_str][row['outlet_id']] += row['total_harga']
                    
                for tgl in deret_tgl:
                    data_baris = {"Tanggal": tgl}
                    self._susun_baris_peran(data_baris, peta_omset[tgl], daftar_outlet, outlet_target)

            # --- MODE 3: M-B (Minggu dalam 1 Bulan) ---
            elif self.mode_grafik == "M-B":
                tahun = int(self.tahun_terpilih)
                bulan = list_nama_bulan.index(self.bulan_terpilih) + 1
                
                peta_omset_minggu = {
                    "Minggu 1": {o.id: 0 for o in daftar_outlet},
                    "Minggu 2": {o.id: 0 for o in daftar_outlet},
                    "Minggu 3": {o.id: 0 for o in daftar_outlet},
                    "Minggu 4": {o.id: 0 for o in daftar_outlet},
                }
                
                df_filtered = df[(df['tanggal'].dt.year == tahun) & (df['tanggal'].dt.month == bulan)]
                for _, row in df_filtered.iterrows():
                    tgl_hari = row['tanggal'].day
                    if 1 <= tgl_hari <= 7: m_key = "Minggu 1"
                    elif 8 <= tgl_hari <= 14: m_key = "Minggu 2"
                    elif 15 <= tgl_hari <= 21: m_key = "Minggu 3"
                    else: m_key = "Minggu 4"
                    
                    peta_omset_minggu[m_key][row['outlet_id']] += row['total_harga']
                    
                for m_name in ["Minggu 1", "Minggu 2", "Minggu 3", "Minggu 4"]:
                    data_baris = {"Tanggal": m_name}
                    self._susun_baris_peran(data_baris, peta_omset_minggu[m_name], daftar_outlet, outlet_target)

            # --- MODE 4: B-T (Bulan dalam 1 Tahun) ---
            elif self.mode_grafik == "B-T":
                tahun = int(self.tahun_terpilih)
                nama_bulan_indo = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
                peta_omset_bulan = {m: {o.id: 0 for o in daftar_outlet} for m in range(1, 13)}
                
                df_filtered = df[df['tanggal'].dt.year == tahun]
                for _, row in df_filtered.iterrows():
                    bln_idx = row['tanggal'].month
                    peta_omset_bulan[bln_idx][row['outlet_id']] += row['total_harga']
                    
                for bln_idx in range(1, 13):
                    data_baris = {"Tanggal": nama_bulan_indo[bln_idx - 1]}
                    self._susun_baris_peran(data_baris, peta_omset_bulan[bln_idx], daftar_outlet, outlet_target)

            # --- MODE 5: T-T (Tahun-Tahun dalam Rentang Dekade) ---
            elif self.mode_grafik == "T-T":
                thn_awal = int(self.tt_tahun_awal)
                thn_akhir = int(self.tt_tahun_akhir)
                
                # PENGAMAN JITU: Fitur swap otomatis jika user terbalik memilih tahun awal & akhir!
                if thn_awal > thn_akhir:
                    thn_awal, thn_akhir = thn_akhir, thn_awal
                    
                deret_tahun = list(range(thn_awal, thn_akhir + 1))
                peta_omset_tahun = {thn: {o.id: 0 for o in daftar_outlet} for thn in deret_tahun}
                
                df_filtered = df[(df['tanggal'].dt.year >= thn_awal) & (df['tanggal'].dt.year <= thn_akhir)]
                for _, row in df_filtered.iterrows():
                    thn_idx = row['tanggal'].year
                    peta_omset_tahun[thn_idx][row['outlet_id']] += row['total_harga']
                    
                for thn in deret_tahun:
                    data_baris = {"Tanggal": str(thn)}
                    self._susun_baris_peran(data_baris, peta_omset_tahun[thn], daftar_outlet, outlet_target)

            # ==============================================================================
            # KALKULASI GRAND TOTAL & DETAIL STATISTIK INDIVIDUAL PER OUTLET (TABEL BAWAH)
            # ==============================================================================
            grand_total_nilai = 0
            jumlah_titik = len(self.data_grafik)
            
            # Wadah penampung kalkulasi angka dasar awal per outlet
            kalkulasi_toko = {o.nama_outlet: {"total": 0, "titik_aktif": 0} for o in daftar_outlet}
            
            for baris in self.data_grafik:
                if outlet_target:
                    grand_total_nilai += baris.get("Omset", 0)
                else:
                    grand_total_nilai += baris.get("Total_Gabungan", 0)
                    # Hitung akumulasi per toko untuk ditaruh di jabaran tabel bawah
                    for o in daftar_outlet:
                        nilai_toko = baris.get(o.nama_outlet)
                        if nilai_toko is not None:
                            kalkulasi_toko[o.nama_outlet]["total"] += nilai_toko
                            kalkulasi_toko[o.nama_outlet]["titik_aktif"] += 1
            
            # Format Teks Grand Total & Grand Rata-rata Gabungan
            rata_grand_nilai = grand_total_nilai / jumlah_titik if jumlah_titik > 0 else 0
            self.total_omset_tampil = f"Rp {grand_total_nilai:,.0f}".replace(",", ".")
            self.rata_rata_omset_tampil = f"Rp {rata_grand_nilai:,.0f}".replace(",", ".")
            
            # Susun data jabaran awal per outlet khusus untuk outlet yang dicentang saja
            self.statistik_per_outlet = []
            for o in daftar_outlet:
                if o.nama_outlet in self.outlet_terpilih:
                    t_nilai = kalkulasi_toko[o.nama_outlet]["total"]
                    t_titik = kalkulasi_toko[o.nama_outlet]["titik_aktif"]
                    r_nilai = t_nilai / t_titik if t_titik > 0 else 0
                    
                    self.statistik_per_outlet.append({
                        "nama": o.nama_outlet,
                        "total": f"Rp {t_nilai:,.0f}".replace(",", "."),
                        "rata": f"Rp {r_nilai:,.0f}".replace(",", ".")
                    })

            # 1. Mengurutkan Tabel Bagian Bawah (Sudah Berhasil)
            self.statistik_per_outlet.sort(key=lambda x: x["nama"])
            
            # 📌 TAMBAHKAN BARIS BARU INI DI SINI UNTUK MENGURUTKAN CHECKBOX ATAS:
            self.daftar_outlet_warna.sort(key=lambda x: x["nama"])

    def _susun_baris_peran(self, data_baris, peta_id_omset, daftar_outlet, outlet_target):
        """Fungsi pembantu internal untuk mengunci data sesuai hak akses Mitra / Checklist Owner"""
        if outlet_target:
            for o in daftar_outlet:
                if outlet_target.lower() in o.nama_outlet.lower():
                    data_baris["Omset"] = peta_id_omset[o.id]
                    data_baris["Outlet"] = o.nama_outlet
                    break
            if "Omset" in data_baris:
                self.data_grafik.append(data_baris)
        else:
            # ==============================================================================
            # JALUR OWNER: SINKRONISASI TOTAL DAN GARIS DENGAN LIST CHECKBOX UTAMA
            # ==============================================================================
            total_per_baris = 0
            for o in daftar_outlet:
                omset_toko = peta_id_omset[o.id]
                
                # JURUS JITU: Hanya masukkan omset jika nama outlet ada di daftar yang DICENTANG
                if o.nama_outlet in self.outlet_terpilih:
                    data_baris[o.nama_outlet] = omset_toko
                    total_per_baris += omset_toko
                else:
                    # Jika TIDAK dicentang, beri nilai None agar garisnya lenyap dari grafik komparasi
                    data_baris[o.nama_outlet] = None
            
            # Garis hijau tebal (Total Gabungan) di grafik atas hanya akan berisi penjumlahan outlet terpilih
            data_baris["Total_Gabungan"] = total_per_baris
            self.data_grafik.append(data_baris)

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