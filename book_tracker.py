import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("800x600")

        # Список для хранения книг
        self.books = []
        self.data_file = "books.json"

        # --- Фрейм ввода данных ---
        input_frame = ttk.LabelFrame(root, text="Добавить новую книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_title = ttk.Entry(input_frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entry_author = ttk.Entry(input_frame, width=20)
        self.entry_author.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_genre = ttk.Entry(input_frame, width=20)
        self.entry_genre.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Страниц:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_pages = ttk.Entry(input_frame, width=10)
        self.entry_pages.grid(row=1, column=3, padx=5, pady=2)

        # Кнопка добавления
        btn_add = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        btn_add.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

        # --- Фрейм фильтрации ---
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5)
        self.filter_genre = ttk.Entry(filter_frame, width=15)
        self.filter_genre.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Мин. страниц:").grid(row=0, column=2, padx=5)
        self.filter_pages = ttk.Entry(filter_frame, width=10)
        self.filter_pages.grid(row=0, column=3, padx=5)

        btn_filter = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=10)
        
        btn_reset = ttk.Button(filter_frame, text="Сброс", command=self.reset_filter)
        btn_reset.grid(row=0, column=5, padx=5)

        # --- Таблица (Treeview) ---
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Title", "Author", "Genre", "Pages")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Название")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Genre", text="Жанр")
        self.tree.heading("Pages", text="Страниц")

        self.tree.column("ID", width=50)
        self.tree.column("Title", width=200)
        self.tree.column("Author", width=150)
        self.tree.column("Genre", width=100)
        self.tree.column("Pages", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # --- Кнопки управления данными ---
        control_frame = ttk.Frame(root)
        control_frame.pack(fill="x", padx=10, pady=5)

        btn_save = ttk.Button(control_frame, text="Сохранить в JSON", command=self.save_to_json)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_load = ttk.Button(control_frame, text="Загрузить из JSON", command=self.load_from_json)
        btn_load.pack(side=tk.LEFT, padx=5)

        # Загрузка данных при старте, если файл существует
        if os.path.exists(self.data_file):
            self.load_from_json()

    def add_book(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.entry_genre.get().strip()
        pages_str = self.entry_pages.get().strip()

        # Валидация
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        book = {
            "id": len(self.books) + 1,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        
        self.books.append(book)
        self.refresh_table(self.books)
        self.clear_inputs()

    def clear_inputs(self):
        self.entry_title.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_pages.delete(0, tk.END)

    def refresh_table(self, data_list):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление данных
        for book in data_list:
            self.tree.insert("", tk.END, values=(
                book["id"],
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def apply_filter(self):
        genre_filter = self.filter_genre.get().strip().lower()
        pages_filter_str = self.filter_pages.get().strip()
        
        filtered_books = self.books

        # Фильтр по жанру
        if genre_filter:
            filtered_books = [b for b in filtered_books if genre_filter in b["genre"].lower()]

        # Фильтр по страницам
        if pages_filter_str:
            try:
                min_pages = int(pages_filter_str)
                filtered_books = [b for b in filtered_books if b["pages"] > min_pages]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Некорректное значение для фильтра страниц")
                return

        self.refresh_table(filtered_books)

    def reset_filter(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_pages.delete(0, tk.END)
        self.refresh_table(self.books)

    def save_to_json(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные сохранены в books.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_from_json(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.books = json.load(f)
            self.refresh_table(self.books)
            messagebox.showinfo("Успех", "Данные загружены")
        except FileNotFoundError:
            messagebox.showwarning("Внимание", "Файл books.json не найден")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Ошибка формата JSON файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    root.mainloop()
