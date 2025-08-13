"""
场景匹配Agent - 负责生成场景分析和推荐方案
"""
import json
from typing import Dict, Any, List
from llm_client import SiliconFlowClient
from models import ScenarioMatcherOutput, Scenario, Recommendation, Elimination, Badge, BadgeTone
from config import AGENT_CONFIG, PROMPT_TEMPLATES

class ScenarioMatcherAgent:
    """场景匹配Agent"""
    
    def __init__(self, llm_client: SiliconFlowClient):
        self.llm_client = llm_client
        self.config = AGENT_CONFIG["scenario_matcher"]
    
    def run(self, user_query: str, eventic_graph: str, summary_base: str, 
            products: List[Dict], scoring_results: Dict, charts: List[Dict]) -> ScenarioMatcherOutput:
        """
        运行场景匹配Agent
        
        Args:
            user_query: 用户查询
            eventic_graph: 事理图谱
            summary_base: 基础数据
            products: 产品列表
            scoring_results: 评分结果
            charts: 图表配置
            
        Returns:
            场景匹配结果
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(user_query, eventic_graph, summary_base, 
                                     products, scoring_results, charts)
            
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
            expected_keys = ["scenarios", "recommendations", "elimination"]
            if not self.llm_client.validate_response(response, expected_keys):
                raise ValueError("模型响应格式不正确")
            
            # 构建输出
            output = ScenarioMatcherOutput(
                scenarios=self._build_scenarios(data.get("scenarios", [])),
                recommendations=self._build_recommendations(data.get("recommendations", [])),
                elimination=self._build_elimination(data.get("elimination", []))
            )
            
            return output
            
        except Exception as e:
            # 如果模型调用失败，使用备用方法
            return self._fallback_scenario_matching(products, scoring_results, charts)
    
    def _build_prompt(self, user_query: str, eventic_graph: str, summary_base: str,
                     products: List[Dict], scoring_results: Dict, charts: List[Dict]) -> str:
        """构建提示词"""
        return f"""
请基于以下信息生成场景分析和推荐方案：

用户查询：{user_query}

事理图谱：{eventic_graph}

产品数据：{summary_base}

产品列表：{json.dumps(products, ensure_ascii=False, indent=2)}

评分结果：{json.dumps(scoring_results, ensure_ascii=False, indent=2)}

图表配置：{json.dumps(charts, ensure_ascii=False, indent=2)}

请执行以下任务：
1. 分析用户使用场景，生成3-5个关键场景分析
2. 基于评分结果生成推荐方案（最佳选择、备选方案等）
3. 分析产品淘汰原因，说明为什么不推荐某些产品

请输出以下JSON格式：
{{
  "scenarios": [
    {{
      "icon": "场景图标",
      "title": "场景标题",
      "bullets": ["要点1", "要点2", "要点3"]
    }}
  ],
  "recommendations": [
    {{
      "title": "推荐标题",
      "badge": {{
        "text": "推荐标签",
        "tone": "primary/success/warning/danger/info",
        "icon": "图标"
      }},
      "productId": "产品ID",
      "fit": "适合原因",
      "reasons": ["推荐理由1", "推荐理由2"],
      "tradeoffs": ["权衡考虑1", "权衡考虑2"]
    }}
  ],
  "elimination": [
    {{
      "title": "淘汰标题",
      "level": "淘汰级别",
      "icon": "图标",
      "bullets": ["淘汰原因1", "淘汰原因2"]
    }}
  ]
}}

