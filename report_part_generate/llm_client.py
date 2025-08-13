"""
硅基流动模型客户端 - 用于与模型API交互
"""
import json
import requests
from typing import Dict, Any, Optional
from config import SILICONFLOW_CONFIG

class SiliconFlowClient:
    """硅基流动模型客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = SILICONFLOW_CONFIG["base_url"]
        self.model = SILICONFLOW_CONFIG["model"]
        self.api_key = api_key or SILICONFLOW_CONFIG["api_key"]
        self.temperature = SILICONFLOW_CONFIG["temperature"]
        self.max_tokens = SILICONFLOW_CONFIG["max_tokens"]
        
        if not self.api_key:
            raise ValueError("API key is required. Please set SILICONFLOW_API_KEY environment variable.")
    
    def chat_completion(
        self, 
        messages: list, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        发送聊天完成请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            模型响应内容
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid API response format: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def extract_json(self, response: str) -> Dict[str, Any]:
        """
        从模型响应中提取JSON数据
        
        Args:
            response: 模型响应文本
            
        Returns:
            解析后的JSON数据
        """
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            import re
            
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # 查找可能的JSON内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            raise ValueError(f"无法从响应中提取有效的JSON数据: {response[:200]}...")
    
    def validate_response(self, response: str, expected_keys: list) -> bool:
        """
        验证响应是否包含预期的键
        
        Args:
            response: 模型响应文本
            expected_keys: 预期的键列表
            
        Returns:
            是否验证通过
        """
        try:
            data = self.extract_json(response)
            for key in expected_keys:
                if key not in data:
                    return False
            return True
        except:
            return False 