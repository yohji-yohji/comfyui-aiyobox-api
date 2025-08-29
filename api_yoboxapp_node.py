import torch
import numpy as np
from PIL import Image
import requests
import base64
import io
import json
import re

class AiYoboxNode:
    """
    A ComfyUI node to call the aiyobox image generation API.

    This node sends a prompt and optional images to a specified API endpoint
    and receives a base64-encoded image, which is then decoded and output.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A beautiful landscape painting"}),
                "api_key": ("STRING", {"multiline": False, "default": "sk-your-key-here"}),
                "post_url": ("STRING", {"multiline": False, "default": "https://api.yoboxapp.com/v1/chat/completions"}),
                "model": ("STRING", {"multiline": False, "default": "gemini-2.0-flash-preview-image-generation"}),
                "timeout": ("INT", {"default": 30, "min": 5, "max": 300, "step": 1}),
            },
            "optional": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "aiyobox"

    def _tensor_to_base64(self, tensor):
        """Converts a torch tensor (B, H, W, C) to a base64 data URL."""
        image_np = tensor.squeeze(0).cpu().numpy()
        image_np = (image_np * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)

        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"

    def process(self, prompt, api_key, post_url, model, timeout, image1=None, image2=None, image3=None, image4=None, image5=None):
        if not api_key or api_key == "sk-your-key-here":
            raise ValueError("API Key is not set. Please provide a valid API Key.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        content = [{"type": "text", "text": prompt}]

        if image1 is not None:
            base64_image1 = self._tensor_to_base64(image1)
            content.append({"type": "image_url", "image_url": {"url": base64_image1}})

        if image2 is not None:
            base64_image2 = self._tensor_to_base64(image2)
            content.append({"type": "image_url", "image_url": {"url": base64_image2}})

        if image3 is not None:
            base64_image3 = self._tensor_to_base64(image3)
            content.append({"type": "image_url", "image_url": {"url": base64_image3}})

        if image4 is not None:
            base64_image4 = self._tensor_to_base64(image4)
            content.append({"type": "image_url", "image_url": {"url": base64_image4}})

        if image5 is not None:
            base64_image5 = self._tensor_to_base64(image5)
            content.append({"type": "image_url", "image_url": {"url": base64_image5}})

        payload = {
          "model": model,
          "messages": [{"role": "user", "content": content}],
          "stream": True,
          "language": "zh"
        }

        try:
            response = requests.post(post_url, headers=headers, json=payload, stream=True, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise Exception(f"API请求超时: 请求超过了 {timeout} 秒没有响应。请检查API服务器状态或增加超时时间。")
        except requests.exceptions.SSLError as e:
            raise Exception(f"API请求SSL错误: 与服务器建立安全连接失败。详细信息: {e}")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"API连接错误: 无法连接到服务器。请检查网络连接和API地址。详细信息: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")

        full_response_text = ""
        try:
            # 设置一个超时计时器，而不是在iter_lines中使用timeout参数
            import time
            start_time = time.time()
            
            for line in response.iter_lines():
                # 检查是否超时
                if time.time() - start_time > timeout:
                    raise requests.exceptions.Timeout(f"读取响应数据超时，超过了{timeout}秒")
                
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[len('data: '):].strip()
                        if json_str == '[DONE]':
                            break
                        if not json_str:
                            continue
                        try:
                            data = json.loads(json_str)
                            delta = data.get('choices', [{}])[0].get('delta', {})
                            if 'content' in delta and delta['content']:
                                full_response_text += delta['content']
                        except (json.JSONDecodeError, IndexError):
                            print(f"Skipping malformed stream line: {decoded_line}")
                            continue
        except requests.exceptions.Timeout as e:
            raise Exception(f"API流式读取超时: {str(e)}。已接收的部分数据: {full_response_text[:200]}...")
        
        if not full_response_text:
            raise Exception("API没有返回任何内容。请检查API响应和您的输入参数。")

        # 首先尝试提取URL
        url_match = re.search(r'https?://[^\s\)]+\.(?:png|jpg|jpeg|gif|webp)', full_response_text, re.IGNORECASE)
        if url_match:
            image_url = url_match.group(0)
            try:
                # 下载图片
                img_response = requests.get(image_url, timeout=timeout)
                img_response.raise_for_status()
                img = Image.open(io.BytesIO(img_response.content))

                # 转换为RGB格式（如果需要）
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img_np = np.array(img).astype(np.float32) / 255.0
                tensor = torch.from_numpy(img_np).unsqueeze(0)

                return (tensor,)
            except Exception as e:
                raise Exception(f"无法下载或处理URL图像: {image_url}\n错误: {e}")

        # 如果没有找到URL，尝试提取base64字符串
        b64_string = ""
        match = re.search(r'```(?:[a-zA-Z0-9]*)?\s*\n?(.*?)\n?```', full_response_text, re.DOTALL)
        if match:
            b64_string = match.group(1).strip()
        else:
            b64_match = re.search(r'([A-Za-z0-9+/=]{100,})', full_response_text)
            if b64_match:
                b64_string = b64_match.group(1).strip()

        if b64_string:
            try:
                img_data = base64.b64decode(b64_string)
                img = Image.open(io.BytesIO(img_data))

                # 转换为RGB格式（如果需要）
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img_np = np.array(img).astype(np.float32) / 255.0
                tensor = torch.from_numpy(img_np).unsqueeze(0)

                return (tensor,)
            except Exception as e:
                raise Exception(f"无法解码或处理base64图像: {e}\n提取的数据片段: {b64_string[:200]}...")

        # 如果既没有URL也没有base64，抛出错误
        raise Exception(f"无法从API响应中提取有效的图片URL或base64字符串。接收到的数据: {full_response_text[:500]}...")


NODE_CLASS_MAPPINGS = {
    "AiYoboxNode": AiYoboxNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AiYoboxNode": "AiYobox Image Generator"
} 