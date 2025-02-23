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
                return content

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
