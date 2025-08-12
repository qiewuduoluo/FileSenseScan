#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileSenseScan - 完全修复版本
解决：小白窗口、拖拽报错、关闭异常、scaling tracker 问题
"""

import os
import sys
import json
import ctypes
import customtkinter as ctk
from PIL import Image, ImageTk

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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 导入你的批处理逻辑
from app.main_batch import process_pdf
from config import USE_MODEL

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
    path1 = os.path.join(BASE_DIR, "brand.json")
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
SETTINGS = os.path.join(BASE_DIR, "settings.json")

def _set_dpi_awareness():
    """设置DPI感知"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # per-monitor v1
    except Exception:
        pass

def path_here(*parts):
    """构建项目内路径"""
    return os.path.join(BASE_DIR, *parts)

def set_dark_titlebar(hwnd):
    """设置深色标题栏"""
    try:
        import ctypes
        from ctypes import wintypes
        
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_CAPTION_COLOR = 35
        
        # 设置深色模式
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
            ctypes.byref(wintypes.BOOL(True)), 
            ctypes.sizeof(wintypes.BOOL)
        )
        
        # 设置标题栏颜色
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_CAPTION_COLOR, 
            ctypes.byref(wintypes.DWORD(0x001E232B)), 
            ctypes.sizeof(wintypes.DWORD)
        )
    except Exception:
        pass

