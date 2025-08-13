"""
报告组装Agent - 负责组装最终的reportData
"""
import json
from typing import Dict, Any, List
from llm_client import SiliconFlowClient
from models import (ReportAssemblerOutput, ReportData, Hero, Badge, BadgeTone, 
                   Table, GraphInsights, DecisionFactor)
from config import AGENT_CONFIG, PROMPT_TEMPLATES

class ReportAssemblerAgent:
    """报告组装Agent"""
    
    def __init__(self, llm_client: SiliconFlowClient):
        self.llm_client = llm_client
        self.config = AGENT_CONFIG["report_assembler"]
    
    def run(self, user_query: str, eventic_graph: str, summary_base: str,
            data_normalizer_output: Dict, requirement_analyzer_output: Dict,
            product_transformer_output: Dict, scoring_calculator_output: Dict,
            scenario_matcher_output: Dict) -> ReportAssemblerOutput:
        """
        运行报告组装Agent
        
        Args:
            user_query: 用户查询
            eventic_graph: 事理图谱
            summary_base: 基础数据
            data_normalizer_output: 数据规范化输出
            requirement_analyzer_output: 需求分析输出
            product_transformer_output: 产品转换输出
            scoring_calculator_output: 评分计算输出
            scenario_matcher_output: 场景匹配输出
            
        Returns:
            完整的报告数据
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(user_query, eventic_graph, summary_base,
                                     data_normalizer_output, requirement_analyzer_output,
                                     product_transformer_output, scoring_calculator_output,
                                     scenario_matcher_output)
            
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
            expected_keys = ["meta", "nav", "hero"]
            if not self.llm_client.validate_response(response, expected_keys):
                raise ValueError("模型响应格式不正确")
            
            # 构建完整的报告数据
            report_data = self._assemble_report_data(
                data, data_normalizer_output, requirement_analyzer_output,
                product_transformer_output, scoring_calculator_output, scenario_matcher_output
            )
            
            output = ReportAssemblerOutput(reportData=report_data)
            return output
            
        except Exception as e:
            # 如果模型调用失败，使用备用方法
            return self._fallback_assembly(
                data_normalizer_output, requirement_analyzer_output,
                product_transformer_output, scoring_calculator_output, scenario_matcher_output
            )
    
    def _build_prompt(self, user_query: str, eventic_graph: str, summary_base: str,
                     data_normalizer_output: Dict, requirement_analyzer_output: Dict,
                     product_transformer_output: Dict, scoring_calculator_output: Dict,
                     scenario_matcher_output: Dict) -> str:
        """构建提示词"""
        return f"""
请基于以下信息组装完整的报告数据：

用户查询：{user_query}

事理图谱：{eventic_graph}

基础数据：{summary_base}

数据规范化输出：{json.dumps(data_normalizer_output, ensure_ascii=False, indent=2)}

需求分析输出：{json.dumps(requirement_analyzer_output, ensure_ascii=False, indent=2)}

产品转换输出：{json.dumps(product_transformer_output, ensure_ascii=False, indent=2)}

评分计算输出：{json.dumps(scoring_calculator_output, ensure_ascii=False, indent=2)}

场景匹配输出：{json.dumps(scenario_matcher_output, ensure_ascii=False, indent=2)}

请执行以下任务：
1. 生成报告的元信息（标题、描述等）
2. 生成导航菜单结构
3. 生成Hero区域内容（标题、副标题、统计信息等）

请输出以下JSON格式：
{{
  "meta": {{
    "title": "报告标题",
    "description": "报告描述",
    "keywords": "关键词1,关键词2,关键词3"
  }},
  "nav": [
    {{
      "title": "导航标题",
      "href": "锚点链接"
    }}
  ],
  "hero": {{
    "title": "主标题",
    "subtitle": "副标题",
    "chips": [
      {{
        "text": "标签文本",
        "color": "标签颜色"
      }}
    ],
    "stats": [
      {{
        "label": "统计标签",
        "value": "统计值"
      }}
    ]
  }}
}}

