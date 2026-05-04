import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# ------------------ API ------------------
def get_exchange_rate(from_currency, to_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["rates"].get(to_currency)
    except Exception as e:
        messagebox.showerror("Ошибка API", f"Не удалось получить курс:\n{e}")
        return None

# ------------------ История ------------------
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ------------------ GUI ------------------
class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("750x500")

        self.history = load_history()

        # Валюты (популярные)
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "CHF", "CAD", "AUD"]

        # --- Интерфейс ---
        # Из валюты
        tk.Label(root, text="Из валюты:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.from_currency = ttk.Combobox(root, values=self.currencies, state="readonly")
        self.from_currency.grid(row=0, column=1, padx=10, pady=10)
        self.from_currency.set("USD")

        # В валюту
        tk.Label(root, text="В валюту:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.to_currency = ttk.Combobox(root, values=self.currencies, state="readonly")
        self.to_currency.grid(row=0, column=3, padx=10, pady=10)
        self.to_currency.set("EUR")

        # Сумма
        tk.Label(root, text="Сумма:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10)

        # Кнопка
        self.convert_btn = tk.Button(root, text="Конвертировать", command=self.convert, bg="lightblue")
        self.convert_btn.grid(row=1, column=2, padx=10, pady=10)

        # Результат
        self.result_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=2, column=0, columnspan=4, pady=10)

        # Таблица истории
        tk.Label(root, text="История конвертаций:", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=4, pady=5, sticky="w")

        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.grid(row=4, column=0, columnspan=4, padx=10, pady=5)

        # Кнопки управления историей
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10)

        tk.Button(btn_frame, text="Очистить историю", command=self.clear_history, bg="lightcoral").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Обновить курс", command=self.refresh_rate, bg="lightgreen").pack(side="left", padx=10)

        self.update_history_table()

    def convert(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом (больше 0)")
            return

        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()

        rate = get_exchange_rate(from_cur, to_cur)
        if rate is None:
            return

        result = amount * rate
        self.result_label.config(text=f"{amount:.2f} {from_cur} = {result:.2f} {to_cur} (курс: {rate:.4f})")

        # Сохраняем в историю
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from": from_cur,
            "to": to_cur,
            "result": round(result, 2),
            "rate": rate
        }
        self.history.append(record)
        save_history(self.history)
        self.update_history_table()

    def update_history_table(self):
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Заполняем
        for record in self.history[-50:]:  # последние 50 записей
            self.tree.insert("", "end", values=(
                record["date"],
                f"{record['amount']:.2f}",
                record["from"],
                record["to"],
                f"{record['result']:.2f}"
            ))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            save_history(self.history)
            self.update_history_table()
            self.result_label.config(text="История очищена")

    def refresh_rate(self):
        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()
        rate = get_exchange_rate(from_cur, to_cur)
        if rate:
            messagebox.showinfo("Актуальный курс", f"1 {from_cur} = {rate:.4f} {to_cur}")

# ------------------ Запуск ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
