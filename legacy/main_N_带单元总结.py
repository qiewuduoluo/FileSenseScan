# main_N_带单元总结.py
import os
import time  # ✅ 新增：防止请求过快
from pdf_utils import extract_pdf_pages
from deepseek_text_api import deepseek_text_call
from baidu_ocr import ocr_image

# 保存每一页单独的 markdown 文件
def save_page_to_markdown(page_num, content, output_dir, base_filename="人教数学4年级上册_解读结果"):
    filename = f"{base_filename}_第{page_num}页.md"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# 第{page_num}页解读结果\n\n")
        f.write(content)
    print(f"✅ 第 {page_num} 页结果已保存：{filename}")
    return content  # 返回内容供单元汇总使用

# 保存单元汇总内容
def save_unit_summary(unit_num, content_list, output_dir, base_filename="人教数学4年级上册_解读结果"):
    filename = f"{base_filename}_第{unit_num}单元的总结.md"
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# 第{unit_num}单元总结\n\n")
        for idx, content in enumerate(content_list, start=1):
            f.write(f"## 来自第{idx}页内容：\n\n")
            f.write(content + "\n\n---\n\n")
    print(f"📘 单元{unit_num}总结已保存：{filename}")

# 自定义单元页码范围
unit_page_ranges = {
    1: list(range(1, 6)),     # 第1单元：第1~5页
    2: list(range(6, 11)),    # 第2单元：第6~10页
    # 可继续添加：
    # 3: list(range(11, 17)),
}

def process_pdf(pdf_path, output_dir):
    pages = extract_pdf_pages(pdf_path)
    unit_collections = {unit: [] for unit in unit_page_ranges}

    for i, page in enumerate(pages):
        page_num = i + 1
        print(f"\n📄 正在处理第 {page_num} 页...")

        if page['type'] == 'text':
            prompt = f"请你帮我提炼下面内容的摘要、重点知识点和难点解释：\n\n{page['content']}"
            try:
                result = deepseek_text_call(prompt)
                time.sleep(1)  # ✅ 防止请求频率过快
            except Exception as e:
                print(f"❌ 第{page_num}页调用 DeepSeek 出错：", e)
                result = f"第 {page_num} 页解析失败。"
        else:
            print(f"🔍 第{page_num}页是图像，调用百度OCR识别...")
            ocr_text = ocr_image(page['content'])

            if ocr_text.strip():
                prompt = f"以下是通过OCR识别的PDF图像文字内容，请提取重点并解读：\n\n{ocr_text}"
                try:
                    result = deepseek_text_call(prompt)
                    time.sleep(1)  # ✅ 图像页也等待一秒
                except Exception as e:
                    print(f"❌ 第{page_num}页 DeepSeek 解读失败：", e)
                    result = "图像页文字提取成功，但解读失败。"
            else:
                result = "（图像页 OCR 识别失败，未提取出文字）"

        # ✅ 每页生成 markdown 文件
        content = result
        save_page_to_markdown(page_num, content, output_dir)

        # ✅ 收集对应单元页的内容
        for unit, page_range in unit_page_ranges.items():
            if page_num in page_range:
                unit_collections[unit].append(content)

    # ✅ 输出单元总结
    for unit, contents in unit_collections.items():
        if contents:
            save_unit_summary(unit, contents, output_dir)

    print("\n✅ 全部页面和单元总结生成完成。")

if __name__ == "__main__":
    # PDF 路径（注意 raw 字符串）
    pdf_path = r"H:\起萌成长\CK-生物样本库信息项目\SZCDC-YBK-SOP-301 样本库信息系统操作规程.pdf"
    output_dir = r"H:\Code\FileSenseScan\OutPur_Data_Result"

    process_pdf(pdf_path, output_dir)
