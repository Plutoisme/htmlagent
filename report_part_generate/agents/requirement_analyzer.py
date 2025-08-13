"""
需求分析Agent - 分析用户query，生成需求维度
"""
from typing import Dict, Any
from llm_client import SiliconFlowClient
from models import RequirementAnalyzerOutput, GraphInsights, DecisionFactor
from config import AGENT_CONFIG, PROMPT_TEMPLATES

class RequirementAnalyzerAgent:
    """需求分析Agent"""
    
    def __init__(self, llm_client: SiliconFlowClient):
        self.llm_client = llm_client
        self.config = AGENT_CONFIG["requirement_analyzer"]
    
    def run(self, user_query: str, eventic_graph: str, summary_base: str) -> RequirementAnalyzerOutput:
        """
        运行需求分析Agent
        
        Args:
            user_query: 用户查询
            eventic_graph: 事理图谱
            summary_base: 基础数据
            
        Returns:
            需求分析结果
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
            expected_keys = ["graphInsights", "decisionFactors"]
            if not self.llm_client.validate_response(response, expected_keys):
                raise ValueError("模型响应格式不正确")
            
            # 构建输出
            graph_insights = GraphInsights(**data.get("graphInsights", {}))
            decision_factors = [DecisionFactor(**factor) for factor in data.get("decisionFactors", [])]
            
            output = RequirementAnalyzerOutput(
                graphInsights=graph_insights,
                decisionFactors=decision_factors
            )
            
            return output
            
        except Exception as e:
            # 如果模型调用失败，使用备用方法
            return self._fallback_analysis(user_query, eventic_graph)
    
    def _build_prompt(self, user_query: str, eventic_graph: str, summary_base: str) -> str:
        """构建提示词"""
        return f"""
请分析以下用户需求并生成需求维度和决策因素：

用户查询：{user_query}

事理图谱：{eventic_graph}

产品数据：{summary_base}

请执行以下任务：
1. 基于事理图谱和用户查询，生成需求维度分析
2. 提取关键的决策因素
3. 确保分析结果具有通用性，不绑定特定商品

请输出以下JSON格式：
{{
  "graphInsights": {{
    "dimensions": [
      {{
        "icon": "fa-icon-name",
        "title": "维度标题",
        "description": "维度描述"
      }}
    ],
    "knowledge": {{
      "title": "信息指引标题",
      "points": [
        {{
          "badge": "标签",
          "text": "说明文字"
        }}
      ]
    }},
    "flow": {{
      "title": "流程提示标题",
      "notes": ["步骤1", "步骤2", "步骤3"]
    }}
  }},
  "decisionFactors": [
    {{
      "icon": "fa-icon-name",
      "title": "决策因素标题",
      "description": "决策因素描述"
    }}
  ]
}}

注意：
- 使用FontAwesome图标名称（如fa-snowflake, fa-road, fa-battery-full等）
- 保持通用性，避免使用特定商品名称
- 基于事理图谱的逻辑结构组织内容
- 重点关注用户的核心需求和约束条件
"""
    
    def _fallback_analysis(self, user_query: str, eventic_graph: str) -> RequirementAnalyzerOutput:
        """备用分析方法"""
        # 基于用户查询提取关键信息
        dimensions = []
        decision_factors = []
        
        # 分析用户查询中的关键信息（通用方法）
        if "预算" in user_query or "价格" in user_query:
            dimensions.append({
                "icon": "fa-coins",
                "title": "预算约束",
                "description": "在预算范围内选择最优配置，平衡性能、配置和价格"
            })
        
        if "质量" in user_query or "品质" in user_query:
            dimensions.append({
                "icon": "fa-star",
                "title": "品质要求",
                "description": "关注产品的材质、工艺和整体质量水平"
            })
        
        if "功能" in user_query or "性能" in user_query:
            dimensions.append({
                "icon": "fa-cogs",
                "title": "功能性能",
                "description": "产品核心功能的实现程度和性能表现"
            })
        
        if "使用场景" in user_query or "环境" in user_query:
            dimensions.append({
                "icon": "fa-home",
                "title": "使用环境",
                "description": "考虑产品在不同使用场景和环境下的适应性"
            })
        
        if "品牌" in user_query or "信誉" in user_query:
            dimensions.append({
                "icon": "fa-certificate",
                "title": "品牌信誉",
                "description": "品牌知名度和售后服务保障能力"
            })
        
        # 生成决策因素（通用）
        decision_factors = [
            DecisionFactor(
                icon="fa-cogs",
                title="核心功能",
                description="产品主要功能的实现程度和性能表现"
            ),
            DecisionFactor(
                icon="fa-star",
                title="品质水平",
                description="产品的材质、工艺和整体质量水平"
            ),
            DecisionFactor(
                icon="fa-coins",
                title="性价比",
                description="价格与配置的平衡关系，物有所值程度"
            ),
            DecisionFactor(
                icon="fa-home",
                title="适用性",
                description="产品对用户需求的匹配程度和使用便利性"
            )
        ]
        
        # 构建知识指引
        knowledge = {
            "title": "需求分析指引",
            "points": [
                {"badge": "功能需求", "text": "明确产品的核心功能和使用场景"},
                {"badge": "品质要求", "text": "关注产品的质量标准和耐用性"},
                {"badge": "预算控制", "text": "在预算范围内选择最优配置组合"}
            ]
        }
        
        # 构建决策流程
        flow = {
            "title": "决策流程",
            "notes": [
                "明确使用场景和约束条件",
                "筛选符合预算的产品",
                "评估核心性能指标",
                "权衡各维度表现",
                "确定最终选择"
            ]
        }
        
        # 构建事理图谱洞察
        graph_insights = GraphInsights(
            dimensions=dimensions,
            knowledge=knowledge,
            flow=flow
        )
        
        return RequirementAnalyzerOutput(
            graphInsights=graph_insights,
            decisionFactors=decision_factors
        ) 