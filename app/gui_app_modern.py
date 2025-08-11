import os
import sys
import json
import threading
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
import customtkinter as ctk
from PIL import Image

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

# ===== 拖拽支持 =====
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_OK = True
except Exception:
    DND_OK = False
    DND_FILES = None
    TkinterDnD = None

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
        """安全关闭窗口，取消所有任务并销毁"""
        try:
            self._save_window_state()
        except:
            pass

        # 直接停止 scaling tracker 循环
        try:
            from customtkinter.windows.widgets.scaling import scaling_tracker
            scaling_tracker._check_after_id = None
        except:
            pass

        # 停止自己记录的 after
        for aid in getattr(self, "_after_ids", []):
            try:
                self.after_cancel(aid)
            except:
                pass

        self._is_running = False

        if self.winfo_exists():
            super().destroy()

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

        # 导航按钮（大图标风格，紧凑布局）
        self.btn_run = ctk.CTkButton(self.nav, text="开始", fg_color=PRIMARY, hover_color="#1E7FEA",
                                     command=self.start_processing, width=40, height=40)
        self.btn_run.pack(pady=(4, 6))
        
        # 添加按钮状态更新方法
        self._update_button_states()

        self.btn_input = ctk.CTkButton(self.nav, text="输入", fg_color=PANEL, command=self.select_input_dir,
                                       width=40, height=36, border_width=1, border_color="#2F3742")
        self.btn_input.pack(pady=4)

        self.btn_output = ctk.CTkButton(self.nav, text="输出", fg_color=PANEL, command=self.select_output_dir,
                                        width=40, height=36, border_width=1, border_color="#2F3742")
        self.btn_output.pack(pady=4)

    def _build_sidebar(self):
        """构建左侧240px功能栏"""
        # 关键：所有表单放进 body 容器；顶部 padding 设为 16px，与头像对齐
        self.sidebar_body = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_body.pack(fill="both", expand=True, padx=(0,6), pady=(16, 12))  # 左0右6，减少空带

        # 输入目录
        ctk.CTkLabel(self.sidebar_body, text="输入目录", text_color=MUTED)\
            .pack(anchor="w", pady=(0, 4))
        self.input_var = ctk.StringVar(value=path_here("Data_Source"))
        self.input_entry = ctk.CTkEntry(self.sidebar_body, textvariable=self.input_var, width=220)
        self.input_entry.pack(fill="x", pady=(0, 8))

        # 输出目录
        ctk.CTkLabel(self.sidebar_body, text="输出目录", text_color=MUTED)\
            .pack(anchor="w", pady=(6, 4))
        self.output_var = ctk.StringVar(value=path_here("OutPur_Data_Result"))
        self.output_entry = ctk.CTkEntry(self.sidebar_body, textvariable=self.output_var, width=220)
        self.output_entry.pack(fill="x", pady=(0, 8))

        # 模型选择
        ctk.CTkLabel(self.sidebar_body, text="模型", text_color=MUTED)\
            .pack(anchor="w", pady=(6, 4))
        self.btn_model = ctk.CTkSegmentedButton(self.sidebar_body, values=["deepseek", "qwen"],
                                                command=self.set_model)
        self.btn_model.set(USE_MODEL)
        self.btn_model.pack(fill="x", pady=(0, 12))

        # 设置区
        ctk.CTkLabel(self.sidebar_body, text="⚙️ 设置", text_color=MUTED, font=("Microsoft Yahei", 12))\
            .pack(anchor="w", pady=(6, 6))
        ctk.CTkButton(self.sidebar_body, text="打开输出目录", command=self.open_output_dir,
                      fg_color=PANEL, hover_color="#272D36", border_width=1, border_color="#2F3742",
                      height=32).pack(fill="x")

    def _build_main(self):
        """构建中央舞台工作区（紧凑居中）"""
        # 标题
        title = ctk.CTkLabel(self.stage, text="批量识别与总结",
                             text_color=TEXT, font=("Microsoft Yahei", 20, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=0, pady=(0,8))

        # 总进度（标题 + 进度条）
        self.lbl_total = ctk.CTkLabel(self.stage, text="总进度", text_color=MUTED)
        self.lbl_total.grid(row=1, column=0, sticky="w")

        self.progress_total = ctk.CTkProgressBar(self.stage, height=14, progress_color=PRIMARY)
        self.progress_total.grid(row=2, column=0, sticky="we", pady=(0,8))
        self.progress_total.set(0)

        # 页进度（标题 + 进度条）
        self.lbl_page = ctk.CTkLabel(self.stage, text="页进度", text_color=MUTED)
        self.lbl_page.grid(row=3, column=0, sticky="w")

        self.progress_page = ctk.CTkProgressBar(self.stage, height=10, progress_color=PRIMARY)
        self.progress_page.grid(row=4, column=0, sticky="we", pady=(0,12))
        self.progress_page.set(0)

        # === 中央"投递区"卡片（自适应尺寸、可点击、可拖拽） ===
        self.card = ctk.CTkFrame(self.stage, fg_color=PANEL, corner_radius=16)
        self.card.grid(row=5, column=0, sticky="n", pady=(0,12))
        # 卡片尺寸自适应
        self.DZ_W, self.DZ_H = 560, 320
        self.card.configure(width=self.DZ_W + 32, height=self.DZ_H + 80)

        # 内层 wrap 自适应居中承载 drop zone
        self.drop_wrap = ctk.CTkFrame(self.card, fg_color="transparent")
        self.drop_wrap.pack(expand=True, fill="both")  # ✅ 改成 pack 并撑满

        self.drop_canvas = tk.Canvas(self.drop_wrap, width=self.DZ_W, height=self.DZ_H,
                                     highlightthickness=0, bd=0, bg=PANEL)
        self.drop_canvas.pack(expand=True, fill="both", padx=12, pady=12)

        # 画虚线框 + 文案（自适应尺寸）
        def draw_dropzone():
            c = self.drop_canvas
            c.delete("all")
            w = c.winfo_width()
            h = c.winfo_height()
            if w <= 1 or h <= 1:  # 避免尺寸为0
                return
            pad = 14
            # 外层虚线框 - 颜色更对比，虚线更清晰
            c.create_rectangle(pad, pad, w-pad, h-pad, dash=(6,4), outline="#3A4757", width=1.2)
            # 中心坐标重新计算
            cx, cy = w/2, h/2
            # 图标（简单加号），也可以换成图片
            c.create_oval(cx-28, cy-64, cx+28, cy-8, outline="#6EA8FF", width=2)
            c.create_line(cx, cy-56, cx, cy-16, fill="#6EA8FF", width=2)
            c.create_line(cx-20, cy-36, cx+20, cy-36, fill="#6EA8FF", width=2)
            # 主文案
            c.create_text(cx, cy+10, text="点击添加文件或拖拽文件/文件夹到这里",
                          fill="#9AA4B2", font=("Microsoft Yahei", 14))
            # 副文案
            c.create_text(cx, cy+36, text="* 仅支持 PDF；拖入文件夹将自动递归添加其中的 PDF",
                          fill="#6B7480", font=("Microsoft Yahei", 10))
        draw_dropzone()
        
        # 让它在窗口尺寸变化时重新绘制
        self.drop_canvas.bind("<Configure>", lambda e: draw_dropzone())

        # 点击打开文件选择器
        def pick_files(event=None):
            from tkinter import filedialog
            paths = filedialog.askopenfilenames(title="选择 PDF 文件", filetypes=[("PDF", "*.pdf")])
            if not paths: return
            self._add_paths(paths)

        # 绑定点击
        self.drop_canvas.bind("<Button-1>", pick_files)

        # 支持拖拽（若 tkinterdnd2 可用）
        if DND_OK:
            try:
                self.drop_canvas.drop_target_register(DND_FILES)
                self.drop_canvas.dnd_bind("<<Drop>>", lambda e: self._add_paths(self.tk.splitlist(e.data)))
                print("✅ 拖拽功能已启用")
            except Exception as e:
                print(f"⚠️ 拖拽功能初始化失败：{e}")
                # 如果拖拽失败，至少保持点击功能

        # 按钮条（横向自适应，固定高）
        btn_bar = ctk.CTkFrame(self.stage, fg_color=BG)
        btn_bar.grid(row=6, column=0, sticky="w", pady=(2,0))  # 只靠左即可
        
        ctk.CTkButton(btn_bar, text="打开输出目录", command=self.open_output_dir)\
            .pack(side="left", padx=4)
        ctk.CTkButton(btn_bar, text="查看日志", command=self.toggle_log)\
            .pack(side="left", padx=4)
        ctk.CTkButton(btn_bar, text="清空日志", command=lambda: self.log_box.delete("1.0", "end"))\
            .pack(side="left", padx=4)

        # 日志区（可折叠显示：显示时用 nsew 占据剩余空间）
        self.log_box = ctk.CTkTextbox(self.stage, fg_color=PANEL, text_color=TEXT, height=180, width=self.stage_width)
        self.log_shown = False
        # 显示： self.log_box.grid(row=7, column=0, sticky="we", pady=(8,12))
        # 隐藏： self.log_box.grid_remove()

    def _build_statusbar(self):
        """构建底部状态栏"""
        self.statusbar.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(self.statusbar, text="就绪", text_color=MUTED)
        self.status_label.grid(row=0, column=0, sticky="w", padx=12)
        
        self.badge = ctk.CTkLabel(self.statusbar, text="完成", text_color=TEXT,
                                  fg_color=PRIMARY, corner_radius=12, padx=10, pady=4)
        self.badge.grid(row=0, column=1, sticky="e", padx=12)
        self.badge.grid_remove()  # 处理时隐藏/显示

    # ---------- 菜单栏 ----------
    def build_menu(self):
        menubar = Menu(self)
        self.configure(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="选择输入目录", command=self.select_input_dir)
        file_menu.add_command(label="选择输出目录", command=self.select_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.safe_close)
        menubar.add_cascade(label="文件", menu=file_menu)

        settings_menu = Menu(menubar, tearoff=0)
        settings_menu.add_command(label="更换LOGO...", command=self.change_logo)
        settings_menu.add_command(label="选择模型：DeepSeek", command=lambda: self.set_model("deepseek"))
        settings_menu.add_command(label="选择模型：通义千问", command=lambda: self.set_model("qwen"))
        menubar.add_cascade(label="设置", menu=settings_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=lambda: messagebox.showinfo("关于", "FileSenseScan\n批量PDF识别与总结工具"))
        menubar.add_cascade(label="帮助", menu=help_menu)

    # ---------- 功能方法 ----------
    def toggle_log(self):
        """切换日志显示"""
        if self.log_shown:
            self.log_box.grid_remove()  # 保持网格关系，展开时恢复自适应
            self.log_shown = False
        else:
            self.log_box.grid(row=7, column=0, sticky="we", pady=(8,12))  # 显示时用 we 占据剩余空间
            self.log_shown = True

    def open_output_dir(self):
        """打开输出目录"""
        output_dir = self.output_var.get().strip()
        if os.path.exists(output_dir):
            try:
                os.startfile(output_dir)
            except Exception:
                messagebox.showinfo("提示", f"输出目录：{output_dir}")
        else:
            messagebox.showerror("错误", "输出目录不存在")

    def append_log(self, text: str):
        """添加日志"""
        if not hasattr(self, 'log_box') or not self.log_shown:
            return
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.update_idletasks()

    def _collect_pdfs(self, path):
        """收集PDF文件"""
        pdfs = []
        try:
            # 标准化路径
            path = os.path.normpath(path)
            
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        if f.lower().endswith(".pdf"):
                            pdfs.append(os.path.join(root, f))
            elif os.path.isfile(path) and path.lower().endswith(".pdf"):
                pdfs.append(path)
        except Exception as e:
            print(f"⚠️ 处理路径失败：{path} - {e}")
        return pdfs

    def _add_paths(self, paths):
        """添加文件路径"""
        # paths: list[str] 文件或目录
        if not paths:
            return
            
        # 处理路径，确保是列表格式
        if isinstance(paths, str):
            paths = [paths]
            
        added = []
        for p in paths:
            # 处理 Windows 拖拽路径格式
            if p.startswith('{') and p.endswith('}'):
                p = p[1:-1]  # 移除花括号
            added.extend(self._collect_pdfs(p))
            
        if not added:
            # 确保日志框可见后再添加日志
            if not self.log_shown:
                self.toggle_log()
            self.append_log("⚠️ 未发现 PDF。")
            return
            
        # 记录到一个待处理列表（没有就创建）
        if not hasattr(self, "_manual_queue"):
            self._manual_queue = []
            
        # 去重
        exist = set(self._manual_queue)
        for p in added:
            if p not in exist:
                self._manual_queue.append(p)
                exist.add(p)
                
        # 确保日志框可见后再添加日志
        if not self.log_shown:
            self.toggle_log()
        self.append_log(f"📥 已添加 {len(added)} 个 PDF（累计 {len(self._manual_queue)} 个待处理）")

    def select_input_dir(self):
        """选择输入目录"""
        path = filedialog.askdirectory(initialdir=BASE_DIR)
        if path:
            self.input_var.set(path)

    def select_output_dir(self):
        """选择输出目录"""
        path = filedialog.askdirectory(initialdir=BASE_DIR)
        if path:
            self.output_var.set(path)

    def set_model(self, value: str):
        """设置模型"""
        self._current_model = value  # 👈 立刻写入共享变量
        
        # 持久化 config.py（保持原逻辑）
        cfg = os.path.join(BASE_DIR, "config.py")
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(cfg, "w", encoding="utf-8") as f:
                found = False
                for line in lines:
                    if line.strip().startswith("USE_MODEL"):
                        f.write(f'USE_MODEL = os.getenv("USE_MODEL", "{value}")  # deepseek | qwen\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'\nUSE_MODEL = os.getenv("USE_MODEL", "{value}")  # deepseek | qwen\n')
        except Exception as e:
            messagebox.showerror("错误", f"写入配置失败：{e}")

        # 确保日志框可见后再添加日志
        if not self.log_shown:
            self.toggle_log()
            
        if self._is_running:
            if self.model_apply_scope == "page":
                self.append_log(f"🔁 模型已切换为 {value}，将从【下一页】起生效。")
            else:
                self.append_log(f"🔁 模型已切换为 {value}，将用于【后续文件】。")
        else:
            self.append_log(f"✅ 已切换模型：{value}")
        self.btn_model.set(value)

    def change_logo(self):
        """更换LOGO"""
        path = filedialog.askopenfilename(title="选择LOGO图片", filetypes=[("Image", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")])
        if not path:
            return
        BRAND["logo_path"] = path
        brand_path = os.path.join(BASE_DIR, "brand.json")
        try:
            with open(brand_path, "w", encoding="utf-8") as f:
                json.dump(BRAND, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("提示", "LOGO已更换，重启应用后生效。")
        except Exception as e:
            messagebox.showerror("错误", f"保存brand.json失败：{e}")

    def start_processing(self):
        """开始处理"""
        if self._is_running:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return
            
        input_dir = self.input_var.get().strip()
        output_dir = self.output_var.get().strip()

        if not input_dir:
            messagebox.showerror("错误", "请输入输入目录")
            return
        if not output_dir:
            messagebox.showerror("错误", "请输入输出目录")
            return
            
        if not os.path.isdir(input_dir):
            messagebox.showerror("错误", "请输入有效的输入目录")
            return
        if not os.path.isdir(output_dir):
            messagebox.showerror("错误", "请输入有效的输出目录")
            return

        # 确保日志框可见
        if not self.log_shown:
            self.toggle_log()

        threading.Thread(target=self._run_batch, args=(input_dir, output_dir), daemon=True).start()
        
    def stop_processing(self):
        """停止处理"""
        if self._is_running:
            self._is_running = False
            self.append_log("⏹️ 正在停止处理...")
            self._update_button_states()

    def _provider_getter_for_running(self, file_idx, page_idx):
        """若 scope=file 且当前文件尚未开始，用启动时快照；否则每页读取"""
        if self.model_apply_scope == "file":
            return self._file_model_snapshot  # 在每个文件开始前设置
        return self._current_model

    def _run_batch(self, input_dir, output_dir):
        """运行批处理"""
        # 优先使用手动队列
        if hasattr(self, "_manual_queue") and self._manual_queue:
            files = list(self._manual_queue)
            self.append_log(f"📋 使用手动队列：{len(files)} 个文件")
        else:
            try:
                files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
                self.append_log(f"📁 扫描目录：{len(files)} 个文件")
            except Exception as e:
                self.append_log(f"❌ 扫描目录失败：{e}")
                self._is_running = False
                self._update_button_states()
                return

        total = len(files)
        if total == 0:
            self.append_log("⚠️ 没有可处理的 PDF。")
            self._is_running = False
            self._update_button_states()
            return

        self._is_running = True
        self._update_button_states()  # 更新按钮状态
        self.progress_total.set(0)
        self.progress_page.set(0)
        done = 0

        # 确保日志框可见
        if not self.log_shown:
            self.toggle_log()

        self.append_log("🚀 开始批量处理...")
        self.badge.grid_remove()  # 隐藏完成徽章
        
        # 把文件名（去目录）给日志更友好
        names = [os.path.basename(p) for p in files]
        
        for idx, (pdf_path, name) in enumerate(zip(files, names), start=1):
            # 检查是否被停止
            if not self._is_running:
                self.append_log("⏹️ 处理已停止")
                break
                
            # 文件开始：快照模型（scope=file）
            if self.model_apply_scope == "file":
                self._file_model_snapshot = self._current_model

            def on_file_start(file_name, total_pages):
                self.status_label.configure(text=f"处理 {idx}/{total}：{file_name}")
                self.append_log(f"📄 开始处理（共 {total_pages} 页）：{file_name}")
                self.progress_page.set(0)

            def on_page_start(page_num, total_pages):
                self.append_log(f"· 第 {page_num}/{total_pages} 页…")

            def on_page_done(page_num, total_pages, save_path):
                if self._is_running:  # 只有在运行中才更新进度
                    self.progress_page.set(page_num/total_pages)
                if save_path:
                    self.append_log(f"  ✅ 完成第 {page_num} 页 → {os.path.basename(save_path)}")

            def on_file_done(file_name, out_dir):
                if self._is_running:  # 只有在运行中才更新进度
                    self.append_log(f"✅ 文件完成：{file_name}")
                    nonlocal done
                    done += 1
                    self.progress_total.set(done/total)
                else:
                    self.append_log(f"⏹️ 文件处理被停止：{file_name}")

            def on_error(msg):
                if self._is_running:  # 只有在运行中才记录错误
                    self.append_log(f"❌ {msg}")
                else:
                    self.append_log(f"⏹️ 错误（已停止）：{msg}")

            try:
                from functools import partial
                provider_getter = lambda: self._provider_getter_for_running(idx, None)
                process_pdf(
                    pdf_path, output_dir,
                    callbacks={
                        "on_file_start": on_file_start,
                        "on_page_start": on_page_start,
                        "on_page_done": on_page_done,
                        "on_file_done": on_file_done,
                        "on_error": on_error,
                    },
                    provider_getter=provider_getter
                )
            except Exception as e:
                if self._is_running:  # 只有在运行中才记录错误
                    self.append_log(f"❌ 失败: {name} - {e}")
                else:
                    self.append_log(f"⏹️ 失败（已停止）: {name} - {e}")
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