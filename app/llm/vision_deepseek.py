# deepseek_vl_api.py
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

def deepseek_vl_call(image_bytes: bytes, prompt: str) -> str:
    # 1) 上传图片
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    files = {"file": ("page.png", image_bytes, "image/png")}
    upload_resp = requests.post(f"{DEEPSEEK_BASE_URL}/files", headers=headers, files=files, timeout=60)
    upload_resp.raise_for_status()
    file_id = upload_resp.json()["id"]

    # 2) 视觉对话
    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    headers["Content-Type"] = "application/json"
    data = {
        "model": "deepseek-vl-chat",
        "messages": [
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"deepseek-file://{file_id}"}},
                {"type": "text", "text": prompt}
            ]}
        ],
        "temperature": 0.7
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
