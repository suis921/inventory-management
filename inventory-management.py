import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from pykakasi import kakasi

CSV_FILE = "InventoryData.csv"
FIELDNAMES = ["name", "location", "stock", "updated_at"]

kks = kakasi()

# CSV読み込み
def load_data():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            # Add updated_at if missing (for backward compatibility)
            if "updated_at" not in row or not row["updated_at"]:
                row["updated_at"] = ""
            data.append(row)
        return data

# CSV保存
def save_data(data):
    sorted_data = sort_data(data)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(sorted_data)

# ソート
def _sort_key(row):
    name = row["name"]
    if not name:
        return ("9", "")
    
    first_char = name[0]
    
    if first_char.isascii():
        group = "0"
        sort_key = name.lower()
    else:
        group = "1"
        result = kks.convert(name)
        reading = ''.join([item['hira'] for item in result])
        sort_key = reading
    
    return (group, sort_key)

def sort_data(data):
    return sorted(data, key=_sort_key)

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("学生団体在庫管理システム")
        self.root.resizable(True, True)
        self.data = load_data()
        self.dirty = False
        self.selected_index = None
        self._build_ui()
        self.refresh_table()
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Helvetica", 19, "bold"),
                        foreground="#2c3e50")
        style.configure("Treeview", rowheight=24, font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"),
                        background="#2980b9", foreground="white")
        style.map("Treeview", background=[("selected", "#3498db")])
        style.configure("Action.TButton", font=("Helvetica", 12), padding=4)
        style.configure("SaveQuit.TButton", font=("Helvetica", 13, "bold"),
                        padding=6)

        title_frame = ttk.Frame(self.root, padding=(12, 8))
        title_frame.pack(fill="x")
        ttk.Label(title_frame, text="学生団体在庫管理システム",
                  style="Title.TLabel").pack(side="left")

        self.btn_save_quit = ttk.Button(
            title_frame, text="💾  保存して終了",
            style="SaveQuit.TButton", command=self.save_and_quit)
        self.btn_save_quit.pack(side="right", padx=4)

        self.unsaved_label = ttk.Label(
            title_frame, text="", foreground="#e74c3c",
            font=("Helvetica", 12, "bold"))
        self.unsaved_label.pack(side="right", padx=8)

        sep = ttk.Separator(self.root, orient="horizontal")
        sep.pack(fill="x", padx=8)

        main_frame = ttk.Frame(self.root, padding=(10, 8, 10, 10))
        main_frame.pack(fill="both", expand=True)

        table_frame = ttk.LabelFrame(main_frame, text="物品一覧", padding=6)
        table_frame.pack(fill="both", expand=True, pady=(0, 6))

        cols = ("name", "location", "stock", "updated_at")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree.heading("name",       text="物品名")
        self.tree.heading("location",   text="保管場所")
        self.tree.heading("stock",      text="在庫数")
        self.tree.heading("updated_at", text="更新日時")
        self.tree.column("name",       width=200, anchor="w")
        self.tree.column("location",   width=150, anchor="w")
        self.tree.column("stock",      width=80,  anchor="center")
        self.tree.column("updated_at", width=150, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        sep2 = ttk.Separator(main_frame, orient="horizontal")
        sep2.pack(fill="x", pady=4)

        ops_frame = ttk.Frame(main_frame)
        ops_frame.pack(fill="x")
        ops_frame.columnconfigure(0, weight=1)
        ops_frame.columnconfigure(1, weight=1)
        ops_frame.columnconfigure(2, weight=1)

        self._build_stock_panel(ops_frame)
        self._build_location_panel(ops_frame)
        self._build_add_delete_panel(ops_frame)

        credit_frame = ttk.Frame(main_frame, padding=(0, 8, 0, 0))
        credit_frame.pack(fill="x")
        ttk.Label(credit_frame, text="Copyright © 2026 在庫管理システム v1.1",
                  font=("Helvetica", 9), foreground="#7f8c8d").pack(side="right")

    def _build_stock_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="在庫数の変更", padding=6)
        frame.grid(row=0, column=0, padx=4, pady=2, sticky="nsew")

        ttk.Label(frame, text="選択中の物品:").grid(
            row=0, column=0, columnspan=2, sticky="w")
        self.selected_name_var = tk.StringVar(value="(未選択)")
        ttk.Label(frame, textvariable=self.selected_name_var,
                  foreground="#2980b9",
                  font=("Helvetica", 12, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(frame, text="数量:").grid(row=2, column=0, sticky="w")
        self.stock_change_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.stock_change_var,
                  width=15).grid(row=2, column=1, sticky="w", padx=(4, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(8, 0), sticky="w")
        ttk.Button(btn_frame, text="追加 ＋", width=9,
                   command=self.add_stock).pack(side="left", padx=(0, 4))
        ttk.Button(btn_frame, text="消費 －", width=9,
                   command=self.consume_stock).pack(side="left", padx=(0, 4))
        ttk.Button(btn_frame, text="変更 ♺", width=9,
                   command=self.refresh_stock).pack(side="left")

    def _build_location_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="保管場所の変更", padding=6)
        frame.grid(row=0, column=1, padx=4, pady=2, sticky="nsew")

        ttk.Label(frame, text="選択中の物品:").grid(
            row=0, column=0, columnspan=2, sticky="w")
        self.selected_name_var2 = tk.StringVar(value="(未選択)")
        ttk.Label(frame, textvariable=self.selected_name_var2,
                  foreground="#2980b9",
                  font=("Helvetica", 12, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(frame, text="新しい場所:").grid(row=2, column=0, sticky="w")
        self.new_location_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.new_location_var,
                  width=20).grid(row=2, column=1, sticky="w", padx=(4, 0))

        ttk.Button(frame, text="保管場所を変更", width=14,
                   command=self.change_location).grid(
            row=3, column=0, columnspan=2, pady=(8, 0), sticky="w")

    def _build_add_delete_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="物品の追加・削除", padding=6)
        frame.grid(row=0, column=2, padx=4, pady=2, sticky="nsew")

        ttk.Label(frame, text="【新規追加】", font=("Helvetica", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        
        labels = [("物品名:", "new_name_var"),
                  ("保管場所:", "new_loc_var"),
                  ("在庫数:", "new_stock_var")]
        for i, (lbl, attr) in enumerate(labels):
            ttk.Label(frame, text=lbl).grid(
                row=i+1, column=0, sticky="w", pady=2)
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(frame, textvariable=var, width=24).grid(
                row=i+1, column=1, sticky="w", padx=(4, 0))

        ttk.Button(frame, text="物品を追加 ＋", width=20,
                   command=self.add_part).grid(
            row=4, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        ttk.Separator(frame, orient="horizontal").grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(frame, text="【削除】", font=("Helvetica", 11, "bold")).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(0, 4))
        
        delete_frame = ttk.Frame(frame)
        delete_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
        
        ttk.Label(delete_frame, text="対象:").pack(side="left")
        self.delete_name_label = ttk.Label(
            delete_frame, text="(未選択)", foreground="#e74c3c",
            font=("Helvetica", 11, "bold"))
        self.delete_name_label.pack(side="left", padx=4)
        
        ttk.Button(frame, text="選択した物品を削除", width=20,
                   command=self.delete_part).grid(
            row=8, column=0, columnspan=2, pady=(4, 0), sticky="ew")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, row in enumerate(self.data):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", iid=str(i), values=(row["name"], row["location"], row["stock"], row.get("updated_at", "")), tags=(tag,))

        self.tree.tag_configure("even", background="#f0f4f8")
        self.tree.tag_configure("odd",  background="#ffffff")

        self.selected_index = None
        self._update_selection_labels("(未選択)")

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_index = int(sel[0])
        name = self.data[self.selected_index]["name"]
        self._update_selection_labels(name)

    def _update_selection_labels(self, name):
        self.selected_name_var.set(name)
        self.selected_name_var2.set(name)
        self.delete_name_label.config(text=name)

    def _get_current_timestamp(self):
        """Return current timestamp in YYYY-MM-DD HH:MM:SS format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _mark_dirty(self):
        self.dirty = True
        self.unsaved_label.config(text="● 未保存の変更があります")

    def _mark_clean(self):
        self.dirty = False
        self.unsaved_label.config(text="")

    def _get_change_amount(self):
        val = self.stock_change_var.get().strip()
        if not val:
            messagebox.showwarning("入力エラー", "数量を入力してください。")
            return None
        try:
            n = int(val)
        except ValueError:
            messagebox.showwarning("入力エラー", "数量は整数で入力してください。")
            return None
        if n <= 0:
            messagebox.showwarning("入力エラー", "1以上の数値を入力してください。")
            return None
        return n

    def add_stock(self):
        if self.selected_index is None:
            messagebox.showwarning("選択エラー", "物品を選択してください。")
            return
        n = self._get_change_amount()
        if n is None:
            return
        self.data[self.selected_index]["stock"] = str(
            int(self.data[self.selected_index]["stock"]) + n)
        self.data[self.selected_index]["updated_at"] = self._get_current_timestamp()
        self._mark_dirty()
        self.stock_change_var.set("")
        self._reselect_after_refresh(self.selected_index)

    def consume_stock(self):
        if self.selected_index is None:
            messagebox.showwarning("選択エラー", "物品を選択してください。")
            return
        n = self._get_change_amount()
        if n is None:
            return
        current = int(self.data[self.selected_index]["stock"])
        if current - n < 0:
            messagebox.showerror(
                "在庫不足",
                f"在庫数が不足しています。\n"
                f"現在の在庫数: {current}  消費予定: {n}\n"
                f"在庫数がマイナスになるため消費できません。")
            return
        self.data[self.selected_index]["stock"] = str(current - n)
        self.data[self.selected_index]["updated_at"] = self._get_current_timestamp()
        self._mark_dirty()
        self.stock_change_var.set("")
        self._reselect_after_refresh(self.selected_index)

    def refresh_stock(self):
        if self.selected_index is None:
            messagebox.showwarning("選択エラー", "物品を選択してください。")
            return
        n = self._get_change_amount()
        if n is None:
            return
        self.data[self.selected_index]["stock"] = str(n)
        self.data[self.selected_index]["updated_at"] = self._get_current_timestamp()
        self._mark_dirty()
        self.stock_change_var.set("")
        self._reselect_after_refresh(self.selected_index)

    def change_location(self):
        if self.selected_index is None:
            messagebox.showwarning("選択エラー", "物品を選択してください。")
            return
        new_loc = self.new_location_var.get().strip()
        if not new_loc:
            messagebox.showwarning("入力エラー", "新しい保管場所を入力してください。")
            return
        self.data[self.selected_index]["location"] = new_loc
        self.data[self.selected_index]["updated_at"] = self._get_current_timestamp()
        self._mark_dirty()
        self.new_location_var.set("")
        self._reselect_after_refresh(self.selected_index)

    def add_part(self):
        name  = self.new_name_var.get().strip()
        loc   = self.new_loc_var.get().strip()
        stock = self.new_stock_var.get().strip()

        if not name:
            messagebox.showwarning("入力エラー", "物品名を入力してください。")
            return
        if not loc:
            messagebox.showwarning("入力エラー", "保管場所を入力してください。")
            return
        if not stock:
            messagebox.showwarning("入力エラー", "在庫数を入力してください。")
            return
        try:
            stock_int = int(stock)
            if stock_int < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("入力エラー", "在庫数は0以上の整数で入力してください。")
            return

        for row in self.data:
            if row["name"] == name:
                messagebox.showwarning("重複エラー", f"「{name}」はすでに登録されています。")
                return

        self.data.append({"name": name, "location": loc, "stock": str(stock_int), "updated_at": self._get_current_timestamp()})
        self._mark_dirty()
        self.new_name_var.set("")
        self.new_loc_var.set("")
        self.new_stock_var.set("")
        self.refresh_table()
        messagebox.showinfo("追加完了",
                            f"「{name}」を追加しました。\n"
                            "「保存して終了」を押すまでCSVには書き込まれません。")

    def delete_part(self):
        if self.selected_index is None:
            messagebox.showwarning("選択エラー", "削除する物品を選択してください。")
            return
        name = self.data[self.selected_index]["name"]
        confirm = messagebox.askyesno(
            "削除確認",
            f"「{name}」を削除します。\nこの操作は元に戻せません。よろしいですか？")
        if not confirm:
            return
        del self.data[self.selected_index]
        self._mark_dirty()
        self.selected_index = None
        self.refresh_table()
        messagebox.showinfo("削除完了",
                            f"「{name}」を削除しました。\n"
                            "「保存して終了」を押すまでCSVには書き込まれません。")

    def save_and_quit(self):
        confirm = messagebox.askyesno(
            "保存して終了",
            "現在の内容をCSVに保存してアプリを終了します。\n"
            "保存すると物品名のアルファベット順（日本語はあいうえお順）に\n"
            "並べ替えられます。よろしいですか？")
        if not confirm:
            return
        try:
            save_data(self.data)
        except Exception as e:
            messagebox.showerror("保存エラー", f"CSVの保存中にエラーが発生しました。\n{e}")
            return
        self._mark_clean()
        self.root.destroy()

    def _on_window_close(self):
        """Called when the user clicks the ✕ button."""
        if self.dirty:
            answer = messagebox.askyesnocancel(
                "終了の確認",
                "未保存の変更があります。\n\n"
                "「はい」　　　→ 保存して終了\n"
                "「いいえ」　　→ 保存せずに終了\n"
                "「キャンセル」→ 終了をやめる")
            if answer is None:
                return
            elif answer is True:
                try:
                    save_data(self.data)
                except Exception as e:
                    messagebox.showerror("保存エラー", f"CSVの保存中にエラーが発生しました。\n{e}")
                    return
        self.root.destroy()

    def _reselect_after_refresh(self, idx):
        self.refresh_table()
        if 0 <= idx < len(self.data):
            iid = str(idx)
            if self.tree.exists(iid):
                self.tree.selection_set(iid)
                self.tree.focus(iid)
                self.tree.see(iid)
                self.selected_index = idx
                self._update_selection_labels(self.data[idx]["name"])

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(980, 480)
    app = InventoryApp(root)
    root.mainloop()