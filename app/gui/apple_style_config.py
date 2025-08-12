#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苹果风格设计配置文件
遵循苹果公司用户体验设计规范
"""

import platform
from typing import Dict, Any

class AppleStyleConfig:
    """苹果风格设计配置"""
    
    def __init__(self):
        self.system = platform.system()
        self._init_colors()
        self._init_fonts()
        self._init_spacing()
        self._init_animations()
    
    def _init_colors(self):
        """初始化苹果风格颜色方案"""
        # 主色调 - 苹果蓝
        self.colors = {
            'primary': '#007AFF',      # 苹果蓝 - 主要操作按钮
            'secondary': '#5856D6',    # 苹果紫 - 次要操作按钮
            'success': '#34C759',      # 苹果绿 - 成功状态
            'warning': '#FF9500',      # 苹果橙 - 警告状态
            'error': '#FF3B30',        # 苹果红 - 错误状态
            'info': '#5AC8FA',         # 苹果青 - 信息状态
            
            # 背景色系
            'background': '#F2F2F7',   # 主背景色
            'surface': '#FFFFFF',      # 卡片背景色
            'surface_secondary': '#F9F9F9',  # 次要表面色
            
            # 文本色系
            'text': '#000000',         # 主要文本
            'text_secondary': '#8E8E93',     # 次要文本
            'text_tertiary': '#C7C7CC',      # 第三级文本
            'text_quaternary': '#D1D1D6',    # 第四级文本
            
            # 边框色系
            'border': '#C6C6C8',       # 主要边框
            'border_secondary': '#E5E5EA',   # 次要边框
            
            # 特殊状态色
            'link': '#007AFF',         # 链接色
            'placeholder': '#C7C7CC',  # 占位符文本色
            'separator': '#C6C6C8',    # 分隔线色
            'opaque_separator': '#C6C6C8',  # 不透明分隔线色
        }
        
        # 深色模式颜色（如果系统支持）
        self.dark_colors = {
            'primary': '#0A84FF',      # 深色模式苹果蓝
            'secondary': '#5E5CE6',    # 深色模式苹果紫
            'success': '#30D158',      # 深色模式苹果绿
            'warning': '#FF9F0A',      # 深色模式苹果橙
            'error': '#FF453A',        # 深色模式苹果红
            'info': '#64D2FF',         # 深色模式苹果青
            
            'background': '#000000',   # 深色主背景
            'surface': '#1C1C1E',      # 深色卡片背景
            'surface_secondary': '#2C2C2E',  # 深色次要表面
            
            'text': '#FFFFFF',         # 深色主要文本
            'text_secondary': '#8E8E93',     # 深色次要文本
            'text_tertiary': '#48484A',      # 深色第三级文本
            'text_quaternary': '#3A3A3C',    # 深色第四级文本
            
            'border': '#38383A',       # 深色主要边框
            'border_secondary': '#48484A',   # 深色次要边框
            
            'link': '#0A84FF',         # 深色链接色
            'placeholder': '#48484A',  # 深色占位符文本色
            'separator': '#38383A',    # 深色分隔线色
            'opaque_separator': '#38383A',   # 深色不透明分隔线色
        }
    
    def _init_fonts(self):
        """初始化苹果风格字体"""
        if self.system == "Darwin":  # macOS
            self.fonts = {
                'title': ('SF Pro Display', 24, 'bold'),
                'heading': ('SF Pro Text', 18, 'bold'),
                'subheading': ('SF Pro Text', 16, 'normal'),
                'body': ('SF Pro Text', 14, 'normal'),
                'caption': ('SF Pro Text', 12, 'normal'),
                'button': ('SF Pro Text', 15, 'normal'),
                'code': ('SF Mono', 13, 'normal'),
                'large_title': ('SF Pro Display', 34, 'bold'),
                'headline': ('SF Pro Text', 17, 'bold'),
                'callout': ('SF Pro Text', 16, 'normal'),
                'footnote': ('SF Pro Text', 13, 'normal')
            }
        elif self.system == "Windows":
            self.fonts = {
                'title': ('Segoe UI', 24, 'bold'),
                'heading': ('Segoe UI', 18, 'bold'),
                'subheading': ('Segoe UI', 16, 'bold'),
                'body': ('Segoe UI', 14, 'normal'),
                'caption': ('Segoe UI', 12, 'normal'),
                'button': ('Segoe UI', 15, 'bold'),
                'code': ('Consolas', 13, 'normal'),
                'large_title': ('Segoe UI', 34, 'bold'),
                'headline': ('Segoe UI', 17, 'bold'),
                'callout': ('Segoe UI', 16, 'normal'),
                'footnote': ('Segoe UI', 13, 'normal')
            }
        else:  # Linux 或其他系统
            self.fonts = {
                'title': ('DejaVu Sans', 24, 'bold'),
                'heading': ('DejaVu Sans', 18, 'bold'),
                'subheading': ('DejaVu Sans', 16, 'bold'),
                'body': ('DejaVu Sans', 14, 'normal'),
                'caption': ('DejaVu Sans', 12, 'normal'),
                'button': ('DejaVu Sans', 15, 'bold'),
                'code': ('DejaVu Sans Mono', 13, 'normal'),
                'large_title': ('DejaVu Sans', 34, 'bold'),
                'headline': ('DejaVu Sans', 17, 'bold'),
                'callout': ('DejaVu Sans', 16, 'normal'),
                'footnote': ('DejaVu Sans', 13, 'normal')
            }
    
    def _init_spacing(self):
        """初始化苹果风格间距规范"""
        # 苹果设计系统中的标准间距
        self.spacing = {
            'xs': 4,      # 超小间距
            'sm': 8,      # 小间距
            'md': 16,     # 中等间距
            'lg': 24,     # 大间距
            'xl': 32,     # 超大间距
            'xxl': 48,    # 超超大间距
            'xxxl': 64,   # 超超超大间距
        }
        
        # 组件间距
        self.component_spacing = {
            'button_padding': (16, 12),      # 按钮内边距 (水平, 垂直)
            'card_padding': (20, 16),        # 卡片内边距
            'section_padding': (30, 24),     # 区块内边距
            'input_padding': (12, 8),        # 输入框内边距
            'list_item_padding': (16, 12),   # 列表项内边距
        }
    
    def _init_animations(self):
        """初始化苹果风格动画配置"""
        # 动画时长（毫秒）
        self.animation_duration = {
            'fast': 200,      # 快速动画
            'normal': 300,    # 正常动画
            'slow': 500,      # 慢速动画
            'very_slow': 800, # 很慢的动画
        }
        
        # 缓动函数
        self.easing = {
            'ease_in': 'ease-in',
            'ease_out': 'ease-out',
            'ease_in_out': 'ease-in-out',
            'spring': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',  # 弹簧效果
        }
    
    def get_color(self, color_name: str, dark_mode: bool = False) -> str:
        """获取颜色值"""
        if dark_mode and color_name in self.dark_colors:
            return self.dark_colors[color_name]
        return self.colors.get(color_name, self.colors['primary'])
    
    def get_font(self, font_name: str) -> tuple:
        """获取字体配置"""
        return self.fonts.get(font_name, self.fonts['body'])
    
    def get_spacing(self, spacing_name: str) -> int:
        """获取间距值"""
        return self.spacing.get(spacing_name, self.spacing['md'])
    
    def get_component_spacing(self, component_name: str) -> tuple:
        """获取组件间距"""
        return self.component_spacing.get(component_name, (16, 12))
    
    def get_animation_duration(self, duration_name: str) -> int:
        """获取动画时长"""
        return self.animation_duration.get(duration_name, self.animation_duration['normal'])
    
    def get_easing(self, easing_name: str) -> str:
        """获取缓动函数"""
        return self.easing.get(easing_name, self.easing['ease_in_out'])
    
    def is_dark_mode_supported(self) -> bool:
        """检查是否支持深色模式"""
        return self.system in ["Darwin", "Windows"]
    
    def get_system_appearance(self) -> str:
        """获取系统外观模式"""
        if self.system == "Darwin":
            try:
                import subprocess
                result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                     capture_output=True, text=True)
                return "dark" if result.stdout.strip() == "Dark" else "light"
            except:
                return "light"
        elif self.system == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "dark" if value == 0 else "light"
            except:
                return "light"
        return "light"


# 全局配置实例
apple_style_config = AppleStyleConfig()


def get_apple_style_config() -> AppleStyleConfig:
    """获取苹果风格配置实例"""
    return apple_style_config


# 苹果设计原则常量
class AppleDesignPrinciples:
    """苹果设计原则"""
    
    # 简洁性
    CLARITY = "clarity"
    # 一致性
    DEFERENCE = "deference"
    # 深度
    DEPTH = "depth"
    
    # 设计原则描述
    PRINCIPLES = {
        CLARITY: "界面应该清晰易懂，减少视觉噪音",
        DEFERENCE: "内容优先，界面元素应该支持内容而不是与之竞争",
        DEPTH: "使用视觉层次和动效来传达层次结构"
    }
    
    # 交互设计原则
    INTERACTION_PRINCIPLES = [
        "直接操作 - 用户应该能够直接操作屏幕上的对象",
        "即时反馈 - 每个用户操作都应该有即时的视觉反馈",
        "可预测性 - 界面行为应该符合用户期望",
        "容错性 - 界面应该优雅地处理错误和异常情况"
    ]
    
    # 视觉设计原则
    VISUAL_PRINCIPLES = [
        "层次结构 - 使用大小、颜色和位置来传达信息的重要性",
        "一致性 - 在整个应用中保持视觉元素的一致性",
        "对比度 - 确保文本和背景之间有足够的对比度",
        "留白 - 使用适当的留白来改善可读性和视觉层次"
    ]


# 苹果风格组件样式
class AppleStyleComponents:
    """苹果风格组件样式"""
    
    @staticmethod
    def button_style(config: AppleStyleConfig, variant: str = "primary") -> Dict[str, Any]:
        """获取按钮样式"""
        styles = {
            "primary": {
                "fg_color": config.get_color("primary"),
                "hover_color": config.get_color("secondary"),
                "text_color": "white",
                "corner_radius": 8,
                "height": 40,
                "font": config.get_font("button")
            },
            "secondary": {
                "fg_color": "transparent",
                "hover_color": config.get_color("background"),
                "text_color": config.get_color("text"),
                "corner_radius": 8,
                "height": 40,
                "font": config.get_font("button"),
                "border_width": 1,
                "border_color": config.get_color("border")
            },
            "success": {
                "fg_color": config.get_color("success"),
                "hover_color": config.get_color("success"),
                "text_color": "white",
                "corner_radius": 8,
                "height": 40,
                "font": config.get_font("button")
            },
            "warning": {
                "fg_color": config.get_color("warning"),
                "hover_color": config.get_color("warning"),
                "text_color": "white",
                "corner_radius": 8,
                "height": 40,
                "font": config.get_font("button")
            },
            "error": {
                "fg_color": config.get_color("error"),
                "hover_color": config.get_color("error"),
                "text_color": "white",
                "corner_radius": 8,
                "height": 40,
                "font": config.get_font("button")
            }
        }
        return styles.get(variant, styles["primary"])
    
    @staticmethod
    def card_style(config: AppleStyleConfig) -> Dict[str, Any]:
        """获取卡片样式"""
        return {
            "fg_color": config.get_color("surface"),
            "corner_radius": 12,
            "border_width": 0,
            "padx": config.get_component_spacing("card_padding")[0],
            "pady": config.get_component_spacing("card_padding")[1]
        }
    
    @staticmethod
    def input_style(config: AppleStyleConfig) -> Dict[str, Any]:
        """获取输入框样式"""
        return {
            "font": config.get_font("body"),
            "corner_radius": 8,
            "border_width": 1,
            "border_color": config.get_color("border"),
            "fg_color": config.get_color("surface"),
            "text_color": config.get_color("text"),
            "placeholder_text_color": config.get_color("placeholder")
        }
    
    @staticmethod
    def label_style(config: AppleStyleConfig, variant: str = "body") -> Dict[str, Any]:
        """获取标签样式"""
        return {
            "font": config.get_font(variant),
            "text_color": config.get_color("text")
        } 