注意：
- 保持通用性，避免使用特定商品名称
- 场景分析要基于用户的实际使用需求
- 推荐方案要客观公正，基于数据评分
- 淘汰说明要给出具体的技术或功能原因
"""
    
    def _build_scenarios(self, scenarios_data: List[Dict]) -> List[Scenario]:
        """构建场景列表"""
        scenarios = []
        for item in scenarios_data:
            scenario = Scenario(
                icon=item.get("icon", "fa-question"),
                title=item.get("title", ""),
                bullets=item.get("bullets", [])
            )
            scenarios.append(scenario)
        return scenarios
    
    def _build_recommendations(self, recommendations_data: List[Dict]) -> List[Recommendation]:
        """构建推荐列表"""
        recommendations = []
        for item in recommendations_data:
            badge = Badge(
                text=item.get("badge", {}).get("text", ""),
                tone=BadgeTone(item.get("badge", {}).get("tone", "primary")),
                icon=item.get("badge", {}).get("icon", "fa-star")
            )
            
            recommendation = Recommendation(
                title=item.get("title", ""),
                badge=badge,
                productId=item.get("productId", ""),
                fit=item.get("fit", ""),
                reasons=item.get("reasons", []),
                tradeoffs=item.get("tradeoffs", [])
            )
            recommendations.append(recommendation)
        return recommendations
    
    def _build_elimination(self, elimination_data: List[Dict]) -> List[Elimination]:
        """构建淘汰说明列表"""
        elimination = []
        for item in elimination_data:
            elim = Elimination(
                title=item.get("title", ""),
                level=item.get("level", ""),
                icon=item.get("icon", "fa-times"),
                bullets=item.get("bullets", [])
            )
            elimination.append(elim)
        return elimination
    
    def _fallback_scenario_matching(self, products: List[Dict], scoring_results: Dict, charts: List[Dict]) -> ScenarioMatcherOutput:
        """备用场景匹配方法"""
        try:
            # 基于评分结果生成简单推荐
            # 处理产品数据，确保能正确获取ID和价格
            processed_products = []
            for product in products:
                if hasattr(product, 'dict'):
                    # 如果是Pydantic模型，转换为字典
                    product_dict = product.dict()
                elif isinstance(product, dict):
                    # 如果已经是字典
                    product_dict = product
                else:
                    # 其他情况，尝试获取属性
                    product_dict = {
                        "id": getattr(product, "id", str(product)),
                        "name": getattr(product, "name", "未知产品"),
                        "price": getattr(product, "price", 0),
                        "type": getattr(product, "type", ""),
                        "attributes": getattr(product, "attributes", {})
                    }
                processed_products.append(product_dict)
            
            # 按评分排序
            sorted_products = sorted(processed_products, 
                                   key=lambda x: scoring_results.get(x.get("id", ""), {}).get("total", 0),
                                   reverse=True)
            
            # 生成场景分析
            scenarios = [
                Scenario(
                    icon="fa-home",
                    title="日常使用场景",
                    bullets=["考虑产品的核心功能和实用性", "关注产品的耐用性和维护便利性", "评估产品的使用成本"]
                ),
                Scenario(
                    icon="fa-star",
                    title="高品质需求场景",
                    bullets=["关注产品的材质和工艺水平", "考虑品牌信誉和售后服务", "评估产品的长期价值"]
                ),
                Scenario(
                    icon="fa-dollar-sign",
                    title="性价比优先场景",
                    bullets=["在预算范围内选择最优配置", "平衡价格与功能需求", "考虑产品的投资回报"]
                ),
                Scenario(
                    icon="fa-cog",
                    title="技术性能场景",
                    bullets=["关注产品的核心技术指标", "评估产品的创新程度", "考虑产品的技术成熟度"]
                )
            ]
            
            # 生成推荐方案
            recommendations = []
            if sorted_products:
                # 最佳选择
                top_product = sorted_products[0]
                top_score = scoring_results.get(top_product.get("id", ""), {}).get("total", 0)
                recommendations.append(Recommendation(
                    title="最佳选择",
                    badge=Badge(text="推荐", tone=BadgeTone.PRIMARY, icon="fa-crown"),
                    productId=top_product.get("id", ""),
                    fit=f"综合评分最高({top_score}分)，各项性能均衡",
                    reasons=["性能表现优秀", "性价比高", "配置完善"],
                    tradeoffs=["可能存在某些方面的不足", "价格相对较高"]
                ))
                
                # 备选方案
                if len(sorted_products) > 1:
                    second_product = sorted_products[1]
                    second_score = scoring_results.get(second_product.get("id", ""), {}).get("total", 0)
                    recommendations.append(Recommendation(
                        title="备选方案",
                        badge=Badge(text="备选", tone=BadgeTone.SUCCESS, icon="fa-star"),
                        productId=second_product.get("id", ""),
                        fit=f"性能良好({second_score}分)，可作为备选",
                        reasons=["性能表现良好", "价格合理", "配置适中"],
                        tradeoffs=["相比最佳选择略有不足", "某些功能可能不够完善"]
                    ))
                
                # 经济型选择
                if len(sorted_products) > 2:
                    third_product = sorted_products[2]
                    third_score = scoring_results.get(third_product.get("id", ""), {}).get("total", 0)
                    recommendations.append(Recommendation(
                        title="经济型选择",
                        badge=Badge(text="经济", tone=BadgeTone.INFO, icon="fa-coins"),
                        productId=third_product.get("id", ""),
                        fit=f"性价比突出({third_score}分)，适合预算有限用户",
                        reasons=["价格实惠", "基本功能齐全", "维护成本低"],
                        tradeoffs=["高端功能可能缺失", "性能相对较低"]
                    ))
            
            # 生成淘汰说明
            elimination = [
                Elimination(
                    title="性能不足产品",
                    level="淘汰",
                    icon="fa-times",
                    bullets=["综合评分较低", "关键性能指标不达标", "性价比相对较低"]
                ),
                Elimination(
                    title="配置不匹配产品",
                    level="不推荐",
                    icon="fa-exclamation-triangle",
                    bullets=["功能配置与需求不匹配", "使用场景限制较多", "维护成本较高"]
                )
            ]
            
            return ScenarioMatcherOutput(
                scenarios=scenarios,
                recommendations=recommendations,
                elimination=elimination
            )
            
        except Exception as e:
            # 如果所有方法都失败，返回默认结果
            return ScenarioMatcherOutput(
                scenarios=[
                    Scenario(
                        icon="fa-info-circle",
                        title="默认场景分析",
                        bullets=["基于产品数据进行基础分析", "考虑价格、性能、配置等维度"]
                    )
                ],
                recommendations=[
                    Recommendation(
                        title="基础推荐",
                        badge=Badge(text="推荐", tone=BadgeTone.INFO, icon="fa-thumbs-up"),
                        productId=products[0].get("id", "") if products and hasattr(products[0], "get") else (products[0].id if products and hasattr(products[0], "id") else ""),
                        fit="基于可用数据的基础推荐",
                        reasons=["数据完整", "性能指标明确"],
                        tradeoffs=["推荐精度可能有限"]
                    )
                ],
                elimination=[
                    Elimination(
                        title="数据不足产品",
                        level="待评估",
                        icon="fa-question-circle",
                        bullets=["数据信息不完整", "需要进一步评估", "建议谨慎考虑"]
                    )
                ]
            ) 