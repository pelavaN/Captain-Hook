#!/usr/bin/env python3
"""
kirmizi_quickbuttons.py
Geliştirilmiş Apple-like quick-message uygulaması
- Giriş ekranı (ID/PASS, varsayılan BURAK/BURAK)
- Kimlik kaydetme (config)
- Gün içinde buton tıklama logu (usage_logs.json)
- Daha okunaklı metin gösterimi ve profesyonel görünüm

Gereksinimler: customtkinter, pyperclip
Kurulum: python -m pip install customtkinter pyperclip
"""

import customtkinter as ctk
from functools import partial
import pyperclip
import threading
import textwrap
import json
import os
import datetime
import sys
import shutil
import tempfile

# ---------------- MESSAGES (1..29) ----------------
MESSAGES = {
    "1": "Merhaba, iyi günler. Size nasıl yardımcı olabiliriz?",
    "2": "Merhaba, renk ve beden seçiminiz nedir? Stoklar incelensin yardımcı olalım.",
    "3": "Ürün görsellerini görüntüleyemiyoruz. Lütfen ekran görüntüsü olarak tekrar gönderebilir misiniz, efendim?",
    "4": "Merhaba iyi günler. Faturanızın sol üstünde bulunan 9 haneli sipariş numaranızı, kullanılan ad soyad ve iletişim numaranızı iletir misiniz? Kontrol edelim.",
    "5": "Merhaba, bu model stoklarımızda yok. Güncel modeller için kirmizionline.com adresini ziyaret edebilirsiniz.",
    "6": "Instagram açıklamasındaki kod ile https://www.kirmizionline.com adresinden ürün/renk/fiyat bilgilerini kontrol edebilirsiniz.",
    "7": "İade veya değişim paketiniz ulaşmış. Lütfen sipariş kodunuzu ve gönderilen ürünlerin görsellerini paylaşır mısınız?",
    "8": "İade/değişim için WhatsApp hattımızdan destek alabilirsiniz: https://api.whatsapp.com/send?phone=905412243400",
    "9": "Buradan yalnızca online ürünlerimiz satın alınır. Mağaza stokları için mağazayı ziyaret etmenizi öneririz.",
    "10": "Siparişler genellikle 1 iş günü sonra kargolanır, teslim süresi 2-5 iş günüdür. Takip kodu yola çıktıktan sonra SMS ile gönderilir.",
    "11": "Stok güncellemeleri hakkında net bir zaman veremiyoruz; güncellemeler Instagram hesabımızda paylaşılır.",
    "12": "İade edilen tutar, işlem yapılan karta 1-7 iş günü içinde yansır.",
    "13": "Fiyatlarımız sabittir. Web sitemizde indirim veya kampanyaları kontrol edebilirsiniz.",
    "14": "Adres: Kartaltepe Mah. 50. Yıl Cad. No:48/C Bayrampaşa/İstanbul",
    "15": "Modelin renk, beden ve fiyat bilgilerine siteden ulaşabilirsiniz.",
    "16": "Sistemde geçici problem var; ürünleri site üzerinden sepete ekleyip sipariş verebilirsiniz. WhatsApp: +905412243400",
    "17": "Satın almak istiyorsanız ürünleri siteye ekleyip sepet ekran görüntüsünü WhatsApp'a gönderebilirsiniz.",
    "18": "2000₺'ye kadar nakit, üzeri için FAST veya kart ile ödeme yapılmaktadır.",
    "19": "Ürününüz üreticiden kaynaklı gecikme yaşadıysa, kısa sürede paketine eklenecektir. Anlayışınız için teşekkürler.",
    "20": "Kampanya ve duyurular için Instagram: @kirmiziibutiks ve www.kirmizionline.com adresini takip edin.",
    "21": "İade için IBAN ve kart sahibi bilgilerinizi paylaşmanız gerekmektedir.",
    "22": "Sitede seçilemeyen (üstü çizili) bedenler satışta değildir.",
    "23": "Manken: 36/S — Boy:160 cm — Kilo:50 — Göğüs:75 — Bel:62 — Basen:95",
    "24": "İade ve değişim prosedürleri için web sitemizdeki ilgili sayfayı inceleyebilirsiniz.",
    "25": "Kargonuzu linkten takip edebilirsiniz; takip kodu SMS ile de iletilir.",
    "26": "Ödemeniz kontrol edilip sipariş onayı tarafınıza iletilecektir.",
    "27": "Kargo kodu kargo firması tarafından iletilmiştir; firmadan sorgulayarak takip edebilirsiniz.",
    "28": "Sipariş kağıdı yoksa ad-soyad, telefon ve sipariş kodunu bir kağıda yazıp pakete ekleyebilirsiniz.",
    "29": "Cayma hakkı ürün tesliminden itibaren 14 gündür. Süre geçmişse iade sağlanamayabilir."
}