注意：
- 保持通用性，避免使用特定商品名称
- 标题要简洁明了，突出核心价值
- 导航要覆盖报告的所有主要章节
- Hero区域要吸引用户注意力，突出关键信息
"""
    
    def _assemble_report_data(self, hero_data: Dict, data_normalizer_output: Dict,
                             requirement_analyzer_output: Dict, product_transformer_output: Dict,
                             scoring_calculator_output: Dict, scenario_matcher_output: Dict) -> ReportData:
        """组装完整的报告数据"""
        
        # 构建Hero区域
        hero = Hero(
            title=hero_data.get("hero", {}).get("title", "商品推荐报告"),
            subtitle=hero_data.get("hero", {}).get("subtitle", "基于您的需求，为您推荐最适合的商品"),
            chips=hero_data.get("hero", {}).get("chips", []),
            stats=hero_data.get("hero", {}).get("stats", [])
        )
        
        # 构建导航
        nav = hero_data.get("nav", [])
        
        # 构建元信息
        meta = hero_data.get("meta", {})
        
        # 构建事理图谱洞察
        graph_insights = GraphInsights(
            dimensions=requirement_analyzer_output.get("graphInsights", {}).get("dimensions", [])
        )
        
        # 构建决策因素
        decision_factors = []
        for factor_data in requirement_analyzer_output.get("decisionFactors", []):
            factor = DecisionFactor(
                icon=factor_data.get("icon", "fa-question"),
                title=factor_data.get("title", ""),
                description=factor_data.get("description", "")
            )
            decision_factors.append(factor)
        
        # 构建产品列表
        products = product_transformer_output.get("products", [])
        
        # 构建图表配置
        charts = scoring_calculator_output.get("charts", [])
        
        # 构建对比表
        table = Table(
            title="产品对比表",
            notes=["数据来源于官方参数和用户评价"],
            columns=["产品名称", "价格", "核心特性", "推荐指数"]
        )
        
        # 构建场景分析
        scenarios = scenario_matcher_output.get("scenarios", [])
        
        # 构建淘汰说明
        elimination = scenario_matcher_output.get("elimination", [])
        
        # 构建推荐方案
        recommendations = scenario_matcher_output.get("recommendations", [])
        
        # 组装完整的报告数据
        report_data = ReportData(
            meta=meta,
            nav=nav,
            hero=hero,
            graphInsights=graph_insights,
            decisionFactors=decision_factors,
            products=products,
            charts=charts,
            table=table,
            scenarios=scenarios,
            elimination=elimination,
            recommendations=recommendations
        )
        
        return report_data
    
    def _fallback_assembly(self, data_normalizer_output: Dict, requirement_analyzer_output: Dict,
                          product_transformer_output: Dict, scoring_calculator_output: Dict,
                          scenario_matcher_output: Dict) -> ReportAssemblerOutput:
        """备用组装方法"""
        try:
            # 生成默认的Hero区域
            hero = Hero(
                title="智能商品推荐报告",
                subtitle="基于您的具体需求，为您精心挑选最适合的商品",
                chips=[
                    {"text": "个性化推荐", "color": "primary"},
                    {"text": "数据驱动", "color": "success"},
                    {"text": "客观分析", "color": "info"}
                ],
                stats=[
                    {"label": "分析产品", "value": str(len(product_transformer_output.get("products", [])))},
                    {"label": "关键维度", "value": str(len(requirement_analyzer_output.get("decisionFactors", [])))},
                    {"label": "推荐方案", "value": str(len(scenario_matcher_output.get("recommendations", [])))}
                ]
            )
            
            # 生成默认导航
            nav = [
                {"title": "需求分析", "href": "#requirements"},
                {"title": "产品对比", "href": "#products"},
                {"title": "场景分析", "href": "#scenarios"},
                {"title": "推荐方案", "href": "#recommendations"}
            ]
            
            # 生成默认元信息
            meta = {
                "title": "智能商品推荐报告",
                "description": "基于用户需求和产品数据的个性化推荐分析",
                "keywords": "商品推荐,需求分析,产品对比,智能分析"
            }
            
            # 构建事理图谱洞察
            graph_insights = GraphInsights(
                dimensions=requirement_analyzer_output.get("graphInsights", {}).get("dimensions", [])
            )
            
            # 构建决策因素
            decision_factors = []
            for factor_data in requirement_analyzer_output.get("decisionFactors", []):
                factor = DecisionFactor(
                    icon=factor_data.get("icon", "fa-question"),
                    title=factor_data.get("title", ""),
                    description=factor_data.get("description", "")
                )
                decision_factors.append(factor)
            
            # 构建产品列表
            products = product_transformer_output.get("products", [])
            
            # 构建图表配置
            charts = scoring_calculator_output.get("charts", [])
            
            # 构建对比表
            table = Table(
                title="产品对比表",
                notes=["数据来源于官方参数和用户评价"],
                columns=["产品名称", "价格", "核心特性", "推荐指数"]
            )
            
            # 构建场景分析
            scenarios = scenario_matcher_output.get("scenarios", [])
            
            # 构建淘汰说明
            elimination = scenario_matcher_output.get("elimination", [])
            
            # 构建推荐方案
            recommendations = scenario_matcher_output.get("recommendations", [])
            
            # 组装完整的报告数据
            report_data = ReportData(
                meta=meta,
                nav=nav,
                hero=hero,
                graphInsights=graph_insights,
                decisionFactors=decision_factors,
                products=products,
                charts=charts,
                table=table,
                scenarios=scenarios,
                elimination=elimination,
                recommendations=recommendations
            )
            
            return ReportAssemblerOutput(reportData=report_data)
            
        except Exception as e:
            # 如果所有方法都失败，返回空结果
            # 创建一个空的ReportData作为默认值
            empty_report = ReportData(
                meta={},
                nav=[],
                hero=Hero(title="", subtitle=""),
                graphInsights=GraphInsights(),
                decisionFactors=[],
                products=[],
                charts=[],
                table=Table(title=""),
                scenarios=[],
                elimination=[],
                recommendations=[]
            )
            return ReportAssemblerOutput(reportData=empty_report) 