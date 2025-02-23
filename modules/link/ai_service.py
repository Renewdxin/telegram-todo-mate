import aiohttp
from bot.config import GROK_API_KEY, AI_PROXY

class GrokAIService:
    def __init__(self):
        self.api_key = GROK_API_KEY
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.proxy = AI_PROXY

    async def _make_request(self, messages: list) -> str:
        """发送请求到 Grok API"""
        payload = {
            "messages": messages,
            "model": "grok-2-latest",
            "stream": False,
            "temperature": 0.7  # 可以通过配置调整
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                proxy=self.proxy
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API 请求失败: {error_text}")
                    
                result = await response.json()
                return result['choices'][0]['message']['content']

    async def generate_summary(self, url: str, content: str) -> str:
        """生成链接内容的摘要"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的文章摘要生成助手，请生成简洁的中文摘要。"
                },
                {
                    "role": "user",
                    "content": f"""请为以下链接内容生成一个简洁的中文摘要：
                    链接：{url}
                    内容：{content}
                    
                    要求：
                    1. 摘要长度控制在200字以内
                    2. 保留关键信息
                    3. 使用简洁明了的语言
                    """
                }
            ]
            
            return await self._make_request(messages)
            
        except Exception as e:
            raise Exception(f"生成摘要时发生错误: {str(e)}")

    async def generate_explanation(self, url: str, content: str) -> str:
        """生成链接内容的解释"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的内容解释助手，请用通俗易懂的方式解释内容。"
                },
                {
                    "role": "user",
                    "content": f"""请为以下链接内容生成一个详细的解释：
                    链接：{url}
                    内容：{content}
                    
                    要求：
                    1. 解释主要概念和术语
                    2. 分析内容的重点
                    3. 使用通俗易懂的语言
                    """
                }
            ]
            
            return await self._make_request(messages)
            
        except Exception as e:
            raise Exception(f"生成解释时发生错误: {str(e)}") 