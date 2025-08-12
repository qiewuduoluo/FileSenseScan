#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileSenseScan - 统一版本主GUI应用
整合了所有功能，解决拖拽、DPI、关闭异常等问题
"""

import os
import sys
import json
import threading
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
import customtkinter as ctk
from PIL import Image, ImageTk

# ===== Windows 深色标题栏 =====
def set_dark_titlebar(hwnd):
    """在 Windows 10+ 启用深色标题栏"""
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
        value = wintypes.BOOL(1)
        set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                             ctypes.byref(value), ctypes.sizeof(value))
    except Exception:
        pass  # 如果API不可用，静默失败

# ===== 拖拽支持检测和导入 =====
DND_OK = False
DND_FILES = None
TkinterDnD = None

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_OK = True
    print("✅ 拖拽支持已启用")
except ImportError:
    print("⚠️  拖拽支持未安装，将使用标准模式")
    DND_OK = False

# ===== 自定义适配类 =====
if DND_OK:
    class CTkDnD(TkinterDnD.Tk):
        def __init__(self, *args, **kwargs):
            # 只初始化一个 Tk 根，避免多窗口
            super().__init__()
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            # 创建 CTk 主容器作为根窗口的内容
            self.ctk_container = ctk.CTkFrame(self)
            self.ctk_container.pack(fill="both", expand=True)
else:
    class CTkDnD(ctk.CTk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")

# 保证导入项目文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

# 导入批处理逻辑
from app.batch.main_batch import process_pdf
from config.config import USE_MODEL

# ---------- 读取品牌配置 ----------
def load_brand():
    default = {
        "app_name": "FileSenseScan",
        "logo_path": os.path.join(BASE_DIR, "assets", "logo.png"),
        "window_icon": os.path.join(BASE_DIR, "assets", "app.ico"),
        "primary": "#2C93FF",
        "bg": "#161A20",
        "panel": "#1E232B",
        "text": "#E8E9EB",
        "muted": "#9AA4B2"
    }
    path1 = os.path.join(BASE_DIR, "assets", "brand.json")
    path2 = os.path.join(BASE_DIR, "assets", "brand.json")
    use = path1 if os.path.exists(path1) else path2
    try:
        if use and os.path.exists(use):
            with open(use, "r", encoding="utf-8") as f:
                default.update(json.load(f))
    except Exception:
        pass
    return default

BRAND = load_brand()

# ---------- 主题设定 ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRIMARY = BRAND["primary"]
BG = BRAND["bg"]
PANEL = BRAND["panel"]
TEXT = BRAND["text"]
MUTED = BRAND["muted"]

# 设置文件路径
SETTINGS = os.path.join(BASE_DIR, "config", "settings.json")

def _set_dpi_awareness():
    """设置DPI感知"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # per-monitor v1
    except Exception:
        pass

