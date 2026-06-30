import reflex as rx
from ..controller.auth_state import AuthState
from ..controller.dashboard_state import DashboardState

def form_login() -> rx.Component:
    """Tampilan Form Login Menggunakan rx.form (Anti-Error Kompilasi)"""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Sistem Monitoring Laundry IN", size="6", text_align="center"),
                rx.text("Silakan pilih tipe akses masuk Anda", color_scheme="gray", text_align="center"),
                
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Akses Mitra (PIN)", value="tab_mitra"),
                        rx.tabs.trigger("Akses Owner", value="tab_owner"),
                    ),
                    rx.tabs.content(
                        rx.form.root(
                            rx.vstack(
                                rx.text("Masukkan 4 Digit Terakhir No. HP Anda:", font_size="14px", margin_top="10px"),
                                rx.input(
                                    placeholder="Masukkan 4 angka...", 
                                    type="text",
                                    max_length=4,
                                    name="input_pin", 
                                    width="100%"
                                ),
                                rx.button("Masuk Ke Dashboard", type="submit", color_scheme="blue", width="100%"),
                                spacing="3",
                            ),
                            on_submit=AuthState.login_mitra_form,
                        ),
                        value="tab_mitra",
                    ),
                    rx.tabs.content(
                        rx.form.root(
                            rx.vstack(
                                rx.input(placeholder="Username", name="input_user", width="100%", margin_top="10px"),
                                rx.input(placeholder="Password", type="password", name="input_pass", width="100%"),
                                rx.button("Masuk Sebagai Owner", type="submit", color_scheme="green", width="100%"),
                                spacing="3",
                            ),
                            on_submit=AuthState.login_owner_form,
                        ),
                        value="tab_owner",
                    ),
                    default_value="tab_mitra",
                    width="100%"
                ),
                
                rx.cond(
                    AuthState.pesan_error != "",
                    rx.text(AuthState.pesan_error, color="red", font_size="13px", text_align="center")
                ),
                spacing="4",
                padding="10px",
            ),
            width="400px",
        ),
        height="100vh",
        width="100vw"
    )

def halaman_owner() -> rx.Component:
    """Tampilan khusus untuk Owner dengan Impor Data dan Grafik Komparasi"""
    return rx.vstack(
        rx.text("Selamat datang Owner! Silakan kelola berkas transaksi di bawah.", font_size="16px"),
        rx.upload(
            rx.vstack(
                rx.button("Pilih File Excel", color_scheme="blue"),
                rx.text("atau seret file ke sini", color="gray"),
            ),
            id="upload_excel",
            border="2px dashed #ccc",
            padding="30px",
            border_radius="10px",
            width="100%",
        ),
        rx.vstack(
            rx.foreach(
                rx.selected_files("upload_excel"),
                lambda file: rx.text(f"📄 File terpilih: {file}", color="green", font_weight="bold")
            ),
            align_items="start",
            width="100%"
        ),
        rx.button(
            "Mulai Proses Impor Data",
            color_scheme="green",
            on_click=DashboardState.handle_upload(rx.upload_files(upload_id="upload_excel")),
            width="100%"
        ),
        rx.cond(
            DashboardState.pesan_status != "",
            rx.callout(DashboardState.pesan_status, color_scheme="blue", width="100%")
        ),
        rx.divider(margin_top="20px", margin_bottom="20px"),
        # Tampilkan grafik komparasi tumpuk multi-outlet di halaman dashboard Owner
        grafik_owner_tumpuk(),
        width="100%",
        spacing="4"
    )

def halaman_mitra() -> rx.Component:
    """Tampilan Halaman Dashboard Terkunci khusus Mitra"""
    from ..controller.auth_state import AuthState
    
    return rx.vstack(
        # Header Informasi Nama Outlet Mitra
        rx.vstack(
            rx.text("Tren Capaian Omset Harian (Urutan Tanggal Penuh)", font_size="18px", font_weight="bold"),
            rx.text("Outlet Mitra: " + AuthState.nama_outlet_aktif, color="gray", font_size="14px"),
            align_items="start",
            margin_bottom="10px",
        ),
        
        # PANGGIL FUNGSI DROPDOWN + GRAFIK MULTI-MODE YANG BARU DI SINI:
        grafik_mitra_tunggal(),
        
        width="100%",
        spacing="4"
    )