# ---------------- THEMES ----------------
THEMES = {
    "Apple Light": {"appearance": "light", "accent": "#0a84ff", "bg": "#f6f6f7", "card": "#ffffff", "text": "#111111"},
    "Settings Soft": {"appearance": "light", "accent": "#8e8e93", "bg": "#f2f2f7", "card": "#ffffff", "text": "#111111"},
    "Dark Purple": {"appearance": "dark", "accent": "#7f5af0", "bg": "#0f0b12", "card": "#111217", "text": "#eae6ff"}
}

# ---------------- Config / Logs ----------------
def _resolve_paths():
    """
    Resolve CONFIG_PATH and LOGS_PATH with these rules:
    - If a `kh_config.json` exists in the current working directory, use it (external editable).
    - Else if running as a PyInstaller onefile executable, try to load bundled config from sys._MEIPASS and extract it to cwd for editing.
    - Otherwise fall back to the script directory files.
    Logs are preferentially stored next to the executable / cwd so they persist across runs.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()

    external_config = os.path.join(cwd, "kh_config.json")
    external_logs = os.path.join(cwd, "usage_logs.json")

    # If external config already exists, prefer it
    if os.path.exists(external_config):
        config_path = external_config
    else:
        # If running frozen (PyInstaller --onefile), bundled files are in _MEIPASS
        if getattr(sys, 'frozen', False):
            meipass = getattr(sys, '_MEIPASS', None)
            if meipass:
                bundled = os.path.join(meipass, "kh_config.json")
                if os.path.exists(bundled):
                    # try to extract to cwd for user edit, fallback to bundled path
                    try:
                        shutil.copyfile(bundled, external_config)
                        config_path = external_config
                    except Exception:
                        config_path = bundled
                else:
                    config_path = bundled if os.path.exists(bundled) else os.path.join(script_dir, "kh_config.json")
            else:
                config_path = os.path.join(script_dir, "kh_config.json")
        else:
            config_path = os.path.join(script_dir, "kh_config.json")

    # For logs, prefer writing to cwd so the file is easy to find/inspect
    logs_path = external_logs
    # make sure logs path directory is writable
    try:
        open(logs_path, 'a').close()
    except Exception:
        # fallback to script dir
        logs_path = os.path.join(script_dir, "usage_logs.json")

    return config_path, logs_path


WORKDIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH, LOGS_PATH = _resolve_paths()

DEFAULT_CRED = {"id":"BURAK","pass":"BURAK"}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    # if config not present on disk but bundled exists (when frozen), try to read it
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            bundled = os.path.join(meipass, "kh_config.json")
            if os.path.exists(bundled):
                try:
                    with open(bundled, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    # attempt to write extracted copy to cwd for convenience
                    try:
                        with open(os.path.join(os.getcwd(), "kh_config.json"), "w", encoding="utf-8") as out:
                            json.dump(data, out, ensure_ascii=False, indent=2)
                        # update global path so future saves go to extracted file
                        global CONFIG_PATH
                        CONFIG_PATH = os.path.join(os.getcwd(), "kh_config.json")
                    except Exception:
                        pass
                    return data
                except Exception:
                    return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_logs():
    if os.path.exists(LOGS_PATH):
        try:
            with open(LOGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_logs(logs):
    try:
        with open(LOGS_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def today_key():
    return datetime.date.today().isoformat()

class AppleishApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("kirmizionline • Quick Panel")
        self.geometry("1180x720")
        self.minsize(980,600)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # config & logs
        self.config_data = load_config()
        self.logs = load_logs()
        if not isinstance(self.logs, dict):
            self.logs = {}

        # theme
        self.current_theme = self.config_data.get("theme", "Dark Purple")
        self._apply_theme(self.current_theme)

        # show login (may auto-login if config asks)
        auto = self.config_data.get("auto_login", False)
        if auto and self._validate_saved_credentials():
            pass  # skip login
        else:
            if not self._show_login():
                self.destroy()
                return

        # build UI after successful login
        self._build_ui()

    def _apply_theme(self, theme_name):
        t = THEMES.get(theme_name, list(THEMES.values())[0])
        self.appearance = t["appearance"]
        ctk.set_appearance_mode(self.appearance)
        self.accent = t["accent"]
        self.bg_color = t["bg"]
        self.card_color = t["card"]
        self.text_color = t["text"]
        self.configure(fg_color=self.bg_color)

    def _validate_saved_credentials(self):
        saved = self.config_data.get("cred")
        if not saved:
            return False
        return saved.get("id") == DEFAULT_CRED["id"] and saved.get("pass") == DEFAULT_CRED["pass"]

    def _show_login(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Giriş — kirmizionline")
        dlg.geometry("420x260")
        dlg.transient(self)
        dlg.grab_set()

        # prefill from config or default
        pref = self.config_data.get("cred", DEFAULT_CRED)

        lbl = ctk.CTkLabel(dlg, text="Lütfen giriş yapın", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(pady=(18,8))

        frm = ctk.CTkFrame(dlg, fg_color=self.card_color, corner_radius=8)
        frm.pack(padx=16, pady=8, fill="x")

        entry_id = ctk.CTkEntry(frm, placeholder_text="ID", textvariable=ctk.StringVar(value=pref.get("id","")))
        entry_id.pack(fill="x", padx=12, pady=(10,6))
        entry_pw = ctk.CTkEntry(frm, placeholder_text="Şifre", show="*", textvariable=ctk.StringVar(value=pref.get("pass","")))
        entry_pw.pack(fill="x", padx=12, pady=(0,10))

        save_var = ctk.BooleanVar(value=self.config_data.get("save_cred", False))
        chk = ctk.CTkCheckBox(frm, text="Kimliği kaydet", variable=save_var)
        chk.pack(anchor="w", padx=12, pady=(0,8))

        status_lbl = ctk.CTkLabel(dlg, text="", font=ctk.CTkFont(size=12))
        status_lbl.pack(pady=(0,6))

        def try_login():
            uid = entry_id.get().strip()
            pwd = entry_pw.get().strip()
            if uid == DEFAULT_CRED["id"] and pwd == DEFAULT_CRED["pass"]:
                # success
                if save_var.get():
                    self.config_data["cred"] = {"id": uid, "pass": pwd}
                    self.config_data["save_cred"] = True
                else:
                    self.config_data.pop("cred", None)
                    self.config_data["save_cred"] = False
                save_config(self.config_data)
                dlg.grab_release()
                dlg.destroy()
                return True
            else:
                status_lbl.configure(text="Hatalı kimlik bilgileri", text_color="#ff6666")
                return False

        btn_frame = ctk.CTkFrame(dlg, fg_color=self.bg_color, corner_radius=0)
        btn_frame.pack(fill="x", padx=16, pady=(4,12))

        btn_login = ctk.CTkButton(btn_frame, text="Giriş", command=lambda: try_login())
        btn_login.pack(side="right")
        btn_cancel = ctk.CTkButton(btn_frame, text="Çıkış", fg_color="#aaaaaa", command=lambda: (dlg.destroy()))
        btn_cancel.pack(side="right", padx=(0,8))

        self.wait_window(dlg)
        # if dialog destroyed, check if credentials saved or valid
        return self._validate_saved_credentials() or self.config_data.get("save_cred", False)

    def _build_ui(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=self.bg_color, corner_radius=0)
        top.pack(fill="x", padx=10, pady=(8,6))

        title = ctk.CTkLabel(top, text="kirmizionline", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.accent)
        title.grid(row=0, column=0, sticky="w", padx=(6,12))

        theme_box = ctk.CTkOptionMenu(top, values=list(THEMES.keys()), command=self.change_theme)
        theme_box.grid(row=0, column=1, sticky="e", padx=12)
        theme_box.set(self.current_theme)

        report_btn = ctk.CTkButton(top, text="Günlük Rapor", command=self.show_report, width=120)
        report_btn.grid(row=0, column=2, sticky="e", padx=6)

        # Main frame
        main = ctk.CTkFrame(self, fg_color=self.bg_color, corner_radius=0)
        main.pack(fill="both", expand=True, padx=10, pady=8)

        # Left card: buttons
        left_card = ctk.CTkFrame(main, fg_color=self.card_color, corner_radius=12)
        left_card.place(relx=0.02, rely=0.03, relwidth=0.46, relheight=0.88)

        left_title = ctk.CTkLabel(left_card, text="Kategoriler", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.text_color)
        left_title.pack(anchor="nw", padx=14, pady=(12,6))

        left_scroll = ctk.CTkScrollableFrame(left_card)
        left_scroll.pack(fill="both", expand=True, padx=12, pady=8)

        left_keys = ["1","2","4","5","6","7","8","10","11","12","15","16","17","18","19","24","25","26","27","28","29"]
        for k in left_keys:
            self._make_card_button(left_scroll, k)

        # Right card: general
        right_card = ctk.CTkFrame(main, fg_color=self.card_color, corner_radius=12)
        right_card.place(relx=0.52, rely=0.03, relwidth=0.46, relheight=0.88)

        right_title = ctk.CTkLabel(right_card, text="Genel Yanıtlar & Önizleme", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.text_color)
        right_title.pack(anchor="nw", padx=14, pady=(12,6))

        right_scroll = ctk.CTkScrollableFrame(right_card)
        right_scroll.pack(fill="both", expand=True, padx=12, pady=8)

        right_keys = ["3","9","13","14","20","21","22","23","24","25","26","27"]
        for k in right_keys:
            self._make_card_button(right_scroll, k)

        # Preview panel at bottom
        preview_frame = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=12)
        preview_frame.pack(fill="x", padx=10, pady=(0,10))
        preview_label = ctk.CTkLabel(preview_frame, text="Metin Önizlemesi", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.text_color)
        preview_label.pack(anchor="nw", padx=12, pady=(8,0))

        self.preview_box = ctk.CTkTextbox(preview_frame, width=100, height=120, fg_color=self.card_color, text_color=self.text_color, corner_radius=8)
        self.preview_box.pack(fill="both", expand=True, padx=12, pady=(6,12))
        self.preview_box.configure(state="disabled")

        # footer
        footer = ctk.CTkLabel(self, text="Since 2025 • Burak BEKER", text_color=self.text_color, font=ctk.CTkFont(size=10, weight="bold"))
        footer.pack(side="bottom", pady=(0,8))

        # toast
        self.toast = ctk.CTkLabel(self, text="", text_color=self.accent, font=ctk.CTkFont(size=12, weight="bold"))
        self.toast.place(relx=0.98, rely=0.98, anchor="se")

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self._apply_theme(theme_name)
        self.config_data["theme"] = theme_name
        save_config(self.config_data)
        self.toast.configure(text_color=self.accent)

    def _make_card_button(self, parent, key):
        full = MESSAGES.get(key, "—")
        short = self._short_label(full)
        icon = "📋"
        if key in ["10","25","27","26","19","24","29"]:
            icon = "📦"
        if key in ["8","7","12","21"]:
            icon = "💳"
        if key in ["3","16"]:
            icon = "📷"
        if key in ["23"]:
            icon = "👗"

        btn_text = f"{icon}  {key}. {short}"
        btn = ctk.CTkButton(parent, text=btn_text, command=partial(self._on_click, key, full),
                            fg_color=self.card_color, hover_color=self.accent, text_color=self.text_color,
                            height=56, corner_radius=14, border_width=1, border_color=self.accent)
        btn.pack(fill="x", padx=6, pady=8)

    def _short_label(self, full):
        s = " ".join(full.split())
        return (s[:70] + "...") if len(s) > 70 else s

    def _on_click(self, key, text):
        try:
            pyperclip.copy(text)
            self._show_toast("Kopyalandı ✅")
        except Exception:
            self._show_toast("Pano hatası ❌")
        # update preview
        self._set_preview(text)
        # log click
        self._log_click(key)

    def _set_preview(self, text):
        self.preview_box.configure(state="normal")
        self.preview_box.delete("0.0", "end")
        wrapped = textwrap.fill(text, width=80)
        self.preview_box.insert("0.0", wrapped)
        self.preview_box.configure(state="disabled")

    def _show_toast(self, msg, sec=1.2):
        self.toast.configure(text=msg)
        def _clear():
            import time
            time.sleep(sec)
            try:
                self.toast.configure(text="")
            except:
                pass
        threading.Thread(target=_clear, daemon=True).start()

    def _log_click(self, key):
        date = today_key()
        if date not in self.logs:
            self.logs[date] = {"counts":{}, "events": []}
        counts = self.logs[date].setdefault("counts", {})
        counts[key] = counts.get(key, 0) + 1
        # store event with timestamp
        evt = {"key": key, "time": datetime.datetime.now().isoformat()}
        self.logs[date].setdefault("events", []).append(evt)

        # save logs asynchronously
        threading.Thread(target=save_logs, args=(self.logs,), daemon=True).start()

    def show_report(self):
        rpt = ctk.CTkToplevel(self)
        rpt.title("Günlük Rapor")
        rpt.geometry("500x480")
        rpt.transient(self)

        lbl = ctk.CTkLabel(rpt, text=f"Tarih: {today_key()}", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(pady=(12,8))

        box = ctk.CTkTextbox(rpt, width=460, height=360, fg_color=self.card_color, text_color=self.text_color)
        box.pack(padx=12, pady=8)
        box.configure(state="normal")

        data = self.logs.get(today_key(), {})
        counts = data.get("counts", {})
        if not counts:
            box.insert("0.0", "Bugün henüz herhangi bir butona tıklamadınız.")
        else:
            lines = [f"Buton {k}: {v} kez" for k,v in sorted(counts.items(), key=lambda x: int(x[0]))]
            box.insert("0.0", "\n".join(lines))

        box.configure(state="disabled")

    def on_close(self):
        save_logs(self.logs)
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = AppleishApp()
    try:
        app.mainloop()
    except Exception:
        pass