def path_here(*parts):
    """获取相对于当前文件的路径"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)

def load_settings():
    """加载应用设置"""
    default_settings = {
        "win_w": 1200,
        "win_h": 740,
        "win_max": False
    }
    
    try:
        if os.path.exists(SETTINGS):
            with open(SETTINGS, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_settings.update(loaded)
    except Exception as e:
        print(f"加载设置失败: {e}")
    
    return default_settings

def save_settings(settings):
    """保存应用设置"""
    try:
        os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
        with open(SETTINGS, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"保存设置失败: {e}")

class FileSenseScanGUI(CTkDnD):
    def __init__(self):
        super().__init__()
        
        # 设置DPI感知
        _set_dpi_awareness()
        
        # 加载设置
        self.settings = load_settings()
        
        # 设置窗口属性
        self.title(BRAND["app_name"])
        self.geometry(f"{self.settings['win_w']}x{self.settings['win_h']}")
        self.minsize(800, 600)
        
        # 设置图标
        try:
            if os.path.exists(BRAND["window_icon"]):
                self.iconbitmap(BRAND["window_icon"])
        except Exception:
            pass
        
        # 设置深色标题栏
        try:
            set_dark_titlebar(self.winfo_id())
        except Exception:
            pass
        
        # 初始化UI
        self.init_ui()
        
        # 绑定事件
        self.bind_events()
        
        # 设置拖拽
        if DND_OK:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.on_drop)
    
    def init_ui(self):
        """初始化用户界面"""
        # 主容器
        if DND_OK:
            main_frame = self.ctk_container
        else:
            main_frame = self
        
        # 标题栏
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Logo和标题
        logo_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        logo_frame.pack(side="left")
        
        try:
            if os.path.exists(BRAND["logo_path"]):
                logo_img = Image.open(BRAND["logo_path"])
                logo_img = logo_img.resize((40, 40), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ctk.CTkLabel(logo_frame, image=logo_photo, text="")
                logo_label.image = logo_photo
                logo_label.pack(side="left", padx=(0, 10))
        except Exception:
            pass
        
        title_label = ctk.CTkLabel(
            logo_frame, 
            text=BRAND["app_name"], 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=PRIMARY
        )
        title_label.pack(side="left")
        
        # 主内容区域
        content_frame = ctk.CTkFrame(main_frame, fg_color=PANEL)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 文件选择区域
        file_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=20, pady=20)
        
        file_label = ctk.CTkLabel(
            file_frame, 
            text="选择PDF文件:", 
            font=ctk.CTkFont(size=16),
            text_color=TEXT
        )
        file_label.pack(anchor="w")
        
        file_select_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_select_frame.pack(fill="x", pady=10)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ctk.CTkEntry(
            file_select_frame, 
            textvariable=self.file_path_var,
            placeholder_text="拖拽PDF文件到这里，或点击选择...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            file_select_frame,
            text="浏览",
            command=self.browse_file,
            height=40,
            width=80,
            fg_color=PRIMARY,
            hover_color="#1a6bb8"
        )
        browse_btn.pack(side="right")
        
        # 处理选项区域
        options_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=10)
        
        options_label = ctk.CTkLabel(
            options_frame, 
            text="处理选项:", 
            font=ctk.CTkFont(size=16),
            text_color=TEXT
        )
        options_label.pack(anchor="w", pady=(0, 10))
        
        # 模型选择
        model_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        model_frame.pack(fill="x", pady=5)
        
        model_label = ctk.CTkLabel(
            model_frame, 
            text="AI模型:", 
            width=80,
            text_color=MUTED
        )
        model_label.pack(side="left")
        
        self.model_var = tk.StringVar(value=USE_MODEL)
        model_menu = ctk.CTkOptionMenu(
            model_frame,
            variable=self.model_var,
            values=["deepseek", "qwen"],
            fg_color=PANEL,
            button_color=PRIMARY,
            button_hover_color="#1a6bb8"
        )
        model_menu.pack(side="left", padx=10)
        
        # 输出目录
        output_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        output_frame.pack(fill="x", pady=5)
        
        output_label = ctk.CTkLabel(
            output_frame, 
            text="输出目录:", 
            width=80,
            text_color=MUTED
        )
        output_label.pack(side="left")
        
        self.output_path_var = tk.StringVar(value=os.path.join(BASE_DIR, "data", "OutPur_Data_Result"))
        output_entry = ctk.CTkEntry(
            output_frame, 
            textvariable=self.output_path_var,
            height=35
        )
        output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        output_btn = ctk.CTkButton(
            output_frame,
            text="选择",
            command=self.browse_output,
            height=35,
            width=60,
            fg_color=PRIMARY,
            hover_color="#1a6bb8"
        )
        output_btn.pack(side="right")
        
        # 处理按钮
        process_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        process_frame.pack(fill="x", padx=20, pady=20)
        
        self.process_btn = ctk.CTkButton(
            process_frame,
            text="开始处理",
            command=self.start_processing,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=PRIMARY,
            hover_color="#1a6bb8"
        )
        self.process_btn.pack(pady=10)
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(process_frame)
        self.progress_bar.pack(fill="x", pady=10)
        self.progress_bar.set(0)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            process_frame, 
            text="准备就绪", 
            text_color=MUTED
        )
        self.status_label.pack()
        
        # 日志区域
        log_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        log_label = ctk.CTkLabel(
            log_frame, 
            text="处理日志:", 
            font=ctk.CTkFont(size=16),
            text_color=TEXT
        )
        log_label.pack(anchor="w", pady=(0, 10))
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=ctk.CTkFont(size=12),
            fg_color="#1a1a1a",
            text_color="#e0e0e0"
        )
        self.log_text.pack(fill="both", expand=True)
        
        # 添加滚动条
        scrollbar = ctk.CTkScrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def bind_events(self):
        """绑定事件"""
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 窗口大小改变事件
        self.bind("<Configure>", self.on_resize)
    
    def browse_file(self):
        """浏览文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.log_message(f"已选择文件: {file_path}")
    
    def browse_output(self):
        """浏览输出目录"""
        output_path = filedialog.askdirectory(title="选择输出目录")
        if output_path:
            self.output_path_var.set(output_path)
            self.log_message(f"输出目录: {output_path}")
    
    def on_drop(self, event):
        """文件拖拽处理"""
        file_path = event.data
        if file_path.lower().endswith('.pdf'):
            self.file_path_var.set(file_path)
            self.log_message(f"拖拽文件: {file_path}")
        else:
            messagebox.showwarning("文件类型错误", "请拖拽PDF文件")
    
    def start_processing(self):
        """开始处理"""
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showerror("错误", "请选择PDF文件")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 禁用按钮
        self.process_btn.configure(state="disabled", text="处理中...")
        self.progress_bar.set(0)
        
        # 在新线程中处理
        thread = threading.Thread(target=self.process_file, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def process_file(self, file_path):
        """处理文件"""
        try:
            self.update_status("正在处理PDF文件...")
            self.progress_bar.set(0.2)
            
            # 调用批处理逻辑
            result = process_pdf(file_path, self.output_path_var.get())
            
            self.progress_bar.set(1.0)
            self.update_status("处理完成！")
            self.log_message("✅ 文件处理成功")
            
            # 显示结果
            if result:
                self.log_message(f"处理了 {len(result)} 页")
                for page in result:
                    self.log_message(f"第{page['page']}页: {page['type']}")
            
        except Exception as e:
            self.update_status("处理失败")
            self.log_message(f"❌ 错误: {str(e)}")
            messagebox.showerror("处理失败", f"处理文件时发生错误:\n{str(e)}")
        
        finally:
            # 恢复按钮
            self.process_btn.configure(state="normal", text="开始处理")
    
    def update_status(self, message):
        """更新状态"""
        self.status_label.configure(text=message)
        self.log_message(message)
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = threading.current_thread().name
        log_entry = f"[{timestamp}] {message}\n"
        
        # 在主线程中更新UI
        self.after(0, lambda: self.log_text.insert("end", log_entry))
        self.after(0, lambda: self.log_text.see("end"))
    
    def on_resize(self, event):
        """窗口大小改变事件"""
        if event.widget == self:
            # 保存窗口大小
            self.settings["win_w"] = event.width
            self.settings["win_h"] = event.height
    
    def on_closing(self):
        """关闭窗口事件"""
        # 保存设置
        save_settings(self.settings)
        
        # 销毁窗口
        self.destroy()

def main():
    """主函数"""
    try:
        app = FileSenseScanGUI()
        app.mainloop()
    except Exception as e:
        print(f"启动失败: {e}")
        messagebox.showerror("启动失败", f"应用启动失败:\n{str(e)}")

if __name__ == "__main__":
    main() 