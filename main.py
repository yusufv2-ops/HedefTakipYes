# -*- coding: utf-8 -*-
import sqlite3
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta

# Kivy ve KivyMD bileşenleri
from kivy.lang import Builder
from kivy.core.image import Image as CoreImage
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import TwoLineListItem, OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField

# --- TASARIM (KV) ---
KV = '''
MDScreenManager:
    LoginScreen:
    MainScreen:
    AdminScreen:
    StatsScreen:

<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "10dp"
        MDLabel:
            text: "HEDEF TAKİP YES"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Primary"
        MDLabel:
            text: "Profil Seçiniz"
            halign: "center"
            font_style: "H6"
        MDScrollView:
            MDList:
                id: profile_list
        MDRaisedButton:
            text: "Yeni Profil Ekle"
            pos_hint: {"center_x": .5}
            on_release: app.show_add_user_dialog()
        MDLabel:
            text: "Copyright © Yusuf VARKAL"
            halign: "center"
            font_style: "Caption"

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: 'vertical'
        padding: "15dp"
        spacing: "10dp"
        MDTopAppBar:
            id: toolbar
            title: "HEDEF TAKİP YES"
            left_action_items: [["account-switch", lambda x: app.logout()]]
            right_action_items: [["chart-bar", lambda x: app.go_to_stats()], ["cog", lambda x: app.go_to_admin()]]

        MDBoxLayout:
            adaptive_height: True
            MDLabel:
                id: date_label
                text: "Tarih: " + app.selected_date
            MDIconButton:
                icon: "calendar-edit"
                on_release: app.show_date_picker("main")

        MDRaisedButton:
            id: target_drop
            text: "Hedef Seçin"
            pos_hint: {"center_x": .5}
            size_hint_x: 0.9
            on_release: app.main_menu.open()

        MDTextField:
            id: amount_input
            hint_text: "Miktar Girin"
            input_filter: "int"
            mode: "rectangle"

        MDRaisedButton:
            text: "KAYDET"
            md_bg_color: 0, .5, 0, 1
            pos_hint: {"center_x": .5}
            size_hint_x: 0.7
            on_release: app.save_progress()
        
        MDLabel:
            text: "Copyright © Yusuf VARKAL"
            halign: "center"
            font_style: "Caption"
        Widget:

<AdminScreen>:
    name: "admin"
    MDBoxLayout:
        orientation: 'vertical'
        padding: "15dp"
        spacing: "10dp"
        MDLabel:
            id: admin_label
            text: "Profil Yönetimi"
            halign: "center"
            font_style: "H6"
        
        MDTextField:
            id: target_input
            hint_text: "Bu Profil İçin Yeni Hedef"
        
        MDRaisedButton:
            text: "HEDEFİ EKLE"
            pos_hint: {"center_x": .5}
            on_release: app.add_target_to_user()

        MDLabel:
            text: "Hedefleriniz (Silmek için tıklayın)"
            font_style: "Caption"
            halign: "center"

        MDScrollView:
            MDList:
                id: user_target_list

        MDRaisedButton:
            text: "ANA MENÜYE DÖN"
            pos_hint: {"center_x": .5}
            on_release: root.manager.current = "main"

<StatsScreen>:
    name: "stats"
    MDBoxLayout:
        orientation: 'vertical'
        padding: "10dp"
        MDBoxLayout:
            adaptive_height: True
            spacing: "5dp"
            MDRaisedButton:
                id: stats_target_drop
                text: "İş Seç"
                on_release: app.stats_menu.open()
            MDRaisedButton:
                text: "Hafta"
                on_release: app.update_range(7)
            MDRaisedButton:
                text: "Ay"
                on_release: app.update_range(30)
            MDIconButton:
                icon: "calendar-search"
                on_release: app.show_date_picker("stats")

        MDCard:
            size_hint_y: 0.5
            elevation: 1
            Image:
                id: chart_img
                allow_stretch: True

        MDScrollView:
            MDList:
                id: data_list
        MDRaisedButton:
            text: "GERİ"
            pos_hint: {"center_x": .5}
            on_release: root.manager.current = "main"
'''

class LoginScreen(MDScreen): pass
class MainScreen(MDScreen): pass
class AdminScreen(MDScreen): pass
class StatsScreen(MDScreen): pass

class TargetApp(MDApp):
    selected_date = datetime.now().strftime('%Y-%m-%d')
    stats_start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    current_user = None
    current_stats_target = None
    user_dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.init_db()
        self.root_widget = Builder.load_string(KV)
        self.refresh_profiles()
        return self.root_widget

    def init_db(self):
        self.conn = sqlite3.connect("personal_targets.db")
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS user_targets (user TEXT, target_name TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS logs (user TEXT, date TEXT, target TEXT, amount INTEGER)")
        self.conn.commit()

    def refresh_profiles(self):
        self.cur.execute("SELECT name FROM users")
        users = self.cur.fetchall()
        lst = self.root_widget.get_screen('login').ids.profile_list
        lst.clear_widgets()
        for user in users:
            lst.add_widget(OneLineIconListItem(text=user[0], on_release=lambda x, u=user[0]: self.login(u)))

    def login(self, username):
        self.current_user = username
        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.current_stats_target = None
        
        main_ids = self.root_widget.get_screen('main').ids
        main_ids.toolbar.title = f"HEDEF TAKİP YES: {username}"
        main_ids.date_label.text = "Tarih: " + self.selected_date
        main_ids.target_drop.text = "Hedef Seçin"
        main_ids.amount_input.text = ""
        
        self.root_widget.get_screen('admin').ids.admin_label.text = f"{username} - Hedef Yönetimi"
        self.root_widget.get_screen('stats').ids.stats_target_drop.text = "İş Seç"
        self.root_widget.get_screen('stats').ids.data_list.clear_widgets()
        self.root_widget.get_screen('stats').ids.chart_img.texture = None

        self.load_menus()
        self.root_widget.current = "main"

    def logout(self):
        self.current_user = None
        self.refresh_profiles()
        self.root_widget.current = "login"

    def show_add_user_dialog(self):
        self.user_input = MDTextField(hint_text="Profil İsmi")
        self.user_dialog = MDDialog(
            title="Yeni Profil Ekle",
            type="custom",
            content_cls=self.user_input,
            buttons=[
                MDFlatButton(text="İPTAL", on_release=lambda x: self.user_dialog.dismiss()),
                MDFlatButton(text="EKLE", on_release=lambda x: self.add_new_user(self.user_input.text))
            ],
        )
        self.user_dialog.open()

    def add_new_user(self, name):
        if name:
            try:
                self.cur.execute("INSERT INTO users VALUES (?)", (name,))
                self.conn.commit()
                self.refresh_profiles()
                self.user_dialog.dismiss()
            except: pass

    def load_menus(self):
        self.cur.execute("SELECT target_name FROM user_targets WHERE user = ?", (self.current_user,))
        targets = [row[0] for row in self.cur.fetchall()]
        
        main_ids = self.root_widget.get_screen('main').ids
        stats_ids = self.root_widget.get_screen('stats').ids

        self.main_menu = MDDropdownMenu(caller=main_ids.target_drop,
            items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_main(x)} for i in targets], width_mult=4)
        
        self.stats_menu = MDDropdownMenu(caller=stats_ids.stats_target_drop,
            items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_stats(x)} for i in targets], width_mult=4)

    def set_main(self, text):
        self.root_widget.get_screen('main').ids.target_drop.text = text
        self.main_menu.dismiss()

    def set_stats(self, text):
        self.current_stats_target = text
        self.root_widget.get_screen('stats').ids.stats_target_drop.text = text
        self.stats_menu.dismiss()
        self.draw_chart_and_list()

    def add_target_to_user(self):
        target = self.root_widget.get_screen('admin').ids.target_input.text
        if target and self.current_user:
            self.cur.execute("INSERT INTO user_targets VALUES (?, ?)", (self.current_user, target))
            self.conn.commit()
            self.root_widget.get_screen('admin').ids.target_input.text = ""
            self.refresh_admin_list()
            self.load_menus()

    def delete_target(self, target_name):
        self.cur.execute("DELETE FROM user_targets WHERE user = ? AND target_name = ?", (self.current_user, target_name))
        self.conn.commit()
        self.refresh_admin_list()
        self.load_menus()

    def refresh_admin_list(self):
        lst = self.root_widget.get_screen('admin').ids.user_target_list
        lst.clear_widgets()
        self.cur.execute("SELECT target_name FROM user_targets WHERE user = ?", (self.current_user,))
        for t in self.cur.fetchall():
            lst.add_widget(TwoLineListItem(text=t[0], secondary_text="Silmek için tıklayın", 
                                           on_release=lambda x, n=t[0]: self.delete_target(n)))

    def save_progress(self):
        target = self.root_widget.get_screen('main').ids.target_drop.text
        amount = self.root_widget.get_screen('main').ids.amount_input.text
        if amount.isdigit() and target != "Hedef Seçin":
            self.cur.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (self.current_user, self.selected_date, target, int(amount)))
            self.conn.commit()
            self.root_widget.get_screen('main').ids.amount_input.text = ""

    def draw_chart_and_list(self):
        if not self.current_stats_target or not self.current_user: return
        self.cur.execute("SELECT date, amount FROM logs WHERE date >= ? AND target = ? AND user = ? ORDER BY date DESC", 
                         (self.stats_start_date, self.current_stats_target, self.current_user))
        data = self.cur.fetchall()
        
        list_widget = self.root_widget.get_screen('stats').ids.data_list
        list_widget.clear_widgets()
        for d, a in data:
            list_widget.add_widget(TwoLineListItem(text=f"Miktar: {a}", secondary_text=f"Tarih: {d}"))

        plt.clf()
        plt.figure(figsize=(7, 4))
        if data:
            data_plot = data[::-1]
            plt.plot([d[0][-5:] for d in data_plot], [d[1] for d in data_plot], marker='o', color='indigo')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.title(f"{self.current_user}: {self.current_stats_target}")
        plt.tight_layout()
        buf = BytesIO(); plt.savefig(buf, format='png'); buf.seek(0)
        self.root_widget.get_screen('stats').ids.chart_img.texture = CoreImage(buf, ext='png').texture

    def show_date_picker(self, mode):
        self.date_mode = mode
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        formatted = value.strftime('%Y-%m-%d')
        if self.date_mode == "main":
            self.selected_date = formatted
            self.root_widget.get_screen('main').ids.date_label.text = "Tarih: " + formatted
        else:
            self.stats_start_date = formatted
            self.draw_chart_and_list()

    def update_range(self, days):
        self.stats_start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        self.draw_chart_and_list()

    def go_to_stats(self): self.root_widget.current = "stats"
    def go_to_admin(self): self.root_widget.current = "admin"

if __name__ == "__main__":
    TargetApp().run()