"""
配置文件 - 包含模型配置和Agent参数
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 硅基流动模型配置
SILICONFLOW_CONFIG = {
    "base_url": "https://api.siliconflow.cn/v1",
    "model": "deepseek-ai/DeepSeek-R1",
    "api_key": os.getenv("SILICONFLOW_API_KEY", ""),
    "temperature": 0.7,
    "max_tokens": 4000
}

# Agent配置
AGENT_CONFIG = {
    "data_normalizer": {
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "数据规范化Agent，负责预处理和标准化数据"
    },
    "requirement_analyzer": {
        "temperature": 0.7,
        "max_tokens": 3000,
        "description": "需求分析Agent，分析用户query，生成需求维度"
    },
    "product_transformer": {
        "temperature": 0.5,
        "max_tokens": 4000,
        "description": "产品转换Agent，将车型数据转换为模板所需的products格式"
    },
    "scoring_calculator": {
        "temperature": 0.4,
        "max_tokens": 3000,
        "description": "评分计算Agent，计算各维度评分和排序"
    },
    "scenario_matcher": {
        "temperature": 0.6,
        "max_tokens": 3500,
        "description": "场景匹配Agent，生成场景分析和推荐方案"
    },
    "report_assembler": {
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "报告组装Agent，组装最终的reportData"
    }
}

# 报告模板配置
REPORT_CONFIG = {
    "max_products": 10,
    "max_charts": 8,
    "max_scenarios": 5,
    "max_recommendations": 3
}

# 通用提示词模板
PROMPT_TEMPLATES = {
    "system_prefix": """你是一个专业的泛商品推荐报告生成助手。你的任务是分析用户需求、产品数据和事理图谱，生成结构化的报告数据。

重要原则：
1. 保持通用性：避免使用特定商品名称或行业术语，使用通用的描述
2. 数据一致性：确保所有引用的ID、属性名等保持一致
3. 逻辑清晰：按照事理图谱的逻辑结构组织内容
4. 客观分析：基于数据给出客观的分析和建议

请严格按照要求的JSON格式输出，不要包含任何解释性文字。""",
    
    "output_format": """请严格按照以下JSON格式输出，不要包含任何其他内容：

{
  "section_name": {
    // 具体的数据结构
  }
}"""
} 