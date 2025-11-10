import json
import re
from typing import Dict, Any
from app.core.config import settings
from app.models.schema import TripPlanResponse, DailyItinerary, Activity
import httpx


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = None
        self.base_url = None
        
        if self.provider == "openai":
            self.api_key = settings.OPENAI_API_KEY
            self.base_url = settings.OPENAI_BASE_URL or "https://api.openai.com/v1"
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY is not set in environment variables")
        elif self.provider == "bailian":
            self.api_key = settings.BAILIAN_API_KEY
            self.base_url = "https://dashscope.aliyuncs.com/api/v1"
            if not self.api_key:
                raise ValueError("BAILIAN_API_KEY is not set in environment variables")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Supported providers: openai, bailian")
    
    def _call_llm(self, prompt: str, model: str = None) -> str:
        """调用 LLM API"""
        if self.provider == "openai":
            return self._call_openai(prompt, model or "gpt-4")
        elif self.provider == "bailian":
            return self._call_bailian(prompt, model or "qwen-turbo")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _call_openai(self, prompt: str, model: str) -> str:
        """调用 OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个专业的旅行规划助手，能够根据用户需求生成详细的旅行计划。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    def _call_bailian(self, prompt: str, model: str) -> str:
        """调用阿里云百炼 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一个专业的旅行规划助手，能够根据用户需求生成详细的旅行计划。"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.7
            }
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["output"]["text"]
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """从 LLM 返回的文本中提取 JSON"""
        try:
            # 尝试找到 JSON 代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            else:
                # 尝试找到 { ... } 块
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)
                else:
                    # 如果没有找到 JSON，尝试直接解析整个文本
                    pass
            
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            # 如果解析失败，尝试修复常见的 JSON 问题
            # 移除可能的前后文本
            text = text.strip()
            # 尝试找到第一个 { 和最后一个 }
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                text = text[start:end+1]
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Failed to parse JSON from LLM response: {str(e)}\nResponse: {text[:500]}")
    
    def generate_trip_plan(self, user_prompt: str) -> Dict[str, Any]:
        """生成旅行计划"""
        prompt = f"""你是一个专业的旅行规划师。

根据用户输入：{user_prompt}

请严格按照以下 JSON 格式返回行程，不要有任何多余的文字。如果信息不足，请合理推断。

JSON 格式示例：
{{
    "destination": "日本东京",
    "daily_plan": [
        {{
            "day": 1,
            "title": "第一天：到达与初探",
            "summary": "抵达东京，适应时差，初步探索",
            "activities": [
                {{
                    "time": "09:00",
                    "activity": "抵达东京成田机场",
                    "description": "办理入境手续",
                    "location_name": "成田机场"
                }},
                {{
                    "time": "14:00",
                    "activity": "入住酒店",
                    "description": "放下行李，稍作休息",
                    "location_name": "新宿区酒店"
                }},
                {{
                    "time": "18:00",
                    "activity": "晚餐",
                    "description": "品尝当地美食",
                    "location_name": "新宿美食街"
                }}
            ]
        }}
    ],
    "budget_analysis": "根据5天行程和1万元预算，平均每天预算2000元。建议住宿300元/晚，餐饮500元/天，交通200元/天，购物和娱乐1000元/天。"
}}

请根据用户输入生成完整的行程计划。"""
        
        response_text = self._call_llm(prompt)
        plan_data = self._extract_json(response_text)
        
        return plan_data
    
    def extract_expense(self, expense_text: str) -> Dict[str, Any]:
        """从文本中提取费用信息"""
        prompt = f"""从以下文本中提取开销项目、金额和类别。

文本：{expense_text}

请严格按照以下 JSON 格式返回，不要有任何多余的文字：
{{
    "description": "项目描述",
    "amount": 金额（数字）,
    "category": "类别（餐饮/交通/住宿/购物/娱乐/其他）"
}}

如果无法提取金额，请返回 amount: 0。"""
        
        response_text = self._call_llm(prompt)
        expense_data = self._extract_json(response_text)
        
        return expense_data


llm_service = LLMService()

