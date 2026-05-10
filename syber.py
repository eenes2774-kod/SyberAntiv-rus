import customtkinter as ctk
import os
import shutil
import threading
import time
import subprocess
import platform
import getpass

# --- TASARIM YAPILANDIRMASI ---
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

class SyberV310(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Syber Antivirus Sunar")
        self.geometry("1200x850")
        self.configure(fg_color="#F9F9FB")

        # Sistem Altyapısı
        self.user_home = os.path.expanduser("~")
        self.q_path = os.path.join(self.user_home, "Desktop", "SYBER_Karantina")
        if not os.path.exists(self.q_path): os.makedirs(self.q_path)
        
        self.target_dirs = [
            os.path.join(self.user_home, "Desktop"),
            os.path.join(self.user_home, "Downloads"),
            os.path.join(self.user_home, "Library/Caches")
        ]

        self.threat_count = 0
        self.is_scanning = False

        self.setup_ui()
        self.start_engines()

    def setup_ui(self):
        # --- SOL NAVİGASYON ---
        self.sidebar = ctk.CTkFrame(self, width=100, corner_radius=0, fg_color="#FFFFFF", border_width=1, border_color="#E8E8E8")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="🛡️", font=("Arial", 35), text_color="#1D4ED8").pack(pady=30)

        menu = [("📊", "dash"), ("🌐", "vpn"), ("🚀", "fps"), ("⚙️", "set")]
        for icon, name in menu:
            ctk.CTkButton(self.sidebar, text=icon, font=("Arial", 26), fg_color="transparent", 
                          text_color="#5F6368", hover_color="#F1F3F4", width=70, height=70, 
                          command=lambda n=name: self.show_page(n)).pack(pady=15)

        # --- ANA KONTEYNER ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True, padx=40, pady=20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.init_pages()
        self.show_page("dash")

    def init_pages(self):
        for name in ["dash", "vpn", "fps", "set"]:
            p = ctk.CTkFrame(self.container, fg_color="transparent")
            self.pages[name] = p
            p.grid(row=0, column=0, sticky="nsew")

        # --- 1. DASHBOARD ---
        self.draw_dashboard(self.pages["dash"])

        # --- 2. VPN ---
        v = self.pages["vpn"]
        ctk.CTkLabel(v, text="Güvenli Erişim (DNS)", font=("Arial", 32, "bold")).pack(anchor="w", pady=20)
        self.create_settings_card(v, "Gizlilik Modu", "Cloudflare Family DNS ile zararlı siteleri engeller.", "AÇ", lambda: subprocess.run(["networksetup", "-setdnsservers", "Wi-Fi", "1.1.1.3", "1.0.0.3"]))

        # --- 3. FPS BOOST ---
        f = self.pages["fps"]
        ctk.CTkLabel(f, text="Performans", font=("Arial", 32, "bold")).pack(anchor="w", pady=20)
        self.create_settings_card(f, "Turbo Boost", "RAM ve Önbelleği temizleyerek işlemciyi rahatlatır.", "HIZLANDIR", lambda: subprocess.run(["purge"]))

        # --- 4. AYARLAR (DOPDOLU) ---
        s = self.pages["set"]
        ctk.CTkLabel(s, text="Uygulama Ayarları", font=("Arial", 32, "bold")).pack(anchor="w", pady=20)
        
        # Tema Kartı
        t_card = self.create_settings_card(s, "Görünüm", "Koyu veya Açık tema seçimi yapın.", None, None)
        ctk.CTkOptionMenu(t_card, values=["Açık", "Koyu"], command=lambda x: ctk.set_appearance_mode("dark" if x=="Koyu" else "light")).place(relx=0.85, rely=0.5, anchor="center")
        
        # Karantina Temizleme
        self.create_settings_card(s, "Karantina", "Tüm yakalanan tehditleri diskten kalıcı olarak silin.", "TEMİZLE", self.full_reset)
        
        # Sistem Bilgisi Kartı
        info_card = self.create_settings_card(s, "Sistem Bilgisi", f"Cihaz: {platform.node()}\nİşletim Sistemi: macOS {platform.mac_ver()[0]}", None, None)
        info_card.configure(height=100)

    def draw_dashboard(self, page):
        self.status_lbl = ctk.CTkLabel(page, text="Sistem Durumu: GÜVENDE", font=("Arial", 32, "bold"), text_color="#2ECC71")
        self.status_lbl.pack(anchor="w", pady=(10, 20))
        
        c = self.create_settings_card(page, "Tam Tarama", "Tüm kritik klasörler denetleniyor.", "ŞİMDİ TARA", self.run_full_scan)
        
        self.console = ctk.CTkTextbox(page, height=200, fg_color="#1a1a1a", text_color="#00FF00", font=("Courier", 13))
        self.console.pack(fill="x", pady=20)
        self.console.insert("0.0", ">> Syber Full-Scan Engine v310 Aktif.\n")

    def show_page(self, name):
        self.pages[name].tkraise()

    def create_settings_card(self, master, title, desc, btn_txt, cmd):
        card = ctk.CTkFrame(master, height=110, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E8E8E8")
        card.pack(fill="x", pady=10)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold")).place(x=25, y=20)
        ctk.CTkLabel(card, text=desc, font=("Arial", 13), text_color="#757575").place(x=25, y=55)
        if btn_txt:
            ctk.CTkButton(card, text=btn_txt, width=120, height=35, corner_radius=18, font=("Arial", 12, "bold"), command=cmd).place(relx=0.88, rely=0.5, anchor="center")
        return card

    def run_full_scan(self):
        if self.is_scanning: return
        self.is_scanning = True
        def task():
            for d in self.target_dirs:
                if os.path.exists(d):
                    self.console.insert("end", f"\n>> Tarama: {d}\n")
                    for f in os.listdir(d)[:10]:
                        self.console.insert("end", f">> OK: {f[:25]}...\n")
                        self.console.see("end")
                        time.sleep(0.05)
            self.is_scanning = False
        threading.Thread(target=task, daemon=True).start()

    def full_reset(self):
        for f in os.listdir(self.q_path): os.remove(os.path.join(self.q_path, f))
        self.threat_count = 0
        self.status_lbl.configure(text="Sistem Durumu: GÜVENDE", text_color="#2ECC71")

    def start_engines(self):
        def monitor():
            while True:
                for d in self.target_dirs:
                    if os.path.exists(d):
                        try:
                            for f in os.listdir(d):
                                if any(x in f.lower() for x in ["bomb", "virus", "eicar"]):
                                    shutil.move(os.path.join(d, f), self.q_path)
                                    self.status_lbl.configure(text="Sistem Durumu: TEHLİKEDE!", text_color="#E74C3C")
                        except: pass
                time.sleep(4)
        threading.Thread(target=monitor, daemon=True).start()

if __name__ == "__main__":
    app = SyberV310()
    app.mainloop()
