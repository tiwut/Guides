import tkinter as tk
from tkinter import ttk, messagebox
import os
import re

BASE_DIR = os.getcwd()
GUIDES_FILE = "guides.txt"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="../style.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap" rel="stylesheet">
    <script src="https://tiwut.de/Script/enforce_https.js" defer></script>
</head>
<body class="guide-page">

    <nav id="sidebar">
        <h2>{title}</h2>
        <ul>
            {sidebar_links}
            <li><a href="../index.html">← Back to Home</a></li>
        </ul>
    </nav>

    <div id="main-content">
        <header>
            <h1>{title}</h1>
            <p>{description}</p>
        </header>

        {content_sections}
        
        <footer>
            <a href="https://tiwut.de/cookie-banner-information.html">© 2026 Tiwut.de - Legal Notice</a>
        </footer>
    </div>

    <!-- Inject Global Script for Animations -->
    <script src="../script.js"></script>
</body>
</html>
"""

class GuideBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Guide Builder")
        self.geometry("1100x700")
        self.configure(bg="#1e1e1e")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        self.style.configure("TButton", background="#333333", foreground="#ffffff", borderwidth=0, font=("Segoe UI", 9))
        self.style.map("TButton", background=[("active", "#ff6600")])
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#ff6600")
        self.blocks = []
        self.create_layout()

    def create_layout(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill="x", side="top")
        ttk.Label(top_frame, text="Guide Title:").pack(side="left", padx=5)
        self.entry_title = tk.Entry(top_frame, width=30, bg="#333", fg="#fff", insertbackground="white")
        self.entry_title.pack(side="left", padx=5)
        ttk.Label(top_frame, text="Folder Name:").pack(side="left", padx=5)
        self.entry_folder = tk.Entry(top_frame, width=20, bg="#333", fg="#fff", insertbackground="white")
        self.entry_folder.pack(side="left", padx=5)
        ttk.Label(top_frame, text="Description:").pack(side="left", padx=5)
        self.entry_desc = tk.Entry(top_frame, width=40, bg="#333", fg="#fff", insertbackground="white")
        self.entry_desc.pack(side="left", padx=5)
        ttk.Button(top_frame, text="GENERATE GUIDE", command=self.generate_guide).pack(side="right", padx=10, fill="y")
        main_paned = tk.PanedWindow(self, orient="horizontal", bg="#2d2d2d", sashwidth=4)
        main_paned.pack(fill="both", expand=True, pady=5)
        toolbox_frame = ttk.Frame(main_paned, width=200)
        main_paned.add(toolbox_frame)
        ttk.Label(toolbox_frame, text="Toolbox", style="Header.TLabel").pack(pady=10)

        tools = [
            ("Add Section Header", self.add_section_header),
            ("Add Paragraph", self.add_paragraph),
            ("Add Code Block", self.add_code_block),
            ("Add Alert/Warning", self.add_alert),
            ("Add List", self.add_list)
        ]

        for text, cmd in tools:
            btn = tk.Button(toolbox_frame, text=text, command=cmd, bg="#444", fg="#fff", relief="flat", pady=8, cursor="hand2")
            btn.pack(fill="x", padx=10, pady=5)
        self.canvas_frame = tk.Frame(main_paned, bg="#121212")
        main_paned.add(self.canvas_frame)

        ttk.Label(self.canvas_frame, text="Guide Structure (Drag or Click to Edit)", style="Header.TLabel", background="#121212").pack(pady=10)
        canvas_scroll = tk.Canvas(self.canvas_frame, bg="#121212", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=canvas_scroll.yview)
        self.block_list_frame = tk.Frame(canvas_scroll, bg="#121212")
        self.block_list_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_window = canvas_scroll.create_window((0, 0), window=self.block_list_frame, anchor="nw")
        self.canvas_frame.bind("<Configure>", lambda e: canvas_scroll.itemconfig(canvas_window, width=e.width))
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.prop_frame = ttk.Frame(main_paned, width=300, padding=10)
        main_paned.add(self.prop_frame)
        ttk.Label(self.prop_frame, text="Properties", style="Header.TLabel").pack(pady=10)
        self.prop_content = tk.Frame(self.prop_frame, bg="#1e1e1e")
        self.prop_content.pack(fill="both", expand=True)
        ttk.Label(self.prop_content, text="Select a block to edit").pack()

    def refresh_block_list(self):
        for widget in self.block_list_frame.winfo_children():
            widget.destroy()

        for idx, block in enumerate(self.blocks):
            card = tk.Frame(self.block_list_frame, bg="#333", pady=5, padx=5)
            card.pack(fill="x", pady=2, padx=10)
            card.bind("<Button-1>", lambda e, i=idx: self.select_block(i))
            type_lbl = tk.Label(card, text=f"{block['type'].upper()}: {self.get_preview_text(block)}", bg="#333", fg="#ddd", anchor="w")
            type_lbl.pack(side="left", fill="x", expand=True)
            type_lbl.bind("<Button-1>", lambda e, i=idx: self.select_block(i))
            del_btn = tk.Button(card, text="X", bg="#cc0000", fg="#fff", width=3, command=lambda i=idx: self.delete_block(i))
            del_btn.pack(side="right")
            
            if idx > 0:
                up_btn = tk.Button(card, text="↑", bg="#555", fg="#fff", width=2, command=lambda i=idx: self.move_block(i, -1))
                up_btn.pack(side="right", padx=2)
            if idx < len(self.blocks) - 1:
                down_btn = tk.Button(card, text="↓", bg="#555", fg="#fff", width=2, command=lambda i=idx: self.move_block(i, 1))
                down_btn.pack(side="right", padx=2)

    def get_preview_text(self, block):
        if block['type'] == 'header': return block['data'].get("text", "")
        if block['type'] == 'paragraph': return (block['data'].get("text", "")[:30] + "...")
        if block['type'] == 'code': return "Code Block"
        return ""

    def add_section_header(self):
        self.blocks.append({"type": "header", "data": {"text": "New Section", "id": "new-section"}})
        self.refresh_block_list()
        self.select_block(len(self.blocks)-1)

    def add_paragraph(self):
        self.blocks.append({"type": "paragraph", "data": {"text": "Enter content here..."}})
        self.refresh_block_list()
        self.select_block(len(self.blocks)-1)
    
    def add_code_block(self):
        self.blocks.append({"type": "code", "data": {"language": "bash", "code": "# Command here"}})
        self.refresh_block_list()
        self.select_block(len(self.blocks)-1)
    
    def add_alert(self):
        self.blocks.append({"type": "alert", "data": {"level": "important", "text": "Crucial info"}})
        self.refresh_block_list()
        self.select_block(len(self.blocks)-1)

    def add_list(self):
        self.blocks.append({"type": "list", "data": {"items": "Item 1\nItem 2\nItem 3"}})
        self.refresh_block_list()
        self.select_block(len(self.blocks)-1)

    def move_block(self, index, direction):
        new_index = index + direction
        self.blocks[index], self.blocks[new_index] = self.blocks[new_index], self.blocks[index]
        self.refresh_block_list()
    
    def delete_block(self, index):
        self.blocks.pop(index)
        self.refresh_block_list()
        for widget in self.prop_content.winfo_children(): widget.destroy()

    def select_block(self, index):
        for widget in self.prop_content.winfo_children(): widget.destroy()
        
        block = self.blocks[index]
        data = block['data']

        def update_data(key, val):
            self.blocks[index]['data'][key] = val
            self.refresh_block_list_preview_only(index)

        if block['type'] == 'header':
            ttk.Label(self.prop_content, text="Header Text:").pack(anchor="w")
            ent = tk.Entry(self.prop_content, bg="#444", fg="#fff")
            ent.insert(0, data['text'])
            ent.pack(fill="x", pady=5)
            ent.bind("<KeyRelease>", lambda e: update_data("text", ent.get()))
            ttk.Label(self.prop_content, text="ID (anchor):").pack(anchor="w")
            id_ent = tk.Entry(self.prop_content, bg="#444", fg="#fff")
            id_ent.insert(0, data['id'])
            id_ent.pack(fill="x", pady=5)
            id_ent.bind("<KeyRelease>", lambda e: update_data("id", id_ent.get()))

        elif block['type'] == 'paragraph':
            ttk.Label(self.prop_content, text="Content:").pack(anchor="w")
            txt = tk.Text(self.prop_content, height=10, bg="#444", fg="#fff")
            txt.insert("1.0", data['text'])
            txt.pack(fill="x", pady=5)
            txt.bind("<KeyRelease>", lambda e: update_data("text", txt.get("1.0", "end-1c")))
        
        elif block['type'] == 'code':
            ttk.Label(self.prop_content, text="Language:").pack(anchor="w")
            ent = tk.Entry(self.prop_content, bg="#444", fg="#fff")
            ent.insert(0, data['language'])
            ent.pack(fill="x", pady=5)
            ent.bind("<KeyRelease>", lambda e: update_data("language", ent.get()))
            ttk.Label(self.prop_content, text="Code:").pack(anchor="w")
            txt = tk.Text(self.prop_content, height=10, font=("Consolas", 10), bg="#222", fg="#0f0")
            txt.insert("1.0", data['code'])
            txt.pack(fill="x", pady=5)
            txt.bind("<KeyRelease>", lambda e: update_data("code", txt.get("1.0", "end-1c")))

        elif block['type'] == 'alert':
            ttk.Label(self.prop_content, text="Type (important/warning):").pack(anchor="w")
            ent = tk.Entry(self.prop_content, bg="#444", fg="#fff")
            ent.insert(0, data['level'])
            ent.pack(fill="x", pady=5)
            ent.bind("<KeyRelease>", lambda e: update_data("level", ent.get()))
            ttk.Label(self.prop_content, text="Content:").pack(anchor="w")
            txt = tk.Text(self.prop_content, height=5, bg="#444", fg="#fff")
            txt.insert("1.0", data['text'])
            txt.pack(fill="x", pady=5)
            txt.bind("<KeyRelease>", lambda e: update_data("text", txt.get("1.0", "end-1c")))

        elif block['type'] == 'list':
            ttk.Label(self.prop_content, text="Items (one per line):").pack(anchor="w")
            txt = tk.Text(self.prop_content, height=10, bg="#444", fg="#fff")
            txt.insert("1.0", data['items'])
            txt.pack(fill="x", pady=5)
            txt.bind("<KeyRelease>", lambda e: update_data("items", txt.get("1.0", "end-1c")))

    def refresh_block_list_preview_only(self, index):
        pass 

    def generate_guide(self):
        title = self.entry_title.get()
        folder = self.entry_folder.get()
        desc = self.entry_desc.get()

        if not title or not folder:
            messagebox.showerror("Error", "Title and Folder Name are required!")
            return

        html_content = ""
        sidebar_links = ""
        sidebar_links += '<li><a href="#intro" class="active">Introduction</a></li>\n'
        current_section_open = False
        
        for block in self.blocks:
            data = block['data']
            
            if block['type'] == 'header':
                if current_section_open:
                    html_content += "</section>\n"
                
                sid = data['id']
                stext = data['text']
                html_content += f'<section id="{sid}" class="guide-section">\n'
                html_content += f'    <h2>{stext}</h2>\n'
                sidebar_links += f'<li><a href="#{sid}">{stext}</a></li>\n'
                current_section_open = True
            
            elif block['type'] == 'paragraph':
                if not current_section_open:
                    html_content += '<section id="intro" class="guide-section">\n'
                    current_section_open = True
                html_content += f'    <p>{data["text"]}</p>\n'
            
            elif block['type'] == 'code':
                if not current_section_open:
                    html_content += '<section id="example" class="guide-section">\n'
                    current_section_open = True
                html_content += f'    <pre><code class="language-{data["language"]}">{data["code"]}</code></pre>\n'
            
            elif block['type'] == 'alert':
                if not current_section_open:
                    html_content += '<section id="info" class="guide-section">\n'
                    current_section_open = True
                html_content += f'    <div class="{data["level"]}"><p>{data["text"]}</p></div>\n'

            elif block['type'] == 'list':
                if not current_section_open:
                    html_content += '<section id="list" class="guide-section">\n'
                    current_section_open = True
                html_content += '    <ul>\n'
                for item in data['items'].split('\n'):
                    if item.strip():
                        html_content += f'        <li>{item.strip()}</li>\n'
                html_content += '    </ul>\n'
        
        if current_section_open:
            html_content += "</section>\n"

        full_html = HTML_TEMPLATE.format(
            title=title,
            description=desc,
            sidebar_links=sidebar_links,
            content_sections=html_content
        )

        target_dir = os.path.join(BASE_DIR, folder)
        try:
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(full_html)

            with open(GUIDES_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{folder};{title};{title};{title}")

            messagebox.showinfo("Success", f"Guide '{title}' generated successfully in /{folder}!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save guide: {str(e)}")

if __name__ == "__main__":
    app = GuideBuilderApp()
    app.mainloop()
