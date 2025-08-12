# deepseek_qwen_text_api.py
import time, requests
from typing import Dict, Any, List, Optional
from config.config import (
    USE_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL_NAME,
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL_NAME,
    REQ_TIMEOUT, REQ_RETRY
)

def _post(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
    last = None
    for i in range(REQ_RETRY):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=REQ_TIMEOUT)
            if r.status_code < 400: return r.json()
            last = RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
        except Exception as e:
            last = e
        time.sleep(min(1.5**(i+1), 6))
    raise last or RuntimeError("LLM request failed")

def _messages(prompt: str, system: Optional[str]=None) -> List[Dict[str,str]]:
    msgs = []
    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    return msgs

def chat_call(prompt: str, *, system: Optional[str]=None,
              temperature: float=0.7, max_tokens: Optional[int]=None,
              provider: Optional[str]=None, model: Optional[str]=None) -> str:
    provider = (provider or USE_MODEL).lower()
    msgs = _messages(prompt, system)

    if provider == "deepseek":
        url = f"{DEEPSEEK_BASE_URL}/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": model or DEEPSEEK_MODEL_NAME, "messages": msgs, "temperature": temperature}
        if max_tokens: payload["max_tokens"] = max_tokens
        data = _post(url, headers, payload)
        return data["choices"][0]["message"]["content"]

    elif provider == "qwen":
        url = f"{QWEN_BASE_URL}/chat/completions"
        headers = {"Authorization": f"Bearer {QWEN_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": model or QWEN_MODEL_NAME, "messages": msgs, "temperature": temperature}
        if max_tokens: payload["max_tokens"] = max_tokens
        data = _post(url, headers, payload)
        return data["choices"][0]["message"]["content"]

    else:
        raise ValueError(f"Unsupported provider: {provider}")
