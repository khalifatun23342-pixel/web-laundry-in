import reflex as rx

config = rx.Config(
    app_name="web_laundry_in",
    # PAKSA REFLEX MENYEDIAKAN DATABASE SQLITE LOKAL SECARA PERMANEN
    db_url="sqlite:///reflex.db", 
)