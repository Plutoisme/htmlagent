"""
评分计算Agent - 计算各维度评分和排序
"""
from typing import Dict, Any, List
from llm_client import SiliconFlowClient
from models import ScoringCalculatorOutput, Chart
from config import AGENT_CONFIG, PROMPT_TEMPLATES
import json

class ScoringCalculatorAgent:
    """评分计算Agent"""
    
    def __init__(self, llm_client: SiliconFlowClient):
        self.llm_client = llm_client
        self.config = AGENT_CONFIG["scoring_calculator"]
    
    def run(self, user_query: str, eventic_graph: str, summary_base: str,
            products: List[Dict[str, Any]] = None, decision_factors: List[Dict[str, Any]] = None) -> ScoringCalculatorOutput:
        """
        运行评分计算Agent
        
        Args:
            user_query: 用户查询
            eventic_graph: 事理图谱
            summary_base: 基础数据
            products: 产品列表
            decision_factors: 决策因素列表
            
        Returns:
            评分计算结果
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(user_query, eventic_graph, summary_base, products, decision_factors)
            
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
            expected_keys = ["charts", "scoringResults"]
            if not self.llm_client.validate_response(response, expected_keys):
                raise ValueError("模型响应格式不正确")
            
            # 构建图表列表
            charts = []
            for chart_data in data.get("charts", []):
                try:
                    chart = Chart(**chart_data)
                    charts.append(chart)
                except Exception as e:
                    # 如果单个图表解析失败，跳过
                    continue
            
            # 构建评分结果
            scoring_results = data.get("scoringResults", {})
            
            output = ScoringCalculatorOutput(
                charts=charts,
                scoringResults=scoring_results
            )
            
            return output
            
        except Exception as e:
            # 如果模型调用失败，使用备用方法
            return self._fallback_scoring(products, decision_factors)
    
    def _build_prompt(self, user_query: str, eventic_graph: str, summary_base: str,
                      products: List[Dict[str, Any]] = None, decision_factors: List[Dict[str, Any]] = None) -> str:
        """构建提示词"""
        products_info = ""
        if products:
            # 将产品数据转换为更清晰的格式
            products_data = []
            for product in products:
                if hasattr(product, 'dict'):
                    product_dict = product.dict()
                else:
                    product_dict = product
                
                # 提取关键属性用于评分
                product_summary = {
                    "id": product_dict.get("id", ""),
                    "name": product_dict.get("name", ""),
                    "price": product_dict.get("price", 0),
                    "type": product_dict.get("type", ""),
                    "attributes": product_dict.get("attributes", {})
                }
                products_data.append(product_summary)
            
            products_info = f"\n产品数据：{json.dumps(products_data, ensure_ascii=False, indent=2)}"
        
        decision_factors_info = ""
        if decision_factors:
            # 将决策因素转换为更清晰的格式
            factors_data = []
            for factor in decision_factors:
                if hasattr(factor, 'dict'):
                    factor_dict = factor.dict()
                else:
                    factor_dict = factor
                factors_data.append(factor_dict)
            
            decision_factors_info = f"\n决策因素：{json.dumps(factors_data, ensure_ascii=False, indent=2)}"
        
        return f"""
请基于以下信息计算产品评分并生成图表配置：

用户查询：{user_query}

事理图谱：{eventic_graph}

基础数据：{summary_base}{products_info}{decision_factors_info}

请执行以下任务：
1. 基于用户需求和产品数据，计算各维度的评分
2. 生成合适的图表配置，用于可视化对比
3. 确保图表配置与产品属性一致
4. 评分要客观、合理，基于数据而非主观判断

请输出以下JSON格式：
{{
  "charts": [
    {{
      "id": "图表ID",
      "title": "图表标题",
      "note": "图表说明",
      "type": "图表类型",
      "metricKey": "属性键名",
      "unit": "单位",
      "suggestedMax": 建议最大值,
      "stepSize": 步长,
      "reverse": false
    }}
  ],
  "scoringResults": {{
    "产品ID": {{
      "total": 总分,
      "核心性能": 核心性能分数,
      "品质配置": 品质配置分数,
      "性价比": 性价比分数,
      "适用性": 适用性分数
    }}
  }}
}}

评分原则：
- 核心性能：基于产品的主要功能指标，如性能参数、规格等
- 品质配置：基于产品的质量、材质、工艺等配置水平
- 性价比：基于价格与配置的平衡关系
- 适用性：基于产品对用户需求的匹配程度
- 总分：各项分数的加权平均，权重根据用户需求重要性确定

图表配置原则：
- 选择最能体现产品差异的关键属性作为metricKey
- 图表类型根据数据特点选择：bar（对比）、line（趋势）、radar（多维度）、pie（占比）等
- 确保metricKey与产品属性名完全一致
- 图表标题要清晰表达对比内容

