# main_batch.py
import os, time
from app.core.pdf_utils import extract_pdf_pages
from app.services.baidu_ocr import ocr_image
from app.services.llm.text_api import chat_call

# ==================== 核心PDF处理函数 ====================
def process_pdf(
    pdf_path,
    output_root,
    unit_page_ranges=None,
    *,
    callbacks=None,
    provider_getter=None,   # -> str | None  e.g. lambda: "deepseek" or "qwen"
):
    """
    callbacks: 可选dict
      - on_file_start(file_name, total_pages)
      - on_page_start(page_num, total_pages)
      - on_page_done(page_num, total_pages, save_path)
      - on_file_done(file_name, out_dir)
      - on_error(msg)

    provider_getter: 可选函数，每次页调用前获取模型名；
      若为 None，则使用 config.USE_MODEL
    """
    # ==================== 回调函数初始化 ====================
    cb = callbacks or {}
    def _cb(name, *args):
        fn = cb.get(name)
        if callable(fn):
            try: fn(*args)
            except Exception: pass

    # ==================== 文件预处理 ====================
    pages = extract_pdf_pages(pdf_path)
    total_pages = len(pages)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    out_dir = os.path.join(output_root, base_name)
    os.makedirs(out_dir, exist_ok=True)

    _cb("on_file_start", base_name, total_pages)

    # ==================== 单元分组初始化 ====================
    unit_buckets = {u: [] for u in (unit_page_ranges or {})}

    # ==================== 逐页处理循环 ====================
    for i, page in enumerate(pages, 1):
        _cb("on_page_start", i, total_pages)

        # 每页决定使用哪个模型（支持处理中切换，从下一页起生效）
        provider = provider_getter() if provider_getter else None

        # ==================== 页面内容类型判断 ====================
        if page["type"] == "text":
            prompt = f"请你帮我提炼下面内容的摘要、重点知识点和难点解释：\n\n{page['content']}"
        else:
            # ==================== OCR图像识别处理 ====================
            ocr_text = ocr_image(page["content"])
            if not ocr_text.strip():
                content = "（图像页 OCR 识别失败）"
                _save_md(i, content, out_dir, base_name)
                _cb("on_page_done", i, total_pages, None)
                continue
            prompt = f"以下是通过OCR识别的PDF图像文字内容，请提取重点并解读：\n\n{ocr_text}"

        # ==================== LLM模型调用 ====================
        try:
            result = chat_call(prompt, provider=provider)  # 👈 每页读取 provider
        except Exception as e:
            msg = f"第{i}页解析失败：{e}"
            _cb("on_error", msg)
            result = msg

        # ==================== 结果保存与回调 ====================
        save_path = _save_md(i, result, out_dir, base_name)
        _cb("on_page_done", i, total_pages, save_path)

        # ==================== 单元内容收集 ====================
        for u, rng in (unit_page_ranges or {}).items():
            if i in rng:
                unit_buckets[u].append(result)

        time.sleep(0.2)  # 轻限速，避免刷屏/超限

    # ==================== 单元总结生成 ====================
    for u, items in unit_buckets.items():
        if items: _save_unit_md(u, items, out_dir, base_name)

    _cb("on_file_done", base_name, out_dir)
    return out_dir

# ==================== 单页Markdown保存 ====================
def _save_md(page_num, content, out_dir, base_name):
    fn = f"{base_name}_第{page_num}页.md"
    path = os.path.join(out_dir, fn)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# 第{page_num}页解读结果\n\n{content}")
    return path

# ==================== 单元总结Markdown保存 ====================
def _save_unit_md(unit_num, contents, out_dir, base_name):
    fn = f"{base_name}_第{unit_num}单元的总结.md"
    path = os.path.join(out_dir, fn)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# 第{unit_num}单元总结\n\n")
        for i, c in enumerate(contents, 1):
            f.write(f"## 来自第{i}页内容\n\n{c}\n\n---\n\n")
    return path 