def grafik_owner_tumpuk() -> rx.Component:
    """Tampilan Dashboard Owner Lengkap dengan Checklist Multi-Outlet & Tabel Penjabaran Detil"""
    return rx.vstack(
        # --- 1. PANEL FILTER DROPDOWN UTAMA ---
        rx.flex(
            rx.vstack(
                rx.text("Mode Analisis", font_size="12px", color="gray", font_weight="bold"),
                rx.select(DashboardState.opsi_mode, value=DashboardState.mode_grafik, on_change=lambda val: DashboardState.ganti_filter("mode", val), color_scheme="blue", width="110px"),
                align_items="start",
            ),
            rx.cond(
                (DashboardState.mode_grafik == "H-M") | (DashboardState.mode_grafik == "H-B") | (DashboardState.mode_grafik == "M-B"),
                rx.vstack(
                    rx.text("Bulan", font_size="12px", color="gray", font_weight="bold"),
                    rx.select(DashboardState.opsi_bulan, value=DashboardState.bulan_terpilih, on_change=lambda val: DashboardState.ganti_filter("bulan", val), width="140px"),
                    align_items="start",
                ),
            ),
            rx.cond(
                DashboardState.mode_grafik == "H-M",
                rx.vstack(
                    rx.text("Pilih Minggu", font_size="12px", color="gray", font_weight="bold"),
                    rx.select(DashboardState.opsi_minggu, value=DashboardState.minggu_terpilih, on_change=lambda val: DashboardState.ganti_filter("minggu", val), width="190px"),
                    align_items="start",
                ),
            ),
            rx.cond(
                DashboardState.mode_grafik != "T-T",
                rx.vstack(
                    rx.text("Tahun", font_size="12px", color="gray", font_weight="bold"),
                    rx.select(DashboardState.opsi_tahun, value=DashboardState.tahun_terpilih, on_change=lambda val: DashboardState.ganti_filter("tahun", val), width="100px"),
                    align_items="start",
                ),
            ),
            rx.cond(
                DashboardState.mode_grafik == "T-T",
                rx.hstack(
                    rx.vstack(
                        rx.text("Tahun Awal", font_size="12px", color="gray", font_weight="bold"),
                        rx.select(DashboardState.opsi_tahun, value=DashboardState.tt_tahun_awal, on_change=lambda val: DashboardState.ganti_filter("tt_awal", val), width="110px"),
                        align_items="start",
                    ),
                    rx.text("s/d", margin_top="25px", color="gray"),
                    rx.vstack(
                        rx.text("Tahun Akhir", font_size="12px", color="gray", font_weight="bold"),
                        rx.select(DashboardState.opsi_tahun, value=DashboardState.tt_tahun_akhir, on_change=lambda val: DashboardState.ganti_filter("tt_akhir", val), width="110px"),
                        align_items="start",
                    ),
                    spacing="3",
                ),
            ),
            rx.spacer(),
            rx.button("Picu Muat Grafik", color_scheme="green", size="2", margin_top="18px", on_click=DashboardState.muat_data_grafik),
            width="100%", spacing="4", background_color="rgba(255,255,255,0.02)", padding="15px", border_radius="10px", border="1px solid rgba(255,255,255,0.05)", align_items="center", flex_wrap="wrap",
        ),
        
        # --- 2. FITUR FITUR CHECKBOX PILIH OUTLET (LOGIKA EKSKLUSI) ---
        rx.vstack(
            rx.text("❌ Pilih Outlet yang TIDAK Ingin Dianalisis (Sembunyikan):", font_size="13px", font_weight="bold", color="red"),
            rx.flex(
                rx.foreach(
                    DashboardState.daftar_outlet_warna,
                    lambda item: rx.box(
                        rx.checkbox(
                            item["nama"],
                            is_checked=DashboardState.outlet_terpilih.contains(item["nama"]),
                            on_change=lambda _: DashboardState.toggle_outlet(item["nama"]),
                            color_scheme="red", # Diubah ke merah agar senada dengan konsep "Sembunyikan/Eksklusi"
                            size="2"
                        ),
                        margin_right="15px",
                        margin_bottom="5px"
                    )
                ),
                flex_wrap="wrap",
                width="100%"
            ),
            width="100%",
            padding="12px 15px",
            background_color="rgba(255,255,255,0.01)",
            border_radius="8px",
            border="1px solid rgba(255,255,255,0.04)"
        ),
        
        # --- 3. PANEL GRAND TOTAL & GRAND RATA-RATA ---
        rx.grid(
            rx.vstack(
                rx.text("Grand Total Omset (Outlet Aktif)", font_size="13px", color="gray"),
                rx.text(DashboardState.total_omset_tampil, font_size="22px", font_weight="bold", color="#10b981"),
                background_color="rgba(16, 185, 129, 0.05)", padding="15px", border_radius="10px", border="1px solid rgba(16, 185, 129, 0.15)", align_items="start", width="100%"
            ),
            rx.vstack(
                rx.text("Grand Rata-rata Omset (Outlet Aktif)", font_size="13px", color="gray"),
                rx.text(DashboardState.rata_rata_omset_tampil, font_size="22px", font_weight="bold", color="#3b82f6"),
                background_color="rgba(59, 130, 246, 0.05)", padding="15px", border_radius="10px", border="1px solid rgba(59, 130, 246, 0.15)", align_items="start", width="100%"
            ),
            columns="2", spacing="4", width="100%"
        ),
        
        # --- 4. GRAFIK (A): TREN TOTAL OMSET GABUNGAN ---
        rx.vstack(
            rx.text("📈 Tren Grafik Total Omset Perusahaan (Akumulasi Outlet Yang Aktif)", font_size="14px", font_weight="bold", color="white", margin_left="15px", margin_top="10px"),
            rx.center(
                rx.recharts.line_chart(
                    rx.recharts.line(data_key="Total_Gabungan", stroke="#10b981", stroke_width=3.5, dot={"r": 3}, active_dot={"r": 7}),
                    rx.recharts.x_axis(data_key="Tanggal", font_size="11px", tick_margin=10),
                    rx.recharts.y_axis(font_size="12px", orientation="right", tick_margin=10),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.graphing_tooltip(),
                    data=DashboardState.data_grafik, width="100%", height=280,
                ),
                width="100%", padding="10px 15px",
            ),
            width="100%", background_color="rgba(255,255,255,0.01)", border_radius="12px", border="1px solid rgba(255,255,255,0.06)",
        ),

        # --- 5. GRAFIK (B): KOMPARASI MULTI-GARIS OUTLET ---
        rx.vstack(
            rx.text("📊 Perbandingan Garis Omset Antar Cabang", font_size="14px", font_weight="bold", color="white", margin_left="15px", margin_top="10px"),
            rx.center(
                rx.recharts.line_chart(
                    rx.foreach(
                        DashboardState.daftar_outlet_warna,
                        lambda item: rx.recharts.line(data_key=item["nama"], stroke=item["warna"], stroke_width=2, dot={"r": 2}, active_dot={"r": 5})
                    ),
                    rx.recharts.x_axis(data_key="Tanggal", font_size="11px", tick_margin=10),
                    rx.recharts.y_axis(font_size="12px", orientation="right", tick_margin=10),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.legend(vertical_align="bottom", height=55, margin_top=10),
                    data=DashboardState.data_grafik, width="100%", height=320,
                ),
                width="100%", padding="10px 15px",
            ),
            width="100%", background_color="rgba(255,255,255,0.01)", border_radius="12px", border="1px solid rgba(255,255,255,0.06)",
        ),

        # --- 6. TABEL RAGAM STATISTIK INDIVIDUAL OUTLET (PALING BAWAH) ---
        rx.vstack(
            rx.text("📋 Penjabaran Omset Awal per Outlet Yang Aktif", font_size="14px", font_weight="bold", color="white", margin_left="5px", margin_top="5px"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nama Cabang / Outlet"),
                        rx.table.column_header_cell("Total Omset"),
                        rx.table.column_header_cell("Rata-rata Omset / Titik"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        DashboardState.statistik_per_outlet,
                        lambda toko: rx.table.row(
                            rx.table.row_header_cell(toko["nama"]),
                            rx.table.cell(toko["total"], color="#10b981", font_weight="semibold"),
                            rx.table.cell(toko["rata"], color="#3b82f6"),
                        )
                    )
                ),
                width="100%",
                variant="surface"
            ),
            width="100%",
            margin_top="10px",
            padding_bottom="20px"
        ),
        
        width="100%",
        spacing="4"
    )

