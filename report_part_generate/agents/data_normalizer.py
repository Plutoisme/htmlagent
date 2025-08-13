"""
数据规范化Agent - 负责预处理和标准化数据
"""
import json
import re
from typing import Dict, Any, List
from llm_client import SiliconFlowClient
from models import DataNormalizerOutput
from config import AGENT_CONFIG, PROMPT_TEMPLATES

class DataNormalizerAgent:
    """数据规范化Agent"""
    
    def __init__(self, llm_client: SiliconFlowClient):
        self.llm_client = llm_client
        self.config = AGENT_CONFIG["data_normalizer"]
    
    def run(self, user_query: str, eventic_graph: str, summary_base: str) -> DataNormalizerOutput:
        """
        运行数据规范化Agent
        
        Args:
            user_query: 用户查询
            eventic_graph: 事理图谱
            summary_base: 基础数据
            
        Returns:
            规范化后的数据
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(user_query, eventic_graph, summary_base)
            
            # 调用模型
            messages = [
                {"role": "system", "content": PROMPT_TEMPLATES["system_prefix"]},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm_client.chat_completion(
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            
            # 提取JSON数据
            data = self.llm_client.extract_json(response)
            
            # 验证响应
            expected_keys = ["productIdMap", "commonAttributes", "normalizedData"]
            if not self.llm_client.validate_response(response, expected_keys):
                raise ValueError("模型响应格式不正确")
            
            # 构建输出
            output = DataNormalizerOutput(
                productIdMap=data.get("productIdMap", {}),
                commonAttributes=data.get("commonAttributes", []),
                normalizedData=data.get("normalizedData", {})
            )
            
            return output
            
        except Exception as e:
            # 如果模型调用失败，使用备用方法
            return self._fallback_normalization(summary_base)
    
    def _build_prompt(self, user_query: str, eventic_graph: str, summary_base: str) -> str:
        """构建提示词"""
        return f"""
请分析以下数据并进行规范化处理：

用户查询：{user_query}

事理图谱：{eventic_graph}

产品数据：{summary_base}

请执行以下任务：
1. 为每个产品生成唯一的ID（格式：品牌-型号-版本，如：byd-song-plus-ev）
2. 提取所有产品的共同属性维度
3. 标准化数据格式，确保属性名一致

请输出以下JSON格式：
{{
  "productIdMap": {{
    "产品ID": "产品名称"
  }},
  "commonAttributes": ["属性1", "属性2", "属性3"],
  "normalizedData": {{
    "产品ID": {{
      "标准化后的数据"
    }}
  }}
}}

注意：
- 保持通用性，避免使用特定商品名称
- 确保所有产品ID唯一且有意义
- 提取最核心、最重要的属性维度
- 标准化属性名称，使用统一的术语
"""
    
    def _fallback_normalization(self, summary_base: str) -> DataNormalizerOutput:
        """备用规范化方法"""
        try:
            # 尝试解析JSON数据
            if isinstance(summary_base, str):
                data = json.loads(summary_base)
            else:
                data = summary_base
            
            product_id_map = {}
            common_attributes = set()
            normalized_data = {}
            
            # 处理每个产品
            for product_name, product_info in data.items():
                # 生成产品ID
                product_id = self._generate_product_id(product_name)
                product_id_map[product_id] = product_name
                
                # 提取属性（通用方法）
                if "核心参数" in product_info:
                    core_params = product_info["核心参数"]
                    for key, value in core_params.items():
                        if value is not None and value != "":
                            common_attributes.add(key)
                
                # 标准化数据
                normalized_data[product_id] = self._standardize_product_data(product_info)
            
            return DataNormalizerOutput(
                productIdMap=product_id_map,
                commonAttributes=list(common_attributes),
                normalizedData=normalized_data
            )
            
        except Exception as e:
            # 如果所有方法都失败，返回空结果
            return DataNormalizerOutput()
    
    def _generate_product_id(self, product_name: str) -> str:
        """生成产品ID"""
        # 移除特殊字符，转换为小写，用连字符连接
        id_str = re.sub(r'[^\w\s-]', '', product_name.lower())
        id_str = re.sub(r'\s+', '-', id_str.strip())
        return id_str
    
    def _standardize_product_data(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """标准化产品数据"""
        standardized = {}
        
        # 处理核心参数
        if "核心参数" in product_info:
            core_params = product_info["核心参数"]
            for key, value in core_params.items():
                if value is not None and value != "":
                    standardized[key] = value
        
        # 处理其他重要信息（通用属性）
        important_keys = ["价格", "品牌", "型号", "规格", "材质", "功能", "配置", "评价", "使用说明"]
        for key in important_keys:
            if key in product_info:
                standardized[key] = product_info[key]
        
        return standardized 