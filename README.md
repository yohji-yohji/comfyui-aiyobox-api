# ComfyUI AiYobox API Node

[English](#english) | [中文](#中文)

---

## 中文

### 简介
这是一个用于 ComfyUI 的节点插件，可以调用 AiYobox API 进行图像生成。通过这个节点，您可以使用文本提示词和参考图片来生成高质量的图像。

### 功能特性
- 支持文本提示词生成图像
- 支持最多5张参考图片输入
- 支持多种AI模型
- 流式响应处理
- 完整的错误处理机制
- 中文友好的错误提示

### 如何获取API密钥
1. 访问 [https://api.yoboxapp.com/](https://api.yoboxapp.com/)
2. 注册并登录您的账户
3. 申请API密钥
4. **获得密钥后即可使用所有可用的AI模型**

### 安装方法
1. 将此插件文件夹放入 ComfyUI 的 `custom_nodes` 目录
2. 重启 ComfyUI
3. 在节点菜单中找到 "AiYobox Image Generator"

### 使用方法
1. 在 ComfyUI 中添加 "AiYobox Image Generator" 节点
2. 填入您的API密钥
3. 输入文本提示词
4. （可选）连接最多5张参考图片
5. 运行工作流程

### 节点参数
- **prompt**: 文本提示词（必填）
- **api_key**: API密钥（必填）
- **post_url**: API地址（默认已设置）
- **model**: 模型名称（默认：gemini-2.0-flash-preview-image-generation）
- **timeout**: 请求超时时间（秒）
- **image1-5**: 可选的参考图片输入

---

## English

### Introduction
This is a ComfyUI node plugin for calling the AiYobox API to generate images. With this node, you can use text prompts and reference images to generate high-quality images.

### Features
- Support for text prompt image generation
- Support for up to 5 reference image inputs
- Support for multiple AI models
- Streaming response processing
- Comprehensive error handling
- User-friendly error messages

### How to Get API Key
1. Visit [https://api.yoboxapp.com/](https://api.yoboxapp.com/)
2. Register and login to your account
3. Apply for an API key
4. **Once you get the key, you can use all available AI models**

### Installation
1. Place this plugin folder in the `custom_nodes` directory of ComfyUI
2. Restart ComfyUI
3. Find "AiYobox Image Generator" in the node menu

### Usage
1. Add the "AiYobox Image Generator" node in ComfyUI
2. Enter your API key
3. Input text prompt
4. (Optional) Connect up to 5 reference images
5. Run the workflow

### Node Parameters
- **prompt**: Text prompt (required)
- **api_key**: API key (required)
- **post_url**: API endpoint URL (default provided)
- **model**: Model name (default: gemini-2.0-flash-preview-image-generation)
- **timeout**: Request timeout in seconds
- **image1-5**: Optional reference image inputs

### Requirements
- ComfyUI
- Python packages: torch, numpy, PIL, requests

### Support
If you encounter any issues, please check:
1. Your API key is valid and correctly entered
2. Your network connection is stable
3. The API service is available

---

## License
This project is open source and available under standard terms.