"""
FileSenseScan 版本管理GUI界面
提供版本管理、变更日志查看、回滚操作等功能的图形界面
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
from app.core.version_manager import get_version_manager, VersionManager
from app.core.error_monitor import get_error_monitor, ErrorMonitor


class VersionManagementGUI:
    """版本管理GUI主类"""
    
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
            self.root.geometry("1000x700")
            self.root.resizable(True, True)
        else:
            self.root = parent
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 构建界面
        self._build_ui()
        
        # 启动自动刷新
        self._start_auto_refresh()
    
    def _build_ui(self):
        """构建用户界面"""
        # 主标题
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🔧 FileSenseScan 版本管理系统", 
            font=("Microsoft Yahei", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 版本概览选项卡
        self._create_overview_tab()
        
        # 版本历史选项卡
        self._create_history_tab()
        
        # 变更日志选项卡
        self._create_changelog_tab()
        
        # 错误监控选项卡
        self._create_error_monitor_tab()
        
        # 设置选项卡
        self._create_settings_tab()
        
        # 底部状态栏
        self._create_status_bar()
    
    def _create_overview_tab(self):
        """创建版本概览选项卡"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="📊 版本概览")
        
        # 当前版本信息
        current_version_frame = ctk.CTkFrame(overview_frame)
        current_version_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            current_version_frame, 
            text="当前版本信息", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        # 版本信息网格
        info_grid = ctk.CTkFrame(current_version_frame)
        info_grid.pack(fill="x", padx=10, pady=(0, 10))
        
        self.current_version_label = ctk.CTkLabel(info_grid, text="版本: 加载中...")
        self.current_version_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.commit_hash_label = ctk.CTkLabel(info_grid, text="提交: 加载中...")
        self.commit_hash_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.author_label = ctk.CTkLabel(info_grid, text="作者: 加载中...")
        self.author_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.stability_label = ctk.CTkLabel(info_grid, text="稳定性: 加载中...")
        self.stability_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # 项目状态
        status_frame = ctk.CTkFrame(overview_frame)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            status_frame, 
            text="项目状态", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        self.status_text = ctk.CTkTextbox(status_frame, height=150)
        self.status_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # 操作按钮
        button_frame = ctk.CTkFrame(overview_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="🔄 刷新状态", 
            command=self._refresh_overview
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="📋 创建新版本", 
            command=self._create_new_version_dialog
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="🔄 回滚到稳定版本", 
            command=self._rollback_to_stable
        ).pack(side="left", padx=5)
    
    def _create_history_tab(self):
        """创建版本历史选项卡"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="📚 版本历史")
        
        # 版本列表
        list_frame = ctk.CTkFrame(history_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            list_frame, 
            text="版本历史记录", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        # 创建Treeview
        columns = ("版本", "提交", "作者", "时间", "稳定性", "状态")
        self.version_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.version_tree.heading(col, text=col)
            self.version_tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.version_tree.yview)
        self.version_tree.configure(yscrollcommand=scrollbar.set)
        
        self.version_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10))
        
        # 绑定双击事件
        self.version_tree.bind("<Double-1>", self._on_version_double_click)
        
        # 操作按钮
        button_frame = ctk.CTkFrame(history_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="🔄 刷新历史", 
            command=self._refresh_history
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="📥 回滚到此版本", 
            command=self._rollback_to_selected_version
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="📋 查看详情", 
            command=self._show_version_details
        ).pack(side="left", padx=5)
    
    def _create_changelog_tab(self):
        """创建变更日志选项卡"""
        changelog_frame = ttk.Frame(self.notebook)
        self.notebook.add(changelog_frame, text="📝 变更日志")
        
        # 变更日志内容
        content_frame = ctk.CTkFrame(changelog_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            content_frame, 
            text="变更日志", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        self.changelog_text = ctk.CTkTextbox(content_frame)
        self.changelog_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 操作按钮
        button_frame = ctk.CTkFrame(changelog_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="🔄 刷新日志", 
            command=self._refresh_changelog
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="💾 保存到文件", 
            command=self._save_changelog_to_file
        ).pack(side="left", padx=5)
    
    def _create_error_monitor_tab(self):
        """创建错误监控选项卡"""
        error_frame = ttk.Frame(self.notebook)
        self.notebook.add(error_frame, text="⚠️ 错误监控")
        
        # 错误摘要
        summary_frame = ctk.CTkFrame(error_frame)
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            summary_frame, 
            text="错误监控状态", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        self.error_summary_text = ctk.CTkTextbox(summary_frame, height=120)
        self.error_summary_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # 错误历史
        history_frame = ctk.CTkFrame(error_frame)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            history_frame, 
            text="错误历史记录", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        # 创建错误列表
        error_columns = ("时间", "类型", "消息", "严重性")
        self.error_tree = ttk.Treeview(history_frame, columns=error_columns, show="headings", height=12)
        
        for col in error_columns:
            self.error_tree.heading(col, text=col)
            self.error_tree.column(col, width=150)
        
        error_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.error_tree.yview)
        self.error_tree.configure(yscrollcommand=error_scrollbar.set)
        
        self.error_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        error_scrollbar.pack(side="right", fill="y", pady=(0, 10))
        
        # 操作按钮
        button_frame = ctk.CTkFrame(error_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="🔄 刷新状态", 
            command=self._refresh_error_monitor
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="🚨 紧急回滚", 
            command=self._emergency_rollback
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="🧹 清除历史", 
            command=self._clear_error_history
        ).pack(side="left", padx=5)
    
    def _create_settings_tab(self):
        """创建设置选项卡"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ 设置")
        
        # 版本管理设置
        vm_settings_frame = ctk.CTkFrame(settings_frame)
        vm_settings_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            vm_settings_frame, 
            text="版本管理设置", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        # 稳定性阈值
        threshold_frame = ctk.CTkFrame(vm_settings_frame)
        threshold_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(threshold_frame, text="稳定性阈值:").pack(side="left", padx=5)
        self.threshold_var = ctk.StringVar(value="80.0")
        threshold_entry = ctk.CTkEntry(threshold_frame, textvariable=self.threshold_var, width=100)
        threshold_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            threshold_frame, 
            text="设置", 
            command=self._set_stability_threshold
        ).pack(side="left", padx=5)
        
        # 自动备份设置
        backup_frame = ctk.CTkFrame(vm_settings_frame)
        backup_frame.pack(fill="x", padx=10, pady=5)
        
        self.auto_backup_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            backup_frame, 
            text="启用自动备份", 
            variable=self.auto_backup_var,
            command=self._set_auto_backup
        ).pack(side="left", padx=5)
        
        # 错误监控设置
        em_settings_frame = ctk.CTkFrame(settings_frame)
        em_settings_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            em_settings_frame, 
            text="错误监控设置", 
            font=("Microsoft Yahei", 14, "bold")
        ).pack(pady=(10, 5))
        
        # 错误阈值
        error_threshold_frame = ctk.CTkFrame(em_settings_frame)
        error_threshold_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(error_threshold_frame, text="错误阈值:").pack(side="left", padx=5)
        self.error_threshold_var = ctk.StringVar(value="3")
        error_threshold_entry = ctk.CTkEntry(error_threshold_frame, textvariable=self.error_threshold_var, width=100)
        error_threshold_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            error_threshold_frame, 
            text="设置", 
            command=self._set_error_threshold
        ).pack(side="left", padx=5)
        
        # 自动回滚设置
        rollback_frame = ctk.CTkFrame(em_settings_frame)
        rollback_frame.pack(fill="x", padx=10, pady=5)
        
        self.auto_rollback_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            rollback_frame, 
            text="启用自动回滚", 
            variable=self.auto_rollback_var,
            command=self._set_auto_rollback
        ).pack(side="left", padx=5)
    
    def _create_status_bar(self):
        """创建底部状态栏"""
        status_frame = ctk.CTkFrame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(status_frame, text="就绪")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # 自动刷新开关
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            status_frame, 
            text="自动刷新", 
            variable=self.auto_refresh_var
        ).pack(side="right", padx=10, pady=5)
    
    def _start_auto_refresh(self):
        """启动自动刷新"""
        def auto_refresh():
            while True:
                if self.auto_refresh_var.get():
                    try:
                        self._refresh_all()
                    except Exception as e:
                        print(f"自动刷新错误: {e}")
                threading.Event().wait(30)  # 每30秒刷新一次
        
        refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
        refresh_thread.start()
    
    def _refresh_all(self):
        """刷新所有数据"""
        self._refresh_overview()
        self._refresh_history()
        self._refresh_changelog()
        self._refresh_error_monitor()
    
    def _refresh_overview(self):
        """刷新版本概览"""
        try:
            # 获取当前版本信息
            current_info = self.version_manager.get_current_version_info()
            if current_info:
                self.current_version_label.configure(text=f"版本: {current_info['version']}")
                self.commit_hash_label.configure(text=f"提交: {current_info['commit_hash']}")
                self.author_label.configure(text=f"作者: {current_info['author']}")
                
                stability_score = current_info.get('stability_score', 0)
                stability_color = "green" if stability_score >= 80 else "orange" if stability_score >= 60 else "red"
                self.stability_label.configure(
                    text=f"稳定性: {stability_score}/100",
                    text_color=stability_color
                )
            
            # 获取项目状态
            status = self.version_manager.get_project_status()
            status_text = json.dumps(status, indent=2, ensure_ascii=False)
            self.status_text.delete("1.0", "end")
            self.status_text.insert("1.0", status_text)
            
            self.status_label.configure(text=f"最后更新: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新概览失败: {e}")
    
    def _refresh_history(self):
        """刷新版本历史"""
        try:
            # 清空现有数据
            for item in self.version_tree.get_children():
                self.version_tree.delete(item)
            
            # 获取版本历史
            versions = self.version_manager.get_version_history()
            
            for version in versions:
                # 格式化时间
                timestamp = version.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        time_str = timestamp
                else:
                    time_str = '未知'
                
                # 稳定性状态
                stability = version.get('stability_score', 0)
                status = "稳定" if version.get('is_stable', False) else "测试中"
                
                self.version_tree.insert("", "end", values=(
                    version.get('version', ''),
                    version.get('commit_hash', ''),
                    version.get('author', ''),
                    time_str,
                    f"{stability}/100",
                    status
                ))
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新历史失败: {e}")
    
    def _refresh_changelog(self):
        """刷新变更日志"""
        try:
            changelog_file = self.version_manager.changelog_file
            if changelog_file.exists():
                with open(changelog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.changelog_text.delete("1.0", "end")
                self.changelog_text.insert("1.0", content)
            else:
                self.changelog_text.delete("1.0", "end")
                self.changelog_text.insert("1.0", "暂无变更日志")
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新变更日志失败: {e}")
    
    def _refresh_error_monitor(self):
        """刷新错误监控"""
        try:
            # 获取错误摘要
            summary = self.error_monitor.get_error_summary()
            summary_text = json.dumps(summary, indent=2, ensure_ascii=False)
            self.error_summary_text.delete("1.0", "end")
            self.error_summary_text.insert("1.0", summary_text)
            
            # 清空错误历史
            for item in self.error_tree.get_children():
                self.error_tree.delete(item)
            
            # 获取错误历史
            errors = self.error_monitor.error_history[-20:]  # 最近20条
            
            for error in errors:
                # 格式化时间
                timestamp = error.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = timestamp
                else:
                    time_str = '未知'
                
                self.error_tree.insert("", "end", values=(
                    time_str,
                    error.get('type', ''),
                    error.get('message', '')[:50] + '...' if len(error.get('message', '')) > 50 else error.get('message', ''),
                    error.get('severity', '')
                ))
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新错误监控失败: {e}")
    
    def _create_new_version_dialog(self):
        """创建新版本对话框"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("创建新版本")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 版本号
        version_frame = ctk.CTkFrame(dialog)
        version_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(version_frame, text="版本号:").pack(anchor="w", padx=10, pady=5)
        version_var = ctk.StringVar(value="1.0.1")
        version_entry = ctk.CTkEntry(version_frame, textvariable=version_var)
        version_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 描述
        desc_frame = ctk.CTkFrame(dialog)
        desc_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(desc_frame, text="版本描述:").pack(anchor="w", padx=10, pady=5)
        desc_text = ctk.CTkTextbox(desc_frame, height=80)
        desc_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # 变更内容
        changes_frame = ctk.CTkFrame(dialog)
        changes_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(changes_frame, text="变更内容:").pack(anchor="w", padx=10, pady=5)
        changes_text = ctk.CTkTextbox(changes_frame, height=100)
        changes_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # 稳定性评分
        stability_frame = ctk.CTkFrame(dialog)
        stability_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(stability_frame, text="稳定性评分 (0-100):").pack(anchor="w", padx=10, pady=5)
        stability_var = ctk.StringVar(value="90.0")
        stability_entry = ctk.CTkEntry(stability_frame, textvariable=stability_var)
        stability_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 按钮
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def create_version():
            try:
                version = version_var.get().strip()
                description = desc_text.get("1.0", "end").strip()
                changes_text_content = changes_text.get("1.0", "end").strip()
                stability = float(stability_var.get())
                
                if not version or not description:
                    messagebox.showerror("错误", "请填写版本号和描述")
                    return
                
                changes = [line.strip() for line in changes_text_content.split('\n') if line.strip()]
                
                if self.version_manager.create_version(version, description, changes, stability):
                    messagebox.showinfo("成功", f"版本 {version} 创建成功")
                    dialog.destroy()
                    self._refresh_all()
                else:
                    messagebox.showerror("错误", "创建版本失败")
                    
            except Exception as e:
                messagebox.showerror("错误", f"创建版本失败: {e}")
        
        ctk.CTkButton(
            button_frame, 
            text="创建版本", 
            command=create_version
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="取消", 
            command=dialog.destroy
        ).pack(side="right", padx=5)
    
    def _rollback_to_stable(self):
        """回滚到稳定版本"""
        try:
            if messagebox.askyesno("确认", "确定要回滚到最近的稳定版本吗？这将覆盖当前版本。"):
                if self.version_manager.rollback_to_stable():
                    messagebox.showinfo("成功", "回滚到稳定版本成功")
                    self._refresh_all()
                else:
                    messagebox.showerror("错误", "回滚失败")
        except Exception as e:
            messagebox.showerror("错误", f"回滚失败: {e}")
    
    def _rollback_to_selected_version(self):
        """回滚到选中的版本"""
        try:
            selection = self.version_tree.selection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个版本")
                return
            
            item = self.version_tree.item(selection[0])
            version = item['values'][0]
            
            if messagebox.askyesno("确认", f"确定要回滚到版本 {version} 吗？这将覆盖当前版本。"):
                if self.version_manager.rollback_to_version(version):
                    messagebox.showinfo("成功", f"回滚到版本 {version} 成功")
                    self._refresh_all()
                else:
                    messagebox.showerror("错误", "回滚失败")
        except Exception as e:
            messagebox.showerror("错误", f"回滚失败: {e}")
    
    def _on_version_double_click(self, event):
        """版本双击事件"""
        self._show_version_details()
    
    def _show_version_details(self):
        """显示版本详情"""
        try:
            selection = self.version_tree.selection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个版本")
                return
            
            item = self.version_tree.item(selection[0])
            version = item['values'][0]
            
            # 查找版本信息
            versions = self.version_manager.get_version_history()
            version_info = None
            for v in versions:
                if v['version'] == version:
                    version_info = v
                    break
            
            if version_info:
                details = json.dumps(version_info, indent=2, ensure_ascii=False)
                
                detail_dialog = ctk.CTkToplevel(self.root)
                detail_dialog.title(f"版本 {version} 详情")
                detail_dialog.geometry("600x500")
                detail_dialog.resizable(True, True)
                detail_dialog.transient(self.root)
                
                detail_text = ctk.CTkTextbox(detail_dialog)
                detail_text.pack(fill="both", expand=True, padx=10, pady=10)
                detail_text.insert("1.0", details)
                
                ctk.CTkButton(
                    detail_dialog, 
                    text="关闭", 
                    command=detail_dialog.destroy
                ).pack(pady=10)
            else:
                messagebox.showerror("错误", f"未找到版本 {version} 的详细信息")
                
        except Exception as e:
            messagebox.showerror("错误", f"显示版本详情失败: {e}")
    
    def _save_changelog_to_file(self):
        """保存变更日志到文件"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All", "*.*")]
            )
            
            if file_path:
                content = self.changelog_text.get("1.0", "end")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"变更日志已保存到: {file_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def _emergency_rollback(self):
        """紧急回滚"""
        try:
            if messagebox.askyesno("确认", "确定要执行紧急回滚吗？这将尝试恢复到最近的稳定状态。"):
                if self.version_manager.emergency_rollback():
                    messagebox.showinfo("成功", "紧急回滚成功")
                    self._refresh_all()
                else:
                    messagebox.showerror("错误", "紧急回滚失败")
        except Exception as e:
            messagebox.showerror("错误", f"紧急回滚失败: {e}")
    
    def _clear_error_history(self):
        """清除错误历史"""
        try:
            if messagebox.askyesno("确认", "确定要清除错误历史吗？"):
                self.error_monitor.clear_error_history()
                messagebox.showinfo("成功", "错误历史已清除")
                self._refresh_error_monitor()
        except Exception as e:
            messagebox.showerror("错误", f"清除失败: {e}")
    
    def _set_stability_threshold(self):
        """设置稳定性阈值"""
        try:
            threshold = float(self.threshold_var.get())
            if 0 <= threshold <= 100:
                self.version_manager.stability_threshold = threshold
                messagebox.showinfo("成功", f"稳定性阈值已设置为: {threshold}")
            else:
                messagebox.showerror("错误", "稳定性阈值必须在0-100之间")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def _set_auto_backup(self):
        """设置自动备份"""
        try:
            enabled = self.auto_backup_var.get()
            self.version_manager.auto_backup = enabled
            messagebox.showinfo("成功", f"自动备份已{'启用' if enabled else '禁用'}")
        except Exception as e:
            messagebox.showerror("错误", f"设置失败: {e}")
    
    def _set_error_threshold(self):
        """设置错误阈值"""
        try:
            threshold = int(self.error_threshold_var.get())
            if threshold > 0:
                self.error_monitor.set_error_threshold(threshold)
                messagebox.showinfo("成功", f"错误阈值已设置为: {threshold}")
            else:
                messagebox.showerror("错误", "错误阈值必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数")
    
    def _set_auto_rollback(self):
        """设置自动回滚"""
        try:
            enabled = self.auto_rollback_var.get()
            self.error_monitor.set_auto_rollback(enabled)
            messagebox.showinfo("成功", f"自动回滚已{'启用' if enabled else '禁用'}")
        except Exception as e:
            messagebox.showerror("错误", f"设置失败: {e}")
    
    def run(self):
        """运行GUI"""
        if self.parent is None:
            self.root.mainloop()


if __name__ == "__main__":
    # 测试代码
    app = VersionManagementGUI()
    app.run() 