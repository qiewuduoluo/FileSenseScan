# markdown_writer.py
def save_to_markdown(results, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for page in results:
            f.write(f"## 第{page['page']}页（类型：{page['type']}）\n")
            f.write(page["interpretation"])
            f.write("\n\n---\n\n")