def grafik_mitra_tunggal() -> rx.Component:
    """Tampilan Grafik Tunggal Mitra dengan 3 Dropdown Filter Interaktif (Hanya Data Outlet Sendiri)"""
    return rx.vstack(
        # --- PANEL FILTER DROPDOWN MITRA ---
        rx.flex(
            # Dropdown 1: Pilih Mode Grafik
            rx.vstack(
                rx.text("Mode Analisis", font_size="12px", color="gray", font_weight="bold"),
                rx.select(
                    DashboardState.opsi_mode,
                    value=DashboardState.mode_grafik,
                    on_change=lambda val: DashboardState.ganti_filter("mode", val),
                    color_scheme="blue",
                    width="110px",
                ),
                align_items="start",
            ),
            
            # Dropdown 2: Pilih Bulan (Muncul jika Mode H-M, H-B, atau M-B)
            rx.cond(
                (DashboardState.mode_grafik == "H-M") | 
                (DashboardState.mode_grafik == "H-B") | 
                (DashboardState.mode_grafik == "M-B"),
                rx.vstack(
                    rx.text("Bulan", font_size="12px", color="gray", font_weight="bold"),
                    rx.select(
                        DashboardState.opsi_bulan,
                        value=DashboardState.bulan_terpilih,
                        on_change=lambda val: DashboardState.ganti_filter("bulan", val),
                        width="140px",
                    ),
                    align_items="start",
                ),
            ),
            
            # Dropdown 3: Pilih Minggu (HANYA Muncul jika Mode murni H-M)
            rx.cond(
                DashboardState.mode_grafik == "H-M",
                rx.vstack(
                    rx.text("Pilih Minggu", font_size="12px", color="gray", font_weight="bold"),
                    rx.select(
                        DashboardState.opsi_minggu,
                        value=DashboardState.minggu_terpilih,
                        on_change=lambda val: DashboardState.ganti_filter("minggu", val),
                        width="190px",
                    ),
                    align_items="start",
                ),
            ),
            
            # Dropdown 4: Pilih Tahun Aktif (Muncul untuk H-M, H-B, M-B, dan B-T)
            rx.cond(
                DashboardState.mode_grafik != "T-T",
                rx.vstack(
                    rx.text("Tahun", font_size="12px", color="gray", font_weight="bold"),
                    rx.select(
                        DashboardState.opsi_tahun,
                        value=DashboardState.tahun_terpilih,
                        on_change=lambda val: DashboardState.ganti_filter("tahun", val),
                        width="100px",
                    ),
                    align_items="start",
                ),
            ),
            
            # Dropdown 5 & 6: Rentang Tahun Khusus (HANYA Muncul jika Mode T-T aktif)
            rx.cond(
                DashboardState.mode_grafik == "T-T",
                rx.hstack(
                    rx.vstack(
                        rx.text("Tahun Awal", font_size="12px", color="gray", font_weight="bold"),
                        rx.select(
                            DashboardState.opsi_tahun,
                            value=DashboardState.tt_tahun_awal,
                            on_change=lambda val: DashboardState.ganti_filter("tt_awal", val),
                            width="110px",
                        ),
                        align_items="start",
                    ),
                    rx.text("s/d", margin_top="25px", color="gray"),
                    rx.vstack(
                        rx.text("Tahun Akhir", font_size="12px", color="gray", font_weight="bold"),
                        rx.select(
                            DashboardState.opsi_tahun,
                            value=DashboardState.tt_tahun_akhir,
                            on_change=lambda val: DashboardState.ganti_filter("tt_akhir", val),
                            width="110px",
                        ),
                        align_items="start",
                    ),
                    spacing="3",
                ),
            ),
            
            rx.spacer(),
            
            # Tombol Tampilkan/Picu Grafik untuk Mitra
            rx.button(
                "Tampilkan Grafik", 
                color_scheme="blue", 
                size="2", 
                margin_top="18px",
                on_click=DashboardState.muat_data_grafik
            ),
            width="100%",
            spacing="4",
            background_color="rgba(255,255,255,0.02)",
            padding="15px",
            border_radius="10px",
            border="1px solid rgba(255,255,255,0.05)",
            align_items="center",
            flex_wrap="wrap",
        ),
        
        # --- PANEL RINGKASAN DATA (TOTAL & RATA-RATA) ---
        rx.grid(
            rx.vstack(
                rx.text("Total Omset", font_size="13px", color="gray"),
                rx.text(DashboardState.total_omset_tampil, font_size="22px", font_weight="bold", color="#10b981"),
                background_color="rgba(16, 185, 129, 0.05)",
                padding="15px",
                border_radius="10px",
                border="1px solid rgba(16, 185, 129, 0.15)",
                align_items="start",
                width="100%"
            ),
            rx.vstack(
                rx.text("Rata-rata Omset", font_size="13px", color="gray"),
                rx.text(DashboardState.rata_rata_omset_tampil, font_size="22px", font_weight="bold", color="#3b82f6"),
                background_color="rgba(59, 130, 246, 0.05)",
                padding="15px",
                border_radius="10px",
                border="1px solid rgba(59, 130, 246, 0.15)",
                align_items="start",
                width="100%"
            ),
            columns="2",
            spacing="4",
            width="100%",
            margin_top="10px"
        ),

        # --- PANEL UTAMA GRAFIK GARIS MITRA ---
        rx.center(
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="Omset",
                    stroke="#10b981",  # Warna hijau emerald khas mitra
                    stroke_width=2.5,
                    dot={"r": 3},
                    active_dot={"r": 6}
                ),
                rx.recharts.x_axis(data_key="Tanggal", font_size="11px", tick_margin=10),
                rx.recharts.y_axis(font_size="12px", orientation="right", tick_margin=10),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                rx.recharts.graphing_tooltip(),
                data=DashboardState.data_grafik,
                width="100%",
                height=420,
            ),
            width="100%",
            background_color="rgba(255,255,255,0.02)",
            padding="25px 15px 15px 15px",
            border_radius="12px",
            border="1px solid rgba(255,255,255,0.08)",
            margin_top="10px"
        ),
        width="100%",
        spacing="3"
    )

def konten_dashboard() -> rx.Component:
    """Memilah isi halaman berdasarkan role user yang sedang aktif"""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Dashboard Monitoring Laundry IN", size="7"),
                rx.text("Sistem berjalan dengan aman.", color="gray"),
            ),
            rx.spacer(),
            rx.button("Keluar (Logout)", color_scheme="red", variant="outline", on_click=AuthState.logout),
            width="100%",
            align_items="center"
        ),
        rx.divider(),
        
        rx.cond(
            AuthState.user_role == "owner",
            halaman_owner(),
            halaman_mitra()
        ),
        spacing="5",
        padding="30px",
        width="100%",
    )

def halaman_dashboard() -> rx.Component:
    """Halaman Utama dengan Trigger muat data grafik di awal load"""
    return rx.cond(
        AuthState.is_authenticated,
        konten_dashboard(),
        form_login()
    )

# Memicu pemuatan data grafik otomatis saat user berhasil masuk dashboard
halaman_dashboard = rx.page()(halaman_dashboard)