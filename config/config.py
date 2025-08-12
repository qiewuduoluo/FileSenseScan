# config.py
import os

# 模型选择：deepseek | qwen
USE_MODEL = os.getenv("USE_MODEL", "qwen")  # deepseek | qwen

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-4f27bc9149234af5862394e7cd8eea3c")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")

# 通义千问（OpenAI兼容模式）
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "sk-2248b259f25148e7bbf554cd702cb088")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME", "qwen-turbo-latest")

# 请求控制
REQ_TIMEOUT = int(os.getenv("REQ_TIMEOUT", "60"))
REQ_RETRY   = int(os.getenv("REQ_RETRY", "3"))
