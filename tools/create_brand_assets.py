#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建品牌资源文件的脚本
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_logo():
    """创建简单的LOGO图片"""
    # 创建一个120x120的图片
    img = Image.new('RGBA', (120, 120), (44, 147, 255, 255))  # 蓝色背景
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    draw.ellipse([10, 10, 110, 110], fill=(44, 147, 255, 255))
    
    # 绘制文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
        except:
            font = ImageFont.load_default()
    
    # 绘制"FS"文字
    text = "FS"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (120 - text_width) // 2
    y = (120 - text_height) // 2
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # 保存
    logo_path = os.path.join("assets", "logo.png")
    img.save(logo_path, "PNG")
    print(f"✅ 创建LOGO：{logo_path}")
    return logo_path

def create_icon():
    """创建简单的图标文件"""
    # 创建一个32x32的图片
    img = Image.new('RGBA', (32, 32), (44, 147, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    draw.ellipse([2, 2, 30, 30], fill=(44, 147, 255, 255))
    
    # 绘制文字
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
        except:
            font = ImageFont.load_default()
    
    # 绘制"F"文字
    text = "F"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (32 - text_width) // 2
    y = (32 - text_height) // 2
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # 保存为ICO
    icon_path = os.path.join("assets", "app.ico")
    img.save(icon_path, "ICO")
    print(f"✅ 创建图标：{icon_path}")
    return icon_path

def main():
    """主函数"""
    print("🎨 创建资源文件...")
    
    # 确保assets目录存在
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"✅ 创建目录：{assets_dir}")
    
    # 创建LOGO和图标
    try:
        create_logo()
        create_icon()
        print("\n🎉 资源文件创建完成！")
        print("现在可以运行 GUI 应用了：")
        print("python app/gui_app_modern.py")
    except Exception as e:
        print(f"❌ 创建资源文件失败：{e}")
        print("GUI应用仍可运行，但会使用默认配置")

if __name__ == "__main__":
    main() 