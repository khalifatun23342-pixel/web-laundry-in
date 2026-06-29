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
    """Tampilan khusus untuk Owner setelah login"""
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
        width="100%",
        spacing="4"
    )

def halaman_mitra() -> rx.Component:
    """Tampilan Grafik Batang Utama Distribusi Omset Cabang"""
    return rx.vstack(
        rx.hstack(
            rx.text("Grafik Perbandingan Capaian Omset per Cabang/Outlet:", font_size="16px", font_weight="medium"),
            rx.spacer(),
            # TOMBOL PENYELAMAT: Untuk memicu grafik jika on_load browser macet
            rx.button(
                "Tampilkan Grafik", 
                color_scheme="blue", 
                size="2",
                on_click=DashboardState.muat_data_grafik
            ),
            width="100%",
            align_items="center"
        ),
        
        # PENYUSUNAN GRAFIK RECHARTS UTAMA PROYEK
        rx.center(
            rx.recharts.bar_chart(
                rx.recharts.bar(
                    data_key="Omset", 
                    stroke="#3b82f6", 
                    fill="#3b82f6",
                    radius=[4, 4, 0, 0]
                ),
                rx.recharts.x_axis(data_key="name", font_size="12px"),
                rx.recharts.y_axis(font_size="12px"),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                rx.recharts.graphing_tooltip(),
                data=DashboardState.data_grafik,
                width="100%",
                height=350,
            ),
            width="100%",
            background_color="rgba(255,255,255,0.03)",
            padding="20px",
            border_radius="12px",
            border="1px solid rgba(255,255,255,0.1)"
        ),
        width="100%",
        spacing="4"
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
halaman_dashboard = rx.page(
    on_load=DashboardState.muat_data_grafik
)(halaman_dashboard)