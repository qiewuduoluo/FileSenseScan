import os
import requests
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL_NAME

def qwen_text_call(prompt: str, api_key: str = None, model: str = None, base_url: str = None,
                   timeout=60, max_tokens=4000) -> str:
    """
    通义千问文本生成调用函数
    
    Args:
        prompt: 输入提示词
        api_key: API密钥，默认使用配置文件中的密钥
        model: 模型名称，默认使用配置文件中的模型
        base_url: API基础URL，默认使用配置文件中的URL
        timeout: 请求超时时间
        max_tokens: 最大生成token数
    
    Returns:
        str: 生成的文本内容
    """
    # 使用默认配置
    api_key = api_key or QWEN_API_KEY
    model = model or QWEN_MODEL_NAME
    base_url = base_url or QWEN_BASE_URL
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers, 
            json=payload, 
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            error_msg = f"⚠️ 通义千问API调用失败：{response.status_code} - {response.text}"
            print(error_msg)
            return error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "⚠️ 通义千问API请求超时"
        print(error_msg)
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"⚠️ 通义千问API网络错误：{str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"⚠️ 通义千问API调用异常：{str(e)}"
        print(error_msg)
        return error_msg

def qwen_extend_content(original_content: str, target_word_count: int, chapter_context: str = "") -> str:
    """
    使用通义千问扩写内容到指定字数
    
    Args:
        original_content: 原始内容
        target_word_count: 目标字数
        chapter_context: 章节上下文信息
    
    Returns:
        str: 扩写后的内容
    """
    current_word_count = len(original_content)
    needed_words = target_word_count - current_word_count
    
    if needed_words <= 0:
        return original_content
    
    extend_prompt = f"""
请继续扩写以下小说内容，要求：

1. 当前内容：
{original_content}

2. 章节背景：{chapter_context}

3. 扩写要求：
- 需要增加约{needed_words}字
- 保持与现有内容的连贯性
- 延续当前的情节发展和人物对话
- 维持原有的写作风格和节奏
- 不要重复已有内容
- 扩写内容要自然流畅，符合小说逻辑

请直接输出扩写的内容，不要添加任何说明文字。
"""
    
    extended_content = qwen_text_call(extend_prompt)
    
    # 清理扩写内容
    extended_content = extended_content.strip()
    
    # 如果扩写内容为空或出错，返回原内容
    if not extended_content or extended_content.startswith("⚠️"):
        return original_content
    
    # 合并原内容和扩写内容
    combined_content = original_content + "\n\n" + extended_content
    
    return combined_content

def qwen_enhance_chapter(chapter_content: str, enhancement_type: str = "general") -> str:
    """
    使用通义千问增强章节内容
    
    Args:
        chapter_content: 章节内容
        enhancement_type: 增强类型（general, dialogue, description, emotion）
    
    Returns:
        str: 增强后的内容
    """
    enhancement_prompts = {
        "general": "请对以下小说章节进行润色，增强可读性和文学性，保持原有情节不变：",
        "dialogue": "请优化以下小说章节中的对话，使其更加自然生动，增强人物个性：",
        "description": "请增强以下小说章节的环境描写和场景描述，使其更加生动形象：",
        "emotion": "请增强以下小说章节的情感描写，深化人物内心活动和情感表达："
    }
    
    prompt = f"""
{enhancement_prompts.get(enhancement_type, enhancement_prompts["general"])}

{chapter_content}

要求：
1. 保持原有情节和人物设定
2. 增强文学性和可读性
3. 保持章节的完整性和连贯性
4. 不要改变核心剧情走向
"""
    
    enhanced_content = qwen_text_call(prompt)
    
    # 如果增强失败，返回原内容
    if not enhanced_content or enhanced_content.startswith("⚠️"):
        return chapter_content
    
    return enhanced_content.strip() 