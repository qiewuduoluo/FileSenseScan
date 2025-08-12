# baidu_ocr.py
import requests
import base64
import urllib.parse

API_KEY = "BMyfv976oKz1POkzEE8WocQe"
SECRET_KEY = "UaEfSwoDLHcD8S2M4xsw14hpsbaNXRwd"

# 获取 access_token（缓存建议后续加）
def get_access_token():
    url = f"https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    res = requests.get(url, params=params)
    return res.json().get("access_token")

# 图像转文字 OCR 主函数
def ocr_image(image_bytes):
    access_token = get_access_token()
    ocr_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"

    image_base64 = base64.b64encode(image_bytes).decode()
    image_encoded = urllib.parse.quote_plus(image_base64)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"image={image_encoded}"

    res = requests.post(ocr_url, headers=headers, data=data)
    result_json = res.json()

    # 提取文字结果
    if "words_result" in result_json:
        words = [item["words"] for item in result_json["words_result"]]
        return "\n".join(words)
    else:
        print("❌ OCR失败：", result_json)
        return ""
