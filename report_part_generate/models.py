"""
数据模型定义 - 包含State和各个Agent的输出数据结构
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, RootModel
from enum import Enum

class BadgeTone(str, Enum):
    """徽章色调枚举"""
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"

class Badge(BaseModel):
    """徽章模型"""
    text: str
    tone: BadgeTone
    icon: str

class Hero(BaseModel):
    """Hero区域模型"""
    title: str
    subtitle: str
    chips: List[Dict[str, str]] = []
    cta: Optional[Dict[str, str]] = None
    stats: List[Dict[str, str]] = []
    priorityBadge: Optional[Badge] = None
    progressBars: List[Dict[str, Any]] = []
    note: Optional[str] = None

class GraphInsights(BaseModel):
    """事理图谱洞察模型"""
    dimensions: List[Dict[str, str]] = []
    knowledge: Optional[Dict[str, Any]] = None
    flow: Optional[Dict[str, Any]] = None

class DecisionFactor(BaseModel):
    """决策因素模型"""
    icon: str
    title: str
    description: str

class ProductAttribute(RootModel):
    """产品属性模型"""
    root: Dict[str, Union[str, int, float, None]]

class ProductDetails(BaseModel):
    """产品详情模型"""
    pros: List[str] = []
    cons: List[str] = []
    notes: List[str] = []

class Product(BaseModel):
    """产品模型"""
    id: str
    name: str
    price: float
    currency: str = "CNY"
    type: str
    tags: List[str] = []
    highlights: List[str] = []
    attributes: Dict[str, Union[str, int, float, None]]
    details: ProductDetails = ProductDetails()

class Chart(BaseModel):
    """图表模型"""
    id: str
    title: str
    note: str = ""
    type: str
    metricKey: Optional[str] = None
    metricKeys: Optional[List[str]] = None
    unit: str = ""
    suggestedMax: Optional[Union[int, float]] = None
    stepSize: Optional[Union[int, float]] = None
    reverse: bool = False

class Table(BaseModel):
    """对比表模型"""
    title: str
    notes: List[str] = []
    columns: Optional[List[str]] = None
    highlightRules: Dict[str, str] = {}
    actions: Dict[str, Any] = {}

class Scenario(BaseModel):
    """场景分析模型"""
    icon: str
    title: str
    bullets: List[str] = []

class Elimination(BaseModel):
    """说明模型"""
    title: str
    level: str
    icon: str
    bullets: List[str] = []

class Recommendation(BaseModel):
    """推荐模型"""
    title: str
    badge: Badge
    productId: str
    fit: str
    reasons: List[str] = []
    tradeoffs: List[str] = []

class ReportData(BaseModel):
    """完整的报告数据模型"""
    meta: Dict[str, str] = {}
    nav: List[Dict[str, str]] = []
    hero: Hero
    graphInsights: GraphInsights
    decisionFactors: List[DecisionFactor] = []
    products: List[Product] = []
    charts: List[Chart] = []
    table: Table
    scenarios: List[Scenario] = []
    elimination: List[Elimination] = []
    recommendations: List[Recommendation] = []

# Agent输出模型
class DataNormalizerOutput(BaseModel):
    """数据规范化Agent输出"""
    productIdMap: Dict[str, str] = {}
    commonAttributes: List[str] = []
    normalizedData: Dict[str, Any] = {}

class RequirementAnalyzerOutput(BaseModel):
    """需求分析Agent输出"""
    graphInsights: GraphInsights
    decisionFactors: List[DecisionFactor]

class ProductTransformerOutput(BaseModel):
    """产品转换Agent输出"""
    products: List[Product]

class ScoringCalculatorOutput(BaseModel):
    """评分计算Agent输出"""
    charts: List[Chart]
    scoringResults: Dict[str, Dict[str, Union[int, float]]]

class ScenarioMatcherOutput(BaseModel):
    """场景匹配Agent输出"""
    scenarios: List[Scenario]
    recommendations: List[Recommendation]
    elimination: List[Elimination]

class ReportAssemblerOutput(BaseModel):
    """报告组装Agent输出"""
    reportData: ReportData

# LangGraph State模型
class AgentState(BaseModel):
    """Agent状态模型"""
    # 输入数据
    user_query: str
    eventic_graph: str
    summary_base: str
    
    # Agent输出
    data_normalizer_output: Optional[DataNormalizerOutput] = None
    requirement_analyzer_output: Optional[RequirementAnalyzerOutput] = None
    product_transformer_output: Optional[ProductTransformerOutput] = None
    scoring_calculator_output: Optional[ScoringCalculatorOutput] = None
    scenario_matcher_output: Optional[ScenarioMatcherOutput] = None
    report_assembler_output: Optional[ReportAssemblerOutput] = None
    
    # 最终输出
    final_report_data: Optional[ReportData] = None
    
    # 错误信息
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True 