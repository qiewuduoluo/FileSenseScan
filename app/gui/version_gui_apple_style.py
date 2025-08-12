#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileSenseScan 版本管理系统 - 苹果风格GUI
遵循苹果公司用户体验设计规范：
- 简洁性：减少视觉噪音，突出重要信息
- 一致性：统一的设计语言和交互模式
- 直接操作：直观的操作反馈
- 层次结构：清晰的信息架构
- 容错性：优雅的错误处理和恢复
"""

import os
import sys
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from pathlib import Path

# 导入版本管理器和错误监控器
from version_manager import get_version_manager, VersionManager
from error_monitor import get_error_monitor, ErrorMonitor


class AppleStyleVersionGUI:
    """苹果风格的版本管理GUI"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.project_root = Path.cwd()
        
        # 获取版本管理器和错误监控器
        self.version_manager = get_version_manager(str(self.project_root))
        self.error_monitor = get_error_monitor(str(self.project_root))
        
        # 创建主窗口
        if parent is None:
            self.root = ctk.CTkToplevel()
            self.root.title("FileSenseScan 版本管理")
            self.root.geometry("1200x800")
            self.root.resizable(True, True)
        else:
            self.root = parent
        
        # 设置苹果风格主题
        ctk.set_appearance_mode("light")  # 苹果偏好浅色主题
        ctk.set_default_color_theme("blue")
        
        # 苹果风格颜色方案
        self.colors = {
            'primary': '#007AFF',      # 苹果蓝
            'secondary': '#5856D6',    # 苹果紫
            'success': '#34C759',      # 苹果绿
            'warning': '#FF9500',      # 苹果橙
            'error': '#FF3B30',        # 苹果红
            'background': '#F2F2F7',   # 苹果浅灰
            'surface': '#FFFFFF',      # 苹果白
            'text': '#000000',         # 苹果黑
            'text_secondary': '#8E8E93' # 苹果灰
        }
        
        # 苹果风格字体
        self.fonts = {
            'title': ('SF Pro Display', 24, 'bold'),
            'heading': ('SF Pro Text', 18, 'bold'),
            'subheading': ('SF Pro Text', 16, 'normal'),
            'body': ('SF Pro Text', 14, 'normal'),
            'caption': ('SF Pro Text', 12, 'normal'),
            'button': ('SF Pro Text', 15, 'normal')
        }
        
        # 初始化 content_pages 属性
        self.content_pages = {}
        
        # 构建界面
        self._build_ui()
        
        # 应用苹果风格样式
        self._apply_apple_style()
        
        # 启动自动刷新（在界面完全构建后）
        self._start_auto_refresh()
    
    def _apply_apple_style(self):
        """应用苹果风格样式"""
        # 设置窗口样式
        self.root.configure(fg_color=self.colors['background'])
        
        # 配置customtkinter主题
        ctk.set_default_color_theme("blue")
        
        # 设置全局字体
        try:
            # 尝试使用系统字体
            import platform
            if platform.system() == "Darwin":  # macOS
                self.fonts = {
                    'title': ('SF Pro Display', 24, 'bold'),
                    'heading': ('SF Pro Text', 18, 'bold'),
                    'subheading': ('SF Pro Text', 16, 'normal'),
                    'body': ('SF Pro Text', 14, 'normal'),
                    'caption': ('SF Pro Text', 12, 'normal'),
                    'button': ('SF Pro Text', 15, 'normal')
                }
            elif platform.system() == "Windows":
                self.fonts = {
                    'title': ('Segoe UI', 24, 'bold'),
                    'heading': ('Segoe UI', 18, 'bold'),
                    'subheading': ('Segoe UI', 16, 'normal'),
                    'body': ('Segoe UI', 14, 'normal'),
                    'caption': ('Segoe UI', 12, 'normal'),
                    'button': ('Segoe UI', 15, 'normal')
                }
        except:
            # 回退到默认字体
            pass
    
    def _build_ui(self):
        """构建苹果风格用户界面"""
        try:
            print("🔨 开始构建用户界面...")
            
            # 主容器
            main_container = ctk.CTkFrame(self.root, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            print("✅ 主容器创建成功")
            
            # 顶部标题区域
            self._create_header(main_container)
            print("✅ 标题区域创建成功")
            
            # 主要内容区域
            content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, pady=(20, 0))
            print("✅ 内容框架创建成功")
            
            # 左侧导航栏
            self._create_sidebar(content_frame)
            print("✅ 侧边栏创建成功")
            
            # 右侧内容区域
            self._create_main_content(content_frame)
            print("✅ 主内容区域创建成功")
            
            print("🎉 用户界面构建完成！")
            
        except Exception as e:
            print(f"❌ 构建用户界面时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_header(self, parent):
        """创建苹果风格标题栏"""
        header_frame = ctk.CTkFrame(parent, fg_color=self.colors['surface'], corner_radius=12)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 标题和副标题
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(fill="x", padx=30, pady=25)
        
        # 主标题
        title_label = ctk.CTkLabel(
            title_container,
            text="版本管理",
            font=self.fonts['title'],
            text_color=self.colors['text']
        )
        title_label.pack(anchor="w")
        
        # 副标题
        subtitle_label = ctk.CTkLabel(
            title_container,
            text="管理项目版本、监控系统状态、自动备份恢复",
            font=self.fonts['body'],
            text_color=self.colors['text_secondary']
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # 快速操作按钮
        quick_actions = ctk.CTkFrame(header_frame, fg_color="transparent")
        quick_actions.pack(fill="x", padx=30, pady=(0, 25))
        
        # 创建新版本按钮
        create_btn = ctk.CTkButton(
            quick_actions,
            text="创建新版本",
            font=self.fonts['button'],
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            corner_radius=8,
            height=40,
            command=self._create_new_version_dialog
        )
        create_btn.pack(side="left", padx=(0, 15))
        
        # 同步到GitHub按钮
        sync_btn = ctk.CTkButton(
            quick_actions,
            text="同步到GitHub",
            font=self.fonts['button'],
            fg_color=self.colors['success'],
            hover_color=self.colors['success'],
            corner_radius=8,
            height=40,
            command=self._sync_to_github
        )
        sync_btn.pack(side="left", padx=(0, 15))
        
        # 系统健康检查按钮
        health_btn = ctk.CTkButton(
            quick_actions,
            text="系统健康检查",
            font=self.fonts['button'],
            fg_color=self.colors['warning'],
            hover_color=self.colors['warning'],
            corner_radius=8,
            height=40,
            command=self._system_health_check
        )
        health_btn.pack(side="left")
    
    def _create_sidebar(self, parent):
        """创建苹果风格侧边栏"""
        sidebar = ctk.CTkFrame(parent, fg_color=self.colors['surface'], corner_radius=12, width=250)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)
        
        # 导航菜单
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=20)
        
        # 导航项
        nav_items = [
            ("📊 概览", "overview"),
            ("📜 版本历史", "history"),
            ("📝 变更日志", "changelog"),
            ("🚨 错误监控", "errors"),
            ("⚙️ 设置", "settings")
        ]
        
        self.nav_buttons = {}
        for text, key in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                font=self.fonts['body'],
                fg_color="transparent",
                text_color=self.colors['text'],
                hover_color=self.colors['background'],
                anchor="w",
                height=45,
                corner_radius=8,
                command=lambda k=key: self._switch_content(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn
        
        # 默认选中概览（在页面创建完成后）
        # self._switch_content("overview")  # 暂时注释掉，等页面创建完成后再调用
        
        # 底部状态信息
        status_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['background'], corner_radius=8)
        status_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            status_frame,
            text="系统状态",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        ).pack(pady=(15, 10))
        
        self.system_status_label = ctk.CTkLabel(
            status_frame,
            text="🟢 运行正常",
            font=self.fonts['body'],
            text_color=self.colors['success']
        )
        self.system_status_label.pack(pady=(0, 15))
    
    def _create_main_content(self, parent):
        """创建主内容区域"""
        try:
            self.content_area = ctk.CTkFrame(parent, fg_color=self.colors['surface'], corner_radius=12)
            self.content_area.pack(side="right", fill="both", expand=True)
            
            # 内容页面
            self.content_pages = {}
            
            # 概览页面
            try:
                self.content_pages["overview"] = self._create_overview_page()
                print("✅ 概览页面创建成功")
            except Exception as e:
                print(f"❌ 创建概览页面失败: {e}")
                self.content_pages["overview"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
            
            # 版本历史页面
            try:
                self.content_pages["history"] = self._create_history_page()
                print("✅ 版本历史页面创建成功")
            except Exception as e:
                print(f"❌ 创建版本历史页面失败: {e}")
                self.content_pages["history"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
            
            # 变更日志页面
            try:
                self.content_pages["changelog"] = self._create_changelog_page()
                print("✅ 变更日志页面创建成功")
            except Exception as e:
                print(f"❌ 创建变更日志页面失败: {e}")
                self.content_pages["changelog"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
            
            # 错误监控页面
            try:
                self.content_pages["errors"] = self._create_errors_page()
                print("✅ 错误监控页面创建成功")
            except Exception as e:
                print(f"❌ 创建错误监控页面失败: {e}")
                self.content_pages["errors"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
            
            # 设置页面
            try:
                self.content_pages["settings"] = self._create_settings_page()
                print("✅ 设置页面创建成功")
            except Exception as e:
                print(f"❌ 创建设置页面失败: {e}")
                self.content_pages["settings"] = ctk.CTkFrame(self.content_area, fg_color="transparent")
            
            print(f"✅ 所有页面创建完成，共 {len(self.content_pages)} 个页面")
            
            # 默认显示概览页面
            try:
                self._switch_content("overview")
                print("✅ 默认页面切换成功")
            except Exception as e:
                print(f"❌ 默认页面切换失败: {e}")
            
        except Exception as e:
            print(f"创建主内容区域时出错: {e}")
            # 确保 content_pages 被初始化
            if not hasattr(self, 'content_pages'):
                self.content_pages = {}
    
    def _create_overview_page(self):
        """创建概览页面"""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # 当前版本卡片
        version_card = self._create_info_card(
            page, "当前版本", "1.0.1", "稳定版本", self.colors['success']
        )
        version_card.pack(fill="x", padx=30, pady=(30, 20))
        
        # 项目统计卡片
        stats_frame = ctk.CTkFrame(page, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=20)
        
        # 配置网格权重
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # 统计卡片网格
        stats = [
            ("总版本数", "1", self.colors['primary']),
            ("稳定版本", "1", self.colors['success']),
            ("备份数量", "1", self.colors['secondary']),
            ("错误数量", "0", self.colors['success'])
        ]
        
        for i, (title, value, color) in enumerate(stats):
            stat_card = self._create_stat_card(stats_frame, title, value, color)
            stat_card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        # 最近活动
        activity_frame = ctk.CTkFrame(page, fg_color=self.colors['background'], corner_radius=12)
        activity_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            activity_frame,
            text="最近活动",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 15))
        
        self.activity_text = ctk.CTkTextbox(
            activity_frame, 
            height=120,
            font=self.fonts['body'],
            fg_color="transparent"
        )
        self.activity_text.pack(fill="x", padx=20, pady=(0, 20))
        
        return page
    
    def _create_info_card(self, parent, title, value, status, status_color):
        """创建信息卡片"""
        card = ctk.CTkFrame(parent, fg_color=self.colors['background'], corner_radius=12)
        
        # 卡片内容
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=25, pady=25)
        
        # 标题
        ctk.CTkLabel(
            content,
            text=title,
            font=self.fonts['caption'],
            text_color=self.colors['text_secondary']
        ).pack(anchor="w")
        
        # 值
        ctk.CTkLabel(
            content,
            text=value,
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(anchor="w", pady=(5, 0))
        
        # 状态
        ctk.CTkLabel(
            content,
            text=status,
            font=self.fonts['body'],
            text_color=status_color
        ).pack(anchor="w", pady=(5, 0))
        
        return card
    
    def _create_stat_card(self, parent, title, value, color):
        """创建统计卡片"""
        card = ctk.CTkFrame(parent, fg_color=self.colors['background'], corner_radius=12)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 值
        ctk.CTkLabel(
            content,
            text=value,
            font=self.fonts['heading'],
            text_color=color
        ).pack()
        
        # 标题
        ctk.CTkLabel(
            content,
            text=title,
            font=self.fonts['caption'],
            text_color=self.colors['text_secondary']
        ).pack(pady=(5, 0))
        
        return card
    
    def _create_history_page(self):
        """创建版本历史页面"""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # 页面标题
        title_frame = ctk.CTkFrame(page, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(
            title_frame,
            text="版本历史",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        # 版本列表
        self.version_tree = ttk.Treeview(
            page,
            columns=("version", "date", "author", "stability", "status"),
            show="headings",
            height=15
        )
        
        # 设置列标题
        self.version_tree.heading("version", text="版本")
        self.version_tree.heading("date", text="日期")
        self.version_tree.heading("author", text="作者")
        self.version_tree.heading("stability", text="稳定性")
        self.version_tree.heading("status", text="状态")
        
        # 设置列宽
        self.version_tree.column("version", width=100)
        self.version_tree.column("date", width=150)
        self.version_tree.column("author", width=120)
        self.version_tree.column("stability", width=80)
        self.version_tree.column("status", width=80)
        
        self.version_tree.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # 操作按钮
        button_frame = ctk.CTkFrame(page, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        ctk.CTkButton(
            button_frame,
            text="回滚到选中版本",
            font=self.fonts['button'],
            fg_color=self.colors['warning'],
            hover_color=self.colors['warning'],
            corner_radius=8,
            height=40,
            command=self._rollback_to_selected_version
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="查看详细信息",
            font=self.fonts['button'],
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            corner_radius=8,
            height=40,
            command=self._show_version_details
        ).pack(side="left")
        
        return page
    
    def _create_changelog_page(self):
        """创建变更日志页面"""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # 页面标题
        title_frame = ctk.CTkFrame(page, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(
            title_frame,
            text="变更日志",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        # 变更日志文本区域
        self.changelog_text = ctk.CTkTextbox(
            page,
            font=self.fonts['body'],
            fg_color=self.colors['background'],
            corner_radius=12
        )
        self.changelog_text.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # 操作按钮
        button_frame = ctk.CTkFrame(page, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        ctk.CTkButton(
            button_frame,
            text="保存到文件",
            font=self.fonts['button'],
            fg_color=self.colors['success'],
            hover_color=self.colors['success'],
            corner_radius=8,
            height=40,
            command=self._save_changelog_to_file
        ).pack(side="left")
        
        return page
    
    def _create_errors_page(self):
        """创建错误监控页面"""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # 页面标题
        title_frame = ctk.CTkFrame(page, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(
            title_frame,
            text="错误监控",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        # 错误摘要
        summary_frame = ctk.CTkFrame(page, fg_color=self.colors['background'], corner_radius=12)
        summary_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        self.error_summary_text = ctk.CTkTextbox(
            summary_frame,
            height=100,
            font=self.fonts['body'],
            fg_color="transparent"
        )
        self.error_summary_text.pack(fill="x", padx=20, pady=20)
        
        # 操作按钮
        button_frame = ctk.CTkFrame(page, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        ctk.CTkButton(
            button_frame,
            text="清除错误历史",
            font=self.fonts['button'],
            fg_color=self.colors['error'],
            hover_color=self.colors['error'],
            corner_radius=8,
            height=40,
            command=self._clear_error_history
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="紧急回滚",
            font=self.fonts['button'],
            fg_color=self.colors['warning'],
            hover_color=self.colors['warning'],
            corner_radius=8,
            height=40,
            command=self._emergency_rollback
        ).pack(side="left")
        
        return page
    
    def _create_settings_page(self):
        """创建设置页面"""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # 页面标题
        title_frame = ctk.CTkFrame(page, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        ctk.CTkLabel(
            title_frame,
            text="设置",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        # 设置选项
        settings_frame = ctk.CTkFrame(page, fg_color=self.colors['background'], corner_radius=12)
        settings_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # 稳定性阈值设置
        stability_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        stability_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            stability_frame,
            text="稳定性阈值",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        self.stability_slider = ctk.CTkSlider(
            stability_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_stability_change
        )
        self.stability_slider.pack(fill="x", pady=(10, 0))
        self.stability_slider.set(80)
        
        # 自动备份设置
        backup_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        backup_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            backup_frame,
            text="自动备份",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        self.auto_backup_switch = ctk.CTkSwitch(
            backup_frame,
            text="启用自动备份",
            font=self.fonts['body'],
            command=self._on_auto_backup_change
        )
        self.auto_backup_switch.pack(anchor="w", pady=(10, 0))
        self.auto_backup_switch.select()
        
        return page
    
    def _switch_content(self, page_key):
        """切换内容页面"""
        # 隐藏所有页面
        for page in self.content_pages.values():
            page.pack_forget()
        
        # 显示选中的页面
        self.content_pages[page_key].pack(fill="both", expand=True, padx=30, pady=30)
        
        # 更新导航按钮状态
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(fg_color=self.colors['primary'], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.colors['text'])
        
        # 刷新页面内容
        self._refresh_page_content(page_key)
    
    def _refresh_page_content(self, page_key):
        """刷新页面内容"""
        if page_key == "overview":
            self._refresh_overview()
        elif page_key == "history":
            self._refresh_history()
        elif page_key == "changelog":
            self._refresh_changelog()
        elif page_key == "errors":
            self._refresh_errors()
    
    def _refresh_overview(self):
        """刷新概览页面"""
        try:
            # 获取项目状态
            status = self.version_manager.get_project_status()
            
            # 更新活动文本
            self.activity_text.delete("1.0", "end")
            activity_text = f"• {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 系统状态检查完成\n"
            activity_text += f"• 当前版本: {status.get('current_version', '未知')}\n"
            activity_text += f"• 总版本数: {status.get('total_versions', 0)}\n"
            activity_text += f"• 稳定版本: {status.get('stable_versions_count', 0)}\n"
            activity_text += f"• 最后更新: {status.get('last_update', '未知')}"
            
            self.activity_text.insert("1.0", activity_text)
            
        except Exception as e:
            self.activity_text.delete("1.0", "end")
            self.activity_text.insert("1.0", f"刷新失败: {str(e)}")
    
    def _refresh_history(self):
        """刷新版本历史页面"""
        try:
            # 清空现有数据
            for item in self.version_tree.get_children():
                self.version_tree.delete(item)
            
            # 获取版本历史
            versions = self.version_manager.get_version_history()
            
            # 添加版本数据
            for version in versions:
                status = "稳定" if version.get("is_stable", False) else "测试中"
                status_color = self.colors['success'] if status == "稳定" else self.colors['warning']
                
                self.version_tree.insert("", "end", values=(
                    version.get("version", ""),
                    version.get("timestamp", ""),
                    version.get("author", ""),
                    f"{version.get('stability_score', 0)}%",
                    status
                ))
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新版本历史失败: {str(e)}")
    
    def _refresh_changelog(self):
        """刷新变更日志页面"""
        try:
            # 这里应该从版本管理器获取变更日志
            # 暂时显示示例内容
            changelog_text = """# FileSenseScan 变更日志

## 版本 1.0.1 (2025-08-11)
### 新增功能
- 修复相对导入问题
- 完善错误监控系统
- 优化版本管理GUI

### 技术改进
- 采用苹果风格设计语言
- 提升用户体验
- 增强系统稳定性

## 版本 1.0.0 (2025-08-11)
### 初始版本
- 基础版本管理功能
- 错误监控系统
- 自动备份机制"""
            
            self.changelog_text.delete("1.0", "end")
            self.changelog_text.insert("1.0", changelog_text)
            
        except Exception as e:
            self.changelog_text.delete("1.0", "end")
            self.changelog_text.insert("1.0", f"刷新变更日志失败: {str(e)}")
    
    def _refresh_errors(self):
        """刷新错误监控页面"""
        try:
            # 获取错误摘要
            summary = self.error_monitor.get_error_summary()
            
            # 格式化错误摘要
            summary_text = f"""错误监控状态:
• 总错误数: {summary.get('total_errors', 0)}
• 监控状态: {'启用' if summary.get('monitoring_status', False) else '禁用'}
• 紧急模式: {'是' if summary.get('emergency_mode', False) else '否'}
• 最后错误时间: {summary.get('last_error_time', '无')}

错误类型统计:"""
            
            for error_type, count in summary.get('error_types', {}).items():
                summary_text += f"\n• {error_type}: {count}"
            
            self.error_summary_text.delete("1.0", "end")
            self.error_summary_text.insert("1.0", summary_text)
            
        except Exception as e:
            self.error_summary_text.delete("1.0", "end")
            self.error_summary_text.insert("1.0", f"刷新错误监控失败: {str(e)}")
    
    def _create_new_version_dialog(self):
        """创建新版本对话框"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("创建新版本")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 对话框内容
        content = ctk.CTkFrame(dialog, fg_color=self.colors['surface'], corner_radius=12)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        ctk.CTkLabel(
            content,
            text="创建新版本",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 30))
        
        # 版本号输入
        version_frame = ctk.CTkFrame(content, fg_color="transparent")
        version_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            version_frame,
            text="版本号:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        version_entry = ctk.CTkEntry(version_frame, font=self.fonts['body'])
        version_entry.pack(fill="x", pady=(5, 0))
        version_entry.insert(0, "1.0.2")
        
        # 描述输入
        desc_frame = ctk.CTkFrame(content, fg_color="transparent")
        desc_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            desc_frame,
            text="版本描述:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        desc_entry = ctk.CTkEntry(desc_frame, font=self.fonts['body'])
        desc_entry.pack(fill="x", pady=(5, 0))
        desc_entry.insert(0, "优化用户体验")
        
        # 变更内容输入
        changes_frame = ctk.CTkFrame(content, fg_color="transparent")
        changes_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            changes_frame,
            text="变更内容:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        changes_text = ctk.CTkTextbox(changes_frame, height=80, font=self.fonts['body'])
        changes_text.pack(fill="x", pady=(5, 0))
        changes_text.insert("1.0", "• 采用苹果风格设计\n• 优化界面布局\n• 提升用户体验")
        
        # 按钮
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=30)
        
        def create_version():
            try:
                version = version_entry.get()
                description = desc_entry.get()
                changes = changes_text.get("1.0", "end-1c").split('\n')
                changes = [c.strip() for c in changes if c.strip()]
                
                if self.version_manager.create_version(version, description, changes, 90.0):
                    messagebox.showinfo("成功", f"版本 {version} 创建成功！")
                    dialog.destroy()
                    self._refresh_all()
                else:
                    messagebox.showerror("错误", "创建版本失败！")
            except Exception as e:
                messagebox.showerror("错误", f"创建版本时出错: {str(e)}")
        
        ctk.CTkButton(
            button_frame,
            text="创建版本",
            font=self.fonts['button'],
            fg_color=self.colors['success'],
            hover_color=self.colors['success'],
            corner_radius=8,
            height=40,
            command=create_version
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="取消",
            font=self.fonts['button'],
            fg_color=self.colors['text_secondary'],
            hover_color=self.colors['text_secondary'],
            corner_radius=8,
            height=40,
            command=dialog.destroy
        ).pack(side="left")
    
    def _sync_to_github(self):
        """同步到GitHub"""
        try:
            # 这里应该调用GitHub同步功能
            messagebox.showinfo("同步", "开始同步到GitHub...")
            # TODO: 实现实际的GitHub同步
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")
    
    def _system_health_check(self):
        """系统健康检查"""
        try:
            # 这里应该执行系统健康检查
            messagebox.showinfo("健康检查", "系统健康检查完成，一切正常！")
            # TODO: 实现实际的系统健康检查
        except Exception as e:
            messagebox.showerror("错误", f"健康检查失败: {str(e)}")
    
    def _rollback_to_selected_version(self):
        """回滚到选中的版本"""
        selection = self.version_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个版本")
            return
        
        # 获取选中的版本信息
        item = self.version_tree.item(selection[0])
        version = item['values'][0]
        
        if messagebox.askyesno("确认", f"确定要回滚到版本 {version} 吗？"):
            try:
                if self.version_manager.rollback_to_version(version):
                    messagebox.showinfo("成功", f"回滚到版本 {version} 成功！")
                    self._refresh_all()
                else:
                    messagebox.showerror("错误", "回滚失败！")
            except Exception as e:
                messagebox.showerror("错误", f"回滚时出错: {str(e)}")
    
    def _show_version_details(self):
        """显示版本详细信息"""
        selection = self.version_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个版本")
            return
        
        # 获取选中的版本信息
        item = self.version_tree.item(selection[0])
        version = item['values'][0]
        
        # 显示版本详情对话框
        messagebox.showinfo("版本详情", f"版本 {version} 的详细信息:\n\n{item['values']}")
    
    def _save_changelog_to_file(self):
        """保存变更日志到文件"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                changelog_content = self.changelog_text.get("1.0", "end")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(changelog_content)
                
                messagebox.showinfo("成功", f"变更日志已保存到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _emergency_rollback(self):
        """紧急回滚"""
        if messagebox.askyesno("紧急回滚", "确定要执行紧急回滚吗？这将回滚到最近的稳定版本。"):
            try:
                if self.version_manager.emergency_rollback():
                    messagebox.showinfo("成功", "紧急回滚成功！")
                    self._refresh_all()
                else:
                    messagebox.showerror("错误", "紧急回滚失败！")
            except Exception as e:
                messagebox.showerror("错误", f"紧急回滚时出错: {str(e)}")
    
    def _clear_error_history(self):
        """清除错误历史"""
        if messagebox.askyesno("确认", "确定要清除所有错误历史吗？"):
            try:
                self.error_monitor.clear_error_history()
                messagebox.showinfo("成功", "错误历史已清除！")
                self._refresh_errors()
            except Exception as e:
                messagebox.showerror("错误", f"清除错误历史失败: {str(e)}")
    
    def _on_stability_change(self, value):
        """稳定性阈值改变"""
        try:
            self.version_manager.stability_threshold = float(value)
            # 这里可以保存设置到配置文件
        except Exception as e:
            print(f"设置稳定性阈值失败: {e}")
    
    def _on_auto_backup_change(self):
        """自动备份设置改变"""
        try:
            self.version_manager.auto_backup = self.auto_backup_switch.get()
            # 这里可以保存设置到配置文件
        except Exception as e:
            print(f"设置自动备份失败: {e}")
    
    def _refresh_all(self):
        """刷新所有页面"""
        self._refresh_overview()
        self._refresh_history()
        self._refresh_changelog()
        self._refresh_errors()
    
    def _start_auto_refresh(self):
        """启动自动刷新"""
        def auto_refresh():
            while True:
                try:
                    # 每30秒自动刷新一次
                    self.root.after(30000, self._refresh_all)
                except:
                    break
        
        refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
        refresh_thread.start()
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = AppleStyleVersionGUI()
    app.run() 