import reflex as rx

class AuthState(rx.State):
    is_authenticated: bool = False
    user_role: str = ""
    pesan_error: str = ""
    # Sesuaikan atau tambahkan variabel penampung nama outlet mitra yang sedang login
    nama_outlet_aktif: str = ""

    async def login_mitra_form(self, form_data: dict):
        pin = form_data.get("input_pin", "").strip()
        self.pesan_error = ""
        
        # Ambil state dashboard secara asinkronus hanya SEKALI saat proses klik tombol login
        from .dashboard_state import DashboardState
        dashboard_state = await self.get_state(DashboardState)
        
        if pin == "6465":
            self.is_authenticated = True
            self.user_role = "mitra"
            self.nama_outlet_aktif = "Semampir"
            
            # SET LANGSUNG KE DATA LOKAL DASHBOARD STATE
            dashboard_state.outlet_aktif_lokal = "Semampir"
            dashboard_state.muat_data_grafik() # Picu muat datanya dari sini langsung!
            return rx.redirect("/")
            
        elif pin == "1969":
            self.is_authenticated = True
            self.user_role = "mitra"
            self.nama_outlet_aktif = "Kaliombo"
            
            # SET LANGSUNG KE DATA LOKAL DASHBOARD STATE
            dashboard_state.outlet_aktif_lokal = "Kaliombo"
            dashboard_state.muat_data_grafik() # Picu muat datanya dari sini langsung!
            return rx.redirect("/")
            
        else:
            self.pesan_error = "PIN yang Anda masukkan salah!"

    async def login_owner_form(self, form_data: dict):
        """Reflex otomatis mengambil isi input berdasarkan nama komponennya"""
        username = form_data.get("input_user", "")
        password = form_data.get("input_pass", "")
        
        if username == "admin" and password == "123":
            from .dashboard_state import DashboardState
            dashboard_state = await self.get_state(DashboardState)
            dashboard_state.outlet_aktif_lokal = "" # Kosongkan agar membaca seluruh outlet
            dashboard_state.muat_data_grafik()
            
            self.is_authenticated = True
            self.user_role = "owner"
            self.pesan_error = ""
            return rx.redirect("/")
        else:
            self.pesan_error = "Username atau Password Owner salah!"

    def logout(self):
        """Fungsi keluar akun"""
        self.is_authenticated = False
        self.user_role = ""
        self.pesan_error = ""
        return rx.redirect("/")