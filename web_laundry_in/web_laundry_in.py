import reflex as rx
from .view.dashboard import halaman_dashboard

app = rx.App()
app.add_page(halaman_dashboard, route="/")