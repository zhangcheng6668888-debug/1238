import tkinter as tk
from tkinter import messagebox, ttk
import json, os, threading, time, requests

DATA_FILE = "data.json"

class MonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高级地址监控系统 Pro")
        self.root.geometry("1000x650")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.data = []
        self.running = False

        self.load_data()
        self.build_ui()
        self.refresh()

    def build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=10)

        self.addr = ttk.Entry(top, width=40)
        self.addr.pack(side="left", padx=5)
        self.note = ttk.Entry(top, width=30)
        self.note.pack(side="left", padx=5)

        ttk.Button(top, text="添加", command=self.add).pack(side="left", padx=5)
        ttk.Button(top, text="删除", command=self.delete).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.root, columns=("addr","note","status"), show="headings")
        self.tree.heading("addr", text="地址")
        self.tree.heading("note", text="备注")
        self.tree.heading("status", text="状态")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        bottom = ttk.Frame(self.root)
        bottom.pack(pady=10)

        ttk.Button(bottom, text="开始监控", command=self.start).pack(side="left", padx=10)
        ttk.Button(bottom, text="停止监控", command=self.stop).pack(side="left", padx=10)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            self.data = json.load(open(DATA_FILE,"r",encoding="utf-8"))

    def save(self):
        json.dump(self.data, open(DATA_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for d in self.data:
            self.tree.insert("", "end", values=(d["addr"], d["note"], d.get("status","未检测")))

    def add(self):
        a = self.addr.get().strip()
        n = self.note.get().strip()
        if not a: return
        if any(i["addr"]==a for i in self.data):
            messagebox.showwarning("重复","地址已存在")
            return
        self.data.append({"addr":a,"note":n,"status":"未检测"})
        self.save()
        self.refresh()

    def delete(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        del self.data[idx]
        self.save()
        self.refresh()

    def start(self):
        if self.running: return
        self.running=True
        threading.Thread(target=self.loop, daemon=True).start()

    def stop(self):
        self.running=False

    def notify(self, msg):
        print("通知:", msg)

    def loop(self):
        while self.running:
            for d in self.data:
                try:
                    requests.get(d["addr"], timeout=3)
                    d["status"]="正常"
                except:
                    d["status"]="异常"
                    self.notify(f"{d['addr']} 异常!")
                self.refresh()
            self.save()
            time.sleep(10)

if __name__=="__main__":
    root=tk.Tk()
    app=MonitorApp(root)
    root.mainloop()
