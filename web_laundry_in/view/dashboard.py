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
    """Tampilan Grafik Garis Tunggal Urut Tanggal - Terkunci khusus Mitra"""
    from ..controller.auth_state import AuthState
    
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Tren Capaian Omset Harian (Urutan Tanggal Penuh)", font_size="18px", font_weight="bold"),
                rx.text("Outlet Mitra: " + AuthState.nama_outlet_aktif, color="gray", font_size="14px"),
            ),
            rx.spacer(),
            rx.button("Tampilkan Grafik", color_scheme="blue", size="2", on_click=DashboardState.muat_data_grafik),
            width="100%",
            align_items="center"
        ),
        rx.center(
            rx.recharts.line_chart(
                rx.recharts.line(data_key="Omset", stroke="#10b981", stroke_width=3, dot={"r": 3}, active_dot={"r": 6}),
                rx.recharts.x_axis(data_key="Tanggal", font_size="11px", tick_margin=10),
                rx.recharts.y_axis(font_size="12px", orientation="right", tick_margin=10),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                rx.recharts.graphing_tooltip(),
                data=DashboardState.data_grafik,
                width="100%",
                height=380,
            ),
            width="100%",
            background_color="rgba(255,255,255,0.02)",
            padding="25px 15px 15px 15px",
            border_radius="12px",
            border="1px solid rgba(255,255,255,0.08)",
            margin_top="15px"
        ),
        width="100%",
        spacing="4"
    )

def grafik_owner_tumpuk() -> rx.Component:
    """Tampilan Grafik Multi-Garis Dinamis dengan 3 Dropdown Filter Interaktif Cerdas"""
    return rx.vstack(
        # --- PANEL FILTER DROPDOWN BARU (Ditempatkan di Atas Grafik) ---
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
            
            # Dropdown 2: Pilih Bulan (Hanya Muncul jika Mode H-M, H-B, atau M-B)
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
            
            # Tombol Picu Muat Data Manual (Sebagai backup)
            rx.button(
                "Picu Muat Grafik", 
                color_scheme="green", 
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
        
        # --- PANEL UTAMA VISUALISASI GRAFIK RECHARTS ---
        rx.center(
            rx.recharts.line_chart(
                rx.foreach(
                    DashboardState.daftar_outlet_warna,
                    lambda item: rx.recharts.line(
                        data_key=item["nama"],
                        stroke=item["warna"],
                        stroke_width=2.5,
                        dot={"r": 2},
                        active_dot={"r": 5}
                    )
                ),
                rx.recharts.x_axis(data_key="Tanggal", font_size="11px", tick_margin=10),
                rx.recharts.y_axis(font_size="12px", orientation="right", tick_margin=10),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(vertical_align="bottom", height=45, margin_top=15),
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