注意：
- 保持通用性，避免使用特定商品类型或行业术语
- 图表ID要唯一且有意义
- 评分要基于客观数据，避免主观判断
- 根据实际产品属性和用户需求灵活调整评分维度
"""
    
    def _fallback_scoring(self, products: List[Dict[str, Any]] = None, decision_factors: List[Dict[str, Any]] = None) -> ScoringCalculatorOutput:
        """备用评分计算方法"""
        try:
            charts = []
            scoring_results = {}
            
            if products:
                # 创建价格对比图表（通用）
                price_chart = Chart(
                    id="price-comparison",
                    title="价格对比",
                    type="bar",
                    metricKey="price",
                    unit="元",
                    suggestedMax=20
                )
                charts.append(price_chart)
                
                # 创建核心属性对比图表（根据产品类型动态选择）
                core_attr_chart = Chart(
                    id="core-attribute-comparison",
                    title="核心属性对比",
                    type="bar",
                    metricKey="核心属性",
                    unit="",
                    suggestedMax=100
                )
                charts.append(core_attr_chart)
                
                # 计算基础评分
                for product in products:
                    # 处理产品ID
                    if hasattr(product, 'id'):
                        product_id = product.id
                    elif hasattr(product, 'dict'):
                        product_id = product.dict().get("id", "")
                    else:
                        product_id = str(product.get("id", "")) if isinstance(product, dict) else str(product)
                    
                    # 处理产品价格
                    if hasattr(product, 'price'):
                        price = product.price
                    elif hasattr(product, 'dict'):
                        price = product.dict().get("price", 0)
                    else:
                        price = product.get("price", 0) if isinstance(product, dict) else 0
                    
                    # 处理产品类型
                    if hasattr(product, 'type'):
                        product_type = product.type
                    elif hasattr(product, 'dict'):
                        product_type = product.dict().get("type", "")
                    else:
                        product_type = product.get("type", "") if isinstance(product, dict) else ""
                    
                    # 处理产品属性
                    if hasattr(product, 'attributes'):
                        attributes = product.attributes
                    elif hasattr(product, 'dict'):
                        attributes = product.dict().get("attributes", {})
                    else:
                        attributes = product.get("attributes", {}) if isinstance(product, dict) else {}
                    
                    # 基础评分逻辑
                    base_score = 70
                    
                    # 价格评分（根据产品类型调整）
                    if price > 0:
                        if "汽车" in product_type or "车" in product_type:
                            # 汽车类产品价格评分
                            if price <= 100000:
                                price_score = 20
                            elif price <= 200000:
                                price_score = 15
                            elif price <= 500000:
                                price_score = 10
                            else:
                                price_score = 5
                        else:
                            # 其他产品价格评分
                            if price <= 1000:
                                price_score = 20
                            elif price <= 5000:
                                price_score = 15
                            elif price <= 10000:
                                price_score = 10
                            else:
                                price_score = 5
                    else:
                        price_score = 10
                    
                    # 核心性能评分（根据产品类型和属性调整）
                    core_score = 15
                    if attributes:
                        # 根据具体属性调整评分
                        if "续航" in str(attributes) or "性能" in str(attributes):
                            core_score = 18
                        elif "容量" in str(attributes) or "功率" in str(attributes):
                            core_score = 17
                    
                    # 品质配置评分
                    quality_score = 15
                    if attributes:
                        if "安全" in str(attributes) or "配置" in str(attributes):
                            quality_score = 18
                        elif "材质" in str(attributes) or "工艺" in str(attributes):
                            quality_score = 17
                    
                    # 适用性评分
                    applicability_score = 10
                    if attributes:
                        if "适用" in str(attributes) or "场景" in str(attributes):
                            applicability_score = 12
                        elif "便利" in str(attributes) or "维护" in str(attributes):
                            applicability_score = 11
                    
                    total_score = base_score + price_score + core_score + quality_score + applicability_score
                    
                    scoring_results[product_id] = {
                        "total": total_score,
                        "价格": price_score,
                        "核心性能": core_score,
                        "品质配置": quality_score,
                        "适用性": applicability_score
                    }
            
            return ScoringCalculatorOutput(
                charts=charts,
                scoringResults=scoring_results
            )
            
        except Exception as e:
            # 如果备用方法也失败，返回默认结果
            return ScoringCalculatorOutput(
                charts=[
                    Chart(
                        id="default-chart",
                        title="默认图表",
                        type="bar",
                        metricKey="default",
                        unit="",
                        suggestedMax=100
                    )
                ],
                scoringResults={
                    "default": {
                        "total": 100,
                        "默认评分": 100
                    }
                }
            ) 