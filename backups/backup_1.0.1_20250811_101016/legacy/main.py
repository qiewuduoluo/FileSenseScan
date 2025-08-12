# main.py
import os
from pdf_utils import extract_pdf_pages
from deepseek_qwen_text_api import chat_call
from markdown_writer import save_to_markdown
from baidu_ocr import ocr_image  # ✅ 新增：引入百度 OCR 模块

def process_pdf(pdf_path):
    pages = extract_pdf_pages(pdf_path)
    all_results = []

    for i, page in enumerate(pages):
        print(f"📄 正在处理第 {i+1} 页...")

        if page['type'] == 'text':
            prompt = f"请你帮我提炼下面内容的摘要、重点知识点和难点解释：\n\n{page['content']}"
            try:
                result = chat_call(prompt)  # 使用统一的API调用
            except Exception as e:
                print(f"❌ 第{i+1}页调用 API 出错：", e)
                result = f"第 {i+1} 页解析失败。"
        else:
            print(f"🔍 第{i+1}页是图像，开始调用百度OCR识别文字...")
            ocr_text = ocr_image(page['content'])

            if ocr_text.strip():
                prompt = f"以下是通过OCR识别的PDF图像文字内容，请提取重点并解读：\n\n{ocr_text}"
                try:
                    result = chat_call(prompt)  # 使用统一的API调用
                except Exception as e:
                    print(f"❌ 第{i+1}页 API 解读失败：", e)
                    result = f"图像页文字提取成功，但解读失败。"
            else:
                result = "（图像页 OCR 识别失败，未提取出文字）"

        all_results.append({
            "page": i + 1,
            "type": page['type'],
            "interpretation": result
        })

    return all_results

if __name__ == "__main__":
    # PDF 路径（注意 raw 字符串）
    pdf_path = r"H:\起萌成长\CK-生物样本库信息项目\SZCDC-YBK-SOP-301 样本库信息系统操作规程.pdf"
    
    # 输出路径
    output_dir = r"H:\Code\FileSenseScan\OutPur_Data_Result"
    output_filename = "生物样本库信息项目_解读结果.md"
    output_path = os.path.join(output_dir, output_filename)

    result_list = process_pdf(pdf_path)
    save_to_markdown(result_list, output_path)

    print(f"\n✅ 所有页面处理完成，结果已保存至：{output_path}")