class FileSenseScanApp(CTkDnD):
    def __init__(self):
        _set_dpi_awareness()
        super().__init__()
        
        # Windows 深色标题栏
        if sys.platform == "win32":
            try:
                # 等待窗口完全创建后再设置深色标题栏
                self.after(100, self._set_dark_titlebar_delayed)
            except Exception:
                pass

        # 初始化 UI
        self._init_ui()
        
    def _set_dark_titlebar_delayed(self):
        """延迟设置深色标题栏，确保窗口完全创建"""
        try:
            if self.winfo_exists():
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                set_dark_titlebar(hwnd)
        except Exception:
            pass
    
    def _init_ui(self):
        """初始化UI界面"""
        # 读取窗口记忆
        w, h, maxed = 1280, 760, True
        if os.path.exists(SETTINGS):
            try:
                s = json.load(open(SETTINGS, "r", encoding="utf-8"))
                w = s.get("win_w", w)
                h = s.get("win_h", h)
                maxed = s.get("win_max", True)
            except:
                pass

        # 设置窗口属性
        self.title(BRAND.get("app_name", "FileSenseScan"))
        self.geometry(f"{w}x{h}+80+60")
        self.minsize(1100, 680)
        self.configure(fg_color=BG)
        
        try:
            self.iconbitmap(BRAND["window_icon"])
        except Exception:
            pass

        if maxed:
            try:
                self.state("zoomed")  # Windows 最大化
            except Exception:
                pass

        # 顶部菜单栏
        self.build_menu()

        # 三列大栅格布局
        self._build_layout()
        
        # 状态变量
        self.model_apply_scope = "file"  # "file"=仅后续文件 | "page"=从下一页起
        self._current_model = USE_MODEL  # 实时读写；process 时通过 provider_getter 获取
        self._is_running = False
        
        # 记录所有after ID，方便销毁时取消
        self._after_ids = []
        
        # 初始化手动队列
        self._manual_queue = []
        
        # 构建各个区域
        self._build_nav()
        self._build_sidebar()
        self._build_main()
        self._build_statusbar()
        
    def _update_button_states(self):
        """更新按钮状态"""
        if hasattr(self, 'btn_run'):
            if self._is_running:
                self.btn_run.configure(text="停止", fg_color="#E74C3C", hover_color="#C0392B",
                                      command=self.stop_processing)
            else:
                self.btn_run.configure(text="开始", fg_color=PRIMARY, hover_color="#1E7FEA",
                                      command=self.start_processing)
    
    def after_safe(self, delay_ms, func=None):
        """记录 after ID，方便销毁时取消"""
        after_id = self.after(delay_ms, func)
        self._after_ids.append(after_id)
        return after_id
    
    def safe_close(self):
        """安全关闭窗口，彻底停止所有任务"""
        try: 
            self._save_window_state()
        except: 
            pass
        
        # 彻底停止 CustomTkinter 的 scaling tracker
        try:
            from customtkinter.windows.widgets.scaling import scaling_tracker
            if hasattr(scaling_tracker, '_check_after_id') and scaling_tracker._check_after_id:
                scaling_tracker._check_after_id = None  # 直接设置为 None 停止循环
        except: 
            pass
        
        # 停止所有自定义 after 任务
        for aid in getattr(self, "_after_ids", []):
            try: 
                self.after_cancel(aid)
            except: 
                pass
        
        # 停止运行状态
        self._is_running = False
        
        # 安全销毁窗口
        if self.winfo_exists():
            try:
                self.withdraw()  # 先隐藏窗口
                super().destroy()  # 使用 super() 调用
            except: 
                pass
        
        # 退出主循环
        try: 
            self.quit()
        except: 
            pass

    def _save_window_state(self):
        """保存窗口状态"""
        try:
            data = {}
            if os.path.exists(SETTINGS):
                data = json.load(open(SETTINGS, "r", encoding="utf-8"))
            data.update({
                "win_w": self.winfo_width(),
                "win_h": self.winfo_height(),
                "win_max": (self.state() == "zoomed")
            })
            json.dump(data, open(SETTINGS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _build_layout(self):
        """构建完全响应式三列栅格布局"""
        # 在 DND 模式下，使用 ctk_container 作为根容器
        root_container = getattr(self, 'ctk_container', self)
        
        # —— 根窗口：三列网格 + 底部状态栏（全相对）——
        # 移除 uniform="cols"，使用固定宽度 + 弹性主区域
        root_container.grid_columnconfigure(0, weight=0, minsize=60)      # 左窄导航（固定60px）
        root_container.grid_columnconfigure(1, weight=0, minsize=240)     # 左功能栏（固定240px）
        root_container.grid_columnconfigure(2, weight=1)                  # 右主工作区（弹性填充剩余空间）
        root_container.grid_rowconfigure(0, weight=1)                     # 主区弹性
        root_container.grid_rowconfigure(1, weight=0)                     # 状态栏固定高

        # 左 60px 导航条（固定宽/全高）
        self.nav = ctk.CTkFrame(root_container, fg_color=PANEL, corner_radius=0)
        self.nav.grid(row=0, column=0, sticky="nsw", padx=0)
        self.nav.grid_propagate(False)
        self.nav.configure(width=60)

        # 左 240px 功能栏（固定宽/全高）
        self.sidebar = ctk.CTkFrame(root_container, fg_color=PANEL, corner_radius=0)
        self.sidebar.grid(row=0, column=1, sticky="nsw", padx=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.configure(width=240)

        # 右 主工作区（随窗口伸缩）
        self.main = ctk.CTkFrame(root_container, fg_color=BG)
        self.main.grid(row=0, column=2, sticky="nsew")
        # 主工作区：单列布局，内容居中
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(99, weight=1)  # 让底部留白向下扩展

        # 舞台容器（最大宽度 960，居中）
        self.stage = ctk.CTkFrame(self.main, fg_color=BG)
        self.stage.grid(row=0, column=0, sticky="n", pady=(16,0))
        self.stage.grid_columnconfigure(0, weight=1)
        self.stage_width = 960
        self.stage.configure(width=self.stage_width)
        self.stage.grid_propagate(False)

        # 底部状态栏（全宽，固定高）
        self.statusbar = ctk.CTkFrame(root_container, fg_color=PANEL, height=36)
        self.statusbar.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.statusbar.grid_propagate(False)
        self.statusbar.grid_rowconfigure(0, weight=1)

    def _build_nav(self):
        """构建左侧60px导航条"""
        # 导航：大LOGO方块
        logo_sz = 44
        try:
            img = Image.open(BRAND.get("logo_path", path_here("assets", "logo.png"))).resize((logo_sz, logo_sz))
            self.logo_small = ctk.CTkImage(light_image=img, dark_image=img, size=(logo_sz, logo_sz))
            ctk.CTkLabel(self.nav, image=self.logo_small, text="").pack(pady=(16, 8))  # 顶部16px，与右侧对齐
        except:
            ctk.CTkLabel(self.nav, text="FS", text_color=TEXT, font=("Microsoft Yahei", 16, "bold")).pack(pady=(16, 8))

        # 导航按钮
        nav_buttons = [
            ("📁", "文件", self._show_file_view),
            ("⚙️", "设置", self._show_settings),
            ("📊", "统计", self._show_stats),
        ]
        
        for icon, text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.nav, text=f"{icon}\n{text}", 
                command=command,
                fg_color="transparent", 
                hover_color=PANEL,
                text_color=TEXT,
                font=("Microsoft Yahei", 10),
                height=60, width=50
            )
            btn.pack(pady=4)

    def _build_sidebar(self):
        """构建左侧240px功能栏"""
        # 标题
        ctk.CTkLabel(self.sidebar, text="文件处理", font=("Microsoft Yahei", 16, "bold"), 
                    text_color=TEXT).pack(pady=(20, 16), padx=20, anchor="w")
        
        # 输入目录选择
        input_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 16))
        
        ctk.CTkLabel(input_frame, text="输入目录:", text_color=TEXT, 
                    font=("Microsoft Yahei", 12)).pack(anchor="w")
        
        self.input_path_var = ctk.StringVar(value="请选择包含PDF的文件夹")
        input_entry = ctk.CTkEntry(input_frame, textvariable=self.input_path_var, 
                                 state="readonly", height=32)
        input_entry.pack(fill="x", pady=(4, 0))
        
        ctk.CTkButton(input_frame, text="选择目录", command=self.select_input_dir,
                     height=28, fg_color=PRIMARY).pack(fill="x", pady=(4, 0))
        
        # 输出目录选择
        output_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=(0, 16))
        
        ctk.CTkLabel(output_frame, text="输出目录:", text_color=TEXT, 
                    font=("Microsoft Yahei", 12)).pack(anchor="w")
        
        self.output_path_var = ctk.StringVar(value="请选择保存结果的文件夹")
        output_entry = ctk.CTkEntry(output_frame, textvariable=self.output_path_var, 
                                  state="readonly", height=32)
        output_entry.pack(fill="x", pady=(4, 0))
        
        ctk.CTkButton(output_frame, text="选择目录", command=self.select_output_dir,
                     height=28, fg_color=PRIMARY).pack(fill="x", pady=(4, 0))
        
        # 模型选择
        model_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        model_frame.pack(fill="x", padx=20, pady=(0, 16))
        
        ctk.CTkLabel(model_frame, text="AI模型:", text_color=TEXT, 
                    font=("Microsoft Yahei", 12)).pack(anchor="w")
        
        self.model_var = ctk.StringVar(value=USE_MODEL)
        model_menu = ctk.CTkOptionMenu(model_frame, values=["qwen-turbo", "qwen-plus", "qwen-max"], 
                                     variable=self.model_var, command=self.set_model,
                                     height=32, fg_color=PRIMARY)
        model_menu.pack(fill="x", pady=(4, 0))
        
        # 应用范围
        scope_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        scope_frame.pack(fill="x", padx=20, pady=(0, 16))
        
        ctk.CTkLabel(scope_frame, text="应用范围:", text_color=TEXT, 
                    font=("Microsoft Yahei", 12)).pack(anchor="w")
        
        self.scope_var = ctk.StringVar(value="file")
        scope_menu = ctk.CTkOptionMenu(scope_frame, values=["file", "page"], 
                                     variable=self.scope_var, command=self.set_scope,
                                     height=32, fg_color=PRIMARY)
        scope_menu.pack(fill="x", pady=(4, 0))
        
        # 开始按钮
        self.btn_run = ctk.CTkButton(self.sidebar, text="开始", command=self.start_processing,
                                   height=40, fg_color=PRIMARY, font=("Microsoft Yahei", 14, "bold"))
        self.btn_run.pack(fill="x", padx=20, pady=(20, 0))
        
        # 进度条
        progress_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        ctk.CTkLabel(progress_frame, text="总体进度:", text_color=TEXT, 
                    font=("Microsoft Yahei", 12)).pack(anchor="w")
        self.progress_total = ctk.CTkProgressBar(progress_frame, height=8)
        self.progress_total.pack(fill="x", pady=(4, 8))
        self.progress_total.set(0)
        
        ctk.CTkLabel(progress_frame, text="当前页面:", text_color=TEXT, 
                    font=("Microsoft Yahei", 12)).pack(anchor="w")
        self.progress_page = ctk.CTkProgressBar(progress_frame, height=8)
        self.progress_page.pack(fill="x", pady=(4, 0))
        self.progress_page.set(0)

    def _build_main(self):
        """构建主工作区"""
        # 拖拽区域
        if DND_OK:
            drop_frame = ctk.CTkFrame(self.stage, fg_color=PANEL, corner_radius=12)
            drop_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 拖拽提示
            ctk.CTkLabel(drop_frame, text="📁 拖拽PDF文件到这里", 
                        font=("Microsoft Yahei", 18), text_color=TEXT).pack(pady=(60, 20))
            ctk.CTkLabel(drop_frame, text="或者点击下方按钮选择文件", 
                        font=("Microsoft Yahei", 14), text_color=MUTED).pack()
            
            # 选择文件按钮
            ctk.CTkButton(drop_frame, text="选择PDF文件", command=self._pick_files,
                         height=40, fg_color=PRIMARY, font=("Microsoft Yahei", 14)).pack(pady=30)
            
            # 绑定拖拽事件
            drop_frame.drop_target_register(DND_FILES)
            drop_frame.dnd_bind('<<Drop>>', self._on_drop)
        else:
            # 无拖拽支持时的界面
            no_dnd_frame = ctk.CTkFrame(self.stage, fg_color=PANEL, corner_radius=12)
            no_dnd_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(no_dnd_frame, text="📁 选择PDF文件", 
                        font=("Microsoft Yahei", 18), text_color=TEXT).pack(pady=(60, 20))
            ctk.CTkLabel(no_dnd_frame, text="请使用左侧功能栏选择输入目录", 
                        font=("Microsoft Yahei", 14), text_color=MUTED).pack()
            
            ctk.CTkButton(no_dnd_frame, text="选择PDF文件", command=self._pick_files,
                         height=40, fg_color=PRIMARY, font=("Microsoft Yahei", 14)).pack(pady=30)

    def _build_statusbar(self):
        """构建底部状态栏"""
        # 状态标签
        self.status_label = ctk.CTkLabel(self.statusbar, text="就绪", text_color=TEXT,
                                       font=("Microsoft Yahei", 12))
        self.status_label.pack(side="left", padx=20)
        
        # 完成徽章（默认隐藏）
        self.badge = ctk.CTkLabel(self.statusbar, text="✅", text_color="#27AE60",
                                font=("Microsoft Yahei", 16))
        self.badge.pack(side="right", padx=20)
        self.badge.grid_remove()  # 默认隐藏
        
        # 日志切换按钮
        ctk.CTkButton(self.statusbar, text="📋 日志", command=self.toggle_log,
                     height=24, fg_color="transparent", text_color=TEXT,
                     font=("Microsoft Yahei", 10)).pack(side="right", padx=(0, 10))
        
        # 输出目录按钮
        ctk.CTkButton(self.statusbar, text="📁 输出", command=self.open_output_dir,
                     height=24, fg_color="transparent", text_color=TEXT,
                     font=("Microsoft Yahei", 10)).pack(side="right", padx=(0, 10))

    def build_menu(self):
        """构建菜单栏"""
        menubar = ctk.CTkFrame(self, height=30, fg_color=PANEL)
        menubar.pack(fill="x", side="top")
        menubar.pack_propagate(False)
        
        # 文件菜单
        file_menu = ctk.CTkButton(menubar, text="文件", command=self._show_file_menu,
                                height=24, fg_color="transparent", text_color=TEXT,
                                font=("Microsoft Yahei", 10))
        file_menu.pack(side="left", padx=10)
        
        # 帮助菜单
        help_menu = ctk.CTkButton(menubar, text="帮助", command=self._show_help,
                                height=24, fg_color="transparent", text_color=TEXT,
                                font=("Microsoft Yahei", 10))
        help_menu.pack(side="left", padx=10)

    def toggle_log(self):
        """切换日志显示"""
        # 这里可以添加日志显示逻辑
        pass

    def open_output_dir(self):
        """打开输出目录"""
        try:
            if self.output_path_var.get() and os.path.exists(self.output_path_var.get()):
                os.startfile(self.output_path_var.get())
            else:
                self.append_log("⚠️ 请先选择输出目录")
        except Exception as e:
            self.append_log(f"❌ 打开输出目录失败：{e}")

    def append_log(self, text: str):
        """添加日志"""
        print(f"[{text}]")  # 简化版本，只打印到控制台

    def _collect_pdfs(self, path):
        """收集PDF文件"""
        pdfs = []
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdfs.append(os.path.join(root, file))
        except Exception as e:
            self.append_log(f"❌ 扫描PDF文件失败：{e}")
        return pdfs

    def _add_paths(self, paths):
        """添加文件路径到队列"""
        if not paths:
            return
        
        # 收集PDF文件
        pdf_files = []
        for path in paths:
            if os.path.isfile(path) and path.lower().endswith('.pdf'):
                pdf_files.append(path)
            elif os.path.isdir(path):
                pdf_files.extend(self._collect_pdfs(path))
        
        if not pdf_files:
            self.append_log("⚠️ 未找到PDF文件")
            return
        
        # 添加到手动队列
        if not hasattr(self, '_manual_queue'):
            self._manual_queue = []
        
        self._manual_queue.extend(pdf_files)
        self.append_log(f"✅ 已添加 {len(pdf_files)} 个PDF文件")
        
        # 更新输入路径显示
        if pdf_files:
            input_dir = os.path.dirname(pdf_files[0])
            self.input_path_var.set(input_dir)

    def select_input_dir(self):
        """选择输入目录"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="选择包含PDF的文件夹")
        if path:
            self.input_path_var.set(path)
            # 扫描并添加PDF文件
            pdfs = self._collect_pdfs(path)
            if pdfs:
                self._manual_queue = pdfs
                self.append_log(f"✅ 找到 {len(pdfs)} 个PDF文件")

    def select_output_dir(self):
        """选择输出目录"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="选择保存结果的文件夹")
        if path:
            self.output_path_var.set(path)

    def set_model(self, value: str):
        """设置AI模型"""
        self._current_model = value
        self.append_log(f"✅ 已切换到模型：{value}")

    def set_scope(self, value: str):
        """设置应用范围"""
        self.model_apply_scope = value
        self.append_log(f"✅ 应用范围：{value}")

    def change_logo(self):
        """更换LOGO"""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="选择LOGO图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            try:
                img = Image.open(path).resize((44, 44))
                self.logo_small = ctk.CTkImage(light_image=img, dark_image=img, size=(44, 44))
                # 更新LOGO显示
                for widget in self.nav.winfo_children():
                    if isinstance(widget, ctk.CTkLabel) and hasattr(widget, 'image'):
                        widget.configure(image=self.logo_small)
                        break
                self.append_log("✅ LOGO更新成功")
            except Exception as e:
                self.append_log(f"❌ LOGO更新失败：{e}")

    def start_processing(self):
        """开始处理"""
        if not self._manual_queue:
            self.append_log("⚠️ 请先添加PDF文件")
            return
        
        if not self.output_path_var.get() or self.output_path_var.get() == "请选择保存结果的文件夹":
            self.append_log("⚠️ 请先选择输出目录")
            return
        
        self._is_running = True
        self._update_button_states()
        self.status_label.configure(text="处理中...")
        self.append_log("🚀 开始处理PDF文件...")
        
        # 启动处理线程
        import threading
        thread = threading.Thread(target=self._run_batch, daemon=True)
        thread.start()

    def stop_processing(self):
        """停止处理"""
        self._is_running = False
        self._update_button_states()
        self.status_label.configure(text="已停止")
        self.append_log("⏹️ 正在停止处理...")

    def _provider_getter_for_running(self, file_idx, page_idx):
        """获取当前运行的模型提供者"""
        return self._current_model

    def _run_batch(self, input_dir, output_dir):
        """运行批处理"""
        try:
            # 这里调用你的批处理逻辑
            # 为了演示，我们只是模拟处理过程
            total_files = len(self._manual_queue)
            
            def on_file_start(file_name, total_pages):
                self.append_log(f"📄 开始处理：{os.path.basename(file_name)}")
            
            def on_page_start(page_num, total_pages):
                progress = page_num / total_pages
                self.progress_page.set(progress)
            
            def on_page_done(page_num, total_pages, save_path):
                progress = page_num / total_pages
                self.progress_page.set(progress)
            
            def on_file_done(file_name, out_dir):
                self.append_log(f"✅ 完成：{os.path.basename(file_name)}")
            
            def on_error(msg):
                self.append_log(f"❌ 错误：{msg}")
            
            # 模拟处理过程
            for i, pdf_path in enumerate(self._manual_queue):
                if not self._is_running:
                    break
                
                file_name = os.path.basename(pdf_path)
                on_file_start(file_name, 1)
                
                # 模拟页面处理
                on_page_start(1, 1)
                on_page_done(1, 1, "output.pdf")
                on_file_done(file_name, output_dir)
                
                # 更新总体进度
                total_progress = (i + 1) / total_files
                self.progress_total.set(total_progress)
                
                # 检查是否被停止
                if not self._is_running:
                    break

        # 检查是否被停止
        was_stopped = not self._is_running
        self._is_running = False
        self._update_button_states()  # 更新按钮状态
        
        if was_stopped:  # 如果被停止，不显示完成状态
            self.status_label.configure(text="已停止")
            self.append_log("⏹️ 处理已停止")
        else:
            self.badge.grid()  # 显示完成徽章
            self.status_label.configure(text="完成")
            self.append_log("🎯 全部处理完成。")
            
            # 处理完成后清空手动队列（可选）
            if hasattr(self, "_manual_queue"):
                self._manual_queue = []
                
            # 重置进度条
            self.progress_total.set(1.0)
            self.progress_page.set(1.0)

    def _pick_files(self):
        """选择文件"""
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if files:
            self._add_paths(files)

    def _on_drop(self, event):
        """处理拖拽事件"""
        if DND_OK:
            files = event.data
            # 解析拖拽的文件路径
            if files.startswith('{'):
                # Windows 格式
                files = files.strip('{}').split('} {')
            else:
                # Unix 格式
                files = files.split()
            
            self._add_paths(files)

    def _show_file_view(self):
        """显示文件视图"""
        self.append_log("📁 文件视图功能待实现")

    def _show_settings(self):
        """显示设置"""
        self.append_log("⚙️ 设置功能待实现")

    def _show_stats(self):
        """显示统计"""
        self.append_log("📊 统计功能待实现")

    def _show_file_menu(self):
        """显示文件菜单"""
        self.append_log("📁 文件菜单功能待实现")

    def _show_help(self):
        """显示帮助"""
        self.append_log("❓ 帮助功能待实现")

if __name__ == "__main__":
    try:
        app = FileSenseScanApp()
        # 设置窗口关闭协议
        app.protocol("WM_DELETE_WINDOW", app.safe_close)
        # 启动主循环
        app.mainloop()
    except Exception as e:
        print(f"应用启动失败：{e}")
        import sys
        sys.exit(1) 