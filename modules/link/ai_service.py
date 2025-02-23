import logging
import re

import aiohttp

from bot.config import API_KEY, API_URL


class AIService:
    def __init__(self):
        self.api_key = API_KEY
        self.api_url = API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _format_markdown_to_html(self, text: str) -> str:
        """
        将 Markdown 格式转换为 Telegram HTML 格式
        """
        # 移除多余的空行
        text = re.sub(r'\n\s*\n', '\n', text)

        # 处理标题
        text = re.sub(r'#{1,6}\s+(.+)', r'<b>\1</b>', text)

        # 处理加粗
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

        # 处理斜体
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)

        # 处理代码块
        text = re.sub(r'```.*?\n(.*?)```', r'<code>\1</code>', text, flags=re.DOTALL)

        # 处理行内代码
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

        # 处理列表
        text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', r'📌 ', text, flags=re.MULTILINE)

        # 处理引用
        text = re.sub(r'^\s*>\s+(.+)', r'❝ \1', text, flags=re.MULTILINE)

        # 移除链接格式但保留文本
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # 确保段落之间有适当的间距
        text = text.replace('\n\n', '\n')

        return text.strip()

    async def _make_request(self, messages: list, temperature: float = 0.5) -> str:
        """
        发送请求到 API
        请求格式：
        {
          "model": "gpt-4o-mini",
          "messages": [ ... ],
          "max_tokens": 1688,
          "temperature": 0.5,
          "stream": false
        }
        """
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 1688,
            "temperature": temperature,
            "stream": False
        }

        logging.info("发送请求到 API, payload: %s", payload)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API 请求失败: 状态码 {response.status}, 错误信息: {error_text}")
                result = await response.json()
                content = result['choices'][0]['message']['content']
                return self._format_markdown_to_html(content)  # 在返回之前格式化内容

    async def generate_title(self, url: str, content: str) -> str:
        """根据链接和内容生成标题"""
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的标题生成助手。请根据提供的网页内容生成一个简洁的中文标题，长度控制在15-25字之间。不要使用 markdown 格式。"
            },
            {
                "role": "user",
                "content": f"请为以下网页内容生成标题：\n链接：{url}\n内容：{content}"
            }
        ]
        try:
            return await self._make_request(messages)
        except Exception as e:
            raise Exception(f"生成标题时发生错误: {str(e)}")

    async def generate_summary(self, url: str, content: str) -> str:
        """生成内容摘要"""
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的文章摘要生成助手。请生成简洁的中文摘要，使用HTML格式，避免使用 markdown。"
            },
            {
                "role": "user",
                "content": f"请为以下链接内容生成一个简洁的中文摘要：\n链接：{url}\n内容：{content}\n要求：摘要长度控制在200字以内，保留关键信息，使用简洁明了的语言。"
            }
        ]
        try:
            return await self._make_request(messages)
        except Exception as e:
            raise Exception(f"生成摘要时发生错误: {str(e)}")

    async def generate_explanation(self, url: str, content: str) -> str:
        """生成详细解释"""
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的内容解释助手。请用通俗易懂的方式解释内容，使用HTML格式，避免使用 markdown。"
            },
            {
                "role": "user",
                "content": f"请为以下链接内容生成一个详细的解释：\n链接：{url}\n内容：{content}\n要求：解释主要概念和术语，分析内容的重点，使用通俗易懂的语言。"
            }
        ]
        try:
            return await self._make_request(messages)
        except Exception as e:
            raise Exception(f"生成解释时发生错误: {str(e)}")
