import tkinter as tk
from tkinter import ttk
from anilist_api import get_current_airing_anime
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

        self.poster_label = tk.Label(root)
        self.poster_label.pack(side=tk.RIGHT, padx=10, pady=10)

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

    def on_row_select(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.filtered_anime_data):
                anime = self.filtered_anime_data[index]
                self.show_image(anime['image_url'])

    def show_image(self, url):
        poster = fetch_and_resize_image(url)
        if poster:
            self.poster_label.config(image=poster)
            self.poster_label.image = poster
