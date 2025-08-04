import tkinter as tk
from tkinter import ttk
from anilist_api import get_current_airing_anime
from torrent_search import search_nyaa
import webbrowser
from utils import fetch_and_resize_image

REFRESH_INTERVAL = 5 * 60 * 1000

class AnimeTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Currently Airing Anime - AniList")
        self.root.geometry("1200x650")

        self.anime_data = []
        self.filtered_anime_data = []

        self.weekday_var = tk.StringVar(value="All")
        self.weekdays = ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.dropdown = ttk.OptionMenu(root, self.weekday_var, "All", *self.weekdays, command=lambda _: self.refresh_table())
        self.dropdown.pack(pady=10)

        columns = ("Title", "Format", "Episodes Aired", "Time Until Next Episode", "Airing Time", "Weekday")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", width=200 if col == "Title" else 150)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.poster_label = tk.Label(right_frame)
        self.poster_label.pack(pady=(0, 10))

        self.download_button = ttk.Button(right_frame, text="Download", command=self.on_download_button_click)
        self.download_button.pack()
        self.download_button.config(state="disabled")

        self.selected_anime = None

        self.refresh_table()

    def refresh_table(self):
        self.anime_data = get_current_airing_anime()
        self.filtered_anime_data = []

        for row in self.tree.get_children():
            self.tree.delete(row)

        for anime in self.anime_data:
            if self.weekday_var.get() == "All" or anime['weekday'] == self.weekday_var.get():
                self.filtered_anime_data.append(anime)
                self.tree.insert('', 'end', values=(
                    anime["title"], anime["format"], anime["episode"],
                    anime["time_remaining"], anime["airing_time"], anime["weekday"]
                ))

        self.root.after(REFRESH_INTERVAL, self.refresh_table)
        self.root.after(100, self.preload_posters)

    def preload_posters(self):
        from threading import Thread

        def load_images():
            for anime in self.filtered_anime_data:
                fetch_and_resize_image(anime['image_url'])

        Thread(target=load_images, daemon=True).start()

    def on_row_select(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.filtered_anime_data):
                anime = self.filtered_anime_data[index]
                self.selected_anime = anime
                self.show_image(anime['image_url'])
                self.download_button.config(state="normal")

    def show_image(self, url):
        poster = fetch_and_resize_image(url)
        if poster:
            self.poster_label.config(image=poster)
            self.poster_label.image = poster

    def on_download_button_click(self):
        if self.selected_anime:
            self.open_anime_popup(self.selected_anime)

    def open_anime_popup(self, anime):
        popup = tk.Toplevel(self.root)
        popup.title(anime['title'])
        popup.geometry("950x500")

        label = tk.Label(popup, text=f"Torrent Results for: {anime['title']}", font=("Arial", 14))
        label.pack(pady=10)

        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("title", "seeders", "leechers", "uploaded", "link")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        for col in columns[:-1]:  # exclude 'link' from resize
            display_name = col.capitalize() if col != "uploaded" else "Date"
            tree.heading(col, text=display_name)
            tree.column(col, anchor="w", width=140)
        tree.heading("link", text="Magnet")
        tree.column("link", width=60, anchor="center")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        results = search_nyaa(anime['title'], max_results=50)
        self.magnet_lookup = {}

        for idx, result in enumerate(results):
            title = result.get('title', '?')
            seeders = result.get('seeders', '?')
            leechers = result.get('leechers', '?')
            uploaded = result.get('uploaded', '?')
            magnet = result.get('magnet')
            tree.insert('', 'end', iid=str(idx), values=(title, seeders, leechers, uploaded, "🔗"))
            self.magnet_lookup[str(idx)] = magnet

        def on_click(event):
            item = tree.identify_row(event.y)
            col = tree.identify_column(event.x)
            if item and col == "#5":  # 'link' column
                magnet = self.magnet_lookup.get(item)
                if magnet:
                    webbrowser.open(magnet)

        tree.bind("<Button-1>", on_click)