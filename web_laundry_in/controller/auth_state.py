import reflex as rx

class AuthState(rx.State):
    is_authenticated: bool = False
    user_role: str = ""
    pesan_error: str = ""

    def login_mitra_form(self, form_data: dict):
        """Reflex otomatis mengambil isi input berdasarkan nama komponennya"""
        pin = form_data.get("input_pin", "")
        
        if pin == "1969":
            self.is_authenticated = True
            self.user_role = "mitra"
            self.pesan_error = ""
            return rx.redirect("/")
        else:
            self.pesan_error = "Kode PIN 4 angka salah atau tidak terdaftar!"

    def login_owner_form(self, form_data: dict):
        """Reflex otomatis mengambil isi input berdasarkan nama komponennya"""
        username = form_data.get("input_user", "")
        password = form_data.get("input_pass", "")
        
        if username == "admin" and password == "123":
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