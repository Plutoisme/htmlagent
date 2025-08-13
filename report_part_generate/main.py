"""
主执行流程 - 使用LangGraph协调各个Agent
"""
import json
import asyncio
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from llm_client import SiliconFlowClient
from models import AgentState
from agents.data_normalizer import DataNormalizerAgent
from agents.requirement_analyzer import RequirementAnalyzerAgent
from agents.product_transformer import ProductTransformerAgent
from agents.scoring_calculator import ScoringCalculatorAgent
from agents.scenario_matcher import ScenarioMatcherAgent
from agents.report_assembler import ReportAssemblerAgent
from config import SILICONFLOW_CONFIG
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器主类"""
    
    def __init__(self):
        """初始化报告生成器"""
        # 初始化LLM客户端
        self.llm_client = SiliconFlowClient(
            api_key=SILICONFLOW_CONFIG["api_key"]
        )
        
        # 初始化各个Agent
        self.data_normalizer = DataNormalizerAgent(self.llm_client)
        self.requirement_analyzer = RequirementAnalyzerAgent(self.llm_client)
        self.product_transformer = ProductTransformerAgent(self.llm_client)
        self.scoring_calculator = ScoringCalculatorAgent(self.llm_client)
        self.scenario_matcher = ScenarioMatcherAgent(self.llm_client)
        self.report_assembler = ReportAssemblerAgent(self.llm_client)
        
        # 构建LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph"""
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("data_normalizer", self._run_data_normalizer)
        workflow.add_node("requirement_analyzer", self._run_requirement_analyzer)
        workflow.add_node("product_transformer", self._run_product_transformer)
        workflow.add_node("scoring_calculator", self._run_scoring_calculator)
        workflow.add_node("scenario_matcher", self._run_scenario_matcher)
        workflow.add_node("report_assembler", self._run_report_assembler)
        
        # 设置入口点
        workflow.set_entry_point("data_normalizer")
        
        # 设置执行流程
        workflow.add_edge("data_normalizer", "requirement_analyzer")
        workflow.add_edge("requirement_analyzer", "product_transformer")
        workflow.add_edge("product_transformer", "scoring_calculator")
        workflow.add_edge("scoring_calculator", "scenario_matcher")
        workflow.add_edge("scenario_matcher", "report_assembler")
        workflow.add_edge("report_assembler", END)
        
        # 直接编译图，不使用checkpointer
        return workflow.compile()
    
    async def _run_data_normalizer(self, state: AgentState) -> AgentState:
        """运行数据规范化Agent"""
        try:
            logger.info("开始运行数据规范化Agent...")
            
            output = self.data_normalizer.run(
                user_query=state.user_query,
                eventic_graph=state.eventic_graph,
                summary_base=state.summary_base
            )
            
            # 更新状态
            state.data_normalizer_output = output
            
            # 保存输出到文件
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write("=== 数据规范化Agent输出 ===\n")
                f.write(f"输出类型: {type(output)}\n")
                f.write(f"输出内容: {output}\n")
                if hasattr(output, 'model_dump'):
                    f.write(f"输出字典: {output.model_dump()}\n")
                elif hasattr(output, 'dict'):
                    f.write(f"输出字典: {output.dict()}\n")
                f.write("==============================\n\n")
            
            # 详细日志输出
            logger.info("=== 数据规范化Agent输出 ===")
            logger.info(f"输出类型: {type(output)}")
            logger.info(f"输出内容: {output}")
            if hasattr(output, 'model_dump'):
                logger.info(f"输出字典: {output.model_dump()}")
            elif hasattr(output, 'dict'):
                logger.info(f"输出字典: {output.dict()}")
            logger.info("================================")
            
            logger.info("数据规范化Agent运行完成")
            return state
            
        except Exception as e:
            logger.error(f"数据规范化Agent运行失败: {e}")
            state.errors.append(f"数据规范化失败: {str(e)}")
            return state
    
    async def _run_requirement_analyzer(self, state: AgentState) -> AgentState:
        """运行需求分析Agent"""
        try:
            logger.info("开始运行需求分析Agent...")
            
            output = self.requirement_analyzer.run(
                user_query=state.user_query,
                eventic_graph=state.eventic_graph,
                summary_base=state.summary_base
            )
            
            # 更新状态
            state.requirement_analyzer_output = output
            
            # 保存输出到文件
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write("=== 需求分析Agent输出 ===\n")
                f.write(f"输出类型: {type(output)}\n")
                f.write(f"输出内容: {output}\n")
                if hasattr(output, 'model_dump'):
                    f.write(f"输出字典: {output.model_dump()}\n")
                elif hasattr(output, 'dict'):
                    f.write(f"输出字典: {output.dict()}\n")
                f.write("==============================\n\n")
            
            # 详细日志输出
            logger.info("=== 需求分析Agent输出 ===")
            logger.info(f"输出类型: {type(output)}")
            logger.info(f"输出内容: {output}")
            if hasattr(output, 'model_dump'):
                logger.info(f"输出字典: {output.model_dump()}")
            elif hasattr(output, 'dict'):
                logger.info(f"输出字典: {output.dict()}")
            logger.info("================================")
            
            logger.info("需求分析Agent运行完成")
            return state
            
        except Exception as e:
            logger.error(f"需求分析Agent运行失败: {e}")
            state.errors.append(f"需求分析失败: {str(e)}")
            return state
    
    async def _run_product_transformer(self, state: AgentState) -> AgentState:
        """运行产品转换Agent"""
        try:
            logger.info("开始运行产品转换Agent...")
            
            # 获取数据规范化输出
            if not state.data_normalizer_output:
                raise ValueError("数据规范化输出未准备好")
            
            output = self.product_transformer.run(
                user_query=state.user_query,
                eventic_graph=state.eventic_graph,
                summary_base=state.summary_base,
                normalized_data=state.data_normalizer_output.normalizedData,
                product_id_map=state.data_normalizer_output.productIdMap,
                common_attributes=state.data_normalizer_output.commonAttributes
            )
            
            # 更新状态
            state.product_transformer_output = output
            
            # 保存输出到文件
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write("=== 产品转换Agent输出 ===\n")
                f.write(f"输出类型: {type(output)}\n")
                f.write(f"输出内容: {output}\n")
                if hasattr(output, 'model_dump'):
                    f.write(f"输出字典: {output.model_dump()}\n")
                elif hasattr(output, 'dict'):
                    f.write(f"输出字典: {output.dict()}\n")
                f.write("==============================\n\n")
            
            # 详细日志输出
            logger.info("=== 产品转换Agent输出 ===")
            logger.info(f"输出类型: {type(output)}")
            logger.info(f"输出内容: {output}")
            if hasattr(output, 'model_dump'):
                logger.info(f"输出字典: {output.model_dump()}")
            elif hasattr(output, 'dict'):
                logger.info(f"输出字典: {output.dict()}")
            logger.info("================================")
            
            logger.info("产品转换Agent运行完成")
            return state
            
        except Exception as e:
            logger.error(f"产品转换Agent运行失败: {e}")
            state.errors.append(f"产品转换失败: {str(e)}")
            return state
    
    async def _run_scoring_calculator(self, state: AgentState) -> AgentState:
        """运行评分计算Agent"""
        try:
            logger.info("开始运行评分计算Agent...")
            
            # 获取前面的输出
            if not state.requirement_analyzer_output or not state.product_transformer_output:
                raise ValueError("前面的Agent输出未准备好")
            
            output = self.scoring_calculator.run(
                user_query=state.user_query,
                eventic_graph=state.eventic_graph,
                summary_base=state.summary_base,
                products=state.product_transformer_output.products,
                decision_factors=state.requirement_analyzer_output.decisionFactors
            )
            
            # 更新状态
            state.scoring_calculator_output = output
            
            # 保存输出到文件
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write("=== 评分计算Agent输出 ===\n")
                f.write(f"输出类型: {type(output)}\n")
                f.write(f"输出内容: {output}\n")
                if hasattr(output, 'model_dump'):
                    f.write(f"输出字典: {output.model_dump()}\n")
                elif hasattr(output, 'dict'):
                    f.write(f"输出字典: {output.dict()}\n")
                f.write("==============================\n\n")
            
            # 详细日志输出
            logger.info("=== 评分计算Agent输出 ===")
            logger.info(f"输出类型: {type(output)}")
            logger.info(f"输出内容: {output}")
            if hasattr(output, 'model_dump'):
                logger.info(f"输出字典: {output.model_dump()}")
            elif hasattr(output, 'dict'):
                logger.info(f"输出字典: {output.dict()}")
            logger.info("================================")
            
            logger.info("评分计算Agent运行完成")
            return state
            
        except Exception as e:
            logger.error(f"评分计算Agent运行失败: {e}")
            state.errors.append(f"评分计算失败: {str(e)}")
            return state
    
    async def _run_scenario_matcher(self, state: AgentState) -> AgentState:
        """运行场景匹配Agent"""
        try:
            logger.info("开始运行场景匹配Agent...")
            
            # 获取前面的输出 - 放宽检查条件
            if not state.product_transformer_output:
                raise ValueError("产品转换Agent输出未准备好")
            
            # 即使其他输出为空，也尝试运行场景匹配
            output = self.scenario_matcher.run(
                user_query=state.user_query,
                eventic_graph=state.eventic_graph,
                summary_base=state.summary_base,
                products=state.product_transformer_output.products,
                scoring_results=state.scoring_calculator_output.scoringResults if state.scoring_calculator_output else {},
                charts=state.scoring_calculator_output.charts if state.scoring_calculator_output else []
            )
            
            # 更新状态
            state.scenario_matcher_output = output
            
            # 保存输出到文件
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write("=== 场景匹配Agent输出 ===\n")
                f.write(f"输出类型: {type(output)}\n")
                f.write(f"输出内容: {output}\n")
                if hasattr(output, 'model_dump'):
                    f.write(f"输出字典: {output.model_dump()}\n")
                elif hasattr(output, 'dict'):
                    f.write(f"输出字典: {output.dict()}\n")
                f.write("==============================\n\n")
            
            # 详细日志输出
            logger.info("=== 场景匹配Agent输出 ===")
            logger.info(f"输出类型: {type(output)}")
            logger.info(f"输出内容: {output}")
            if hasattr(output, 'model_dump'):
                logger.info(f"输出字典: {output.model_dump()}")
            elif hasattr(output, 'dict'):
                logger.info(f"输出字典: {output.dict()}")
            logger.info("================================")
            
            logger.info("场景匹配Agent运行完成")
            return state
            
        except Exception as e:
            logger.error(f"场景匹配Agent运行失败: {e}")
            state.errors.append(f"场景匹配失败: {str(e)}")
            # 即使失败，也创建一个默认输出
            from models import ScenarioMatcherOutput, Scenario, Recommendation, Elimination, Badge, BadgeTone
            default_output = ScenarioMatcherOutput(
                scenarios=[
                    Scenario(
                        icon="fa-exclamation-triangle",
                        title="场景分析失败",
                        bullets=["由于技术原因，场景分析暂时不可用", "请参考产品对比数据进行决策"]
                    )
                ],
                recommendations=[
                    Recommendation(
                        title="基础推荐",
                        badge=Badge(text="待完善", tone=BadgeTone.WARNING, icon="fa-clock"),
                        productId="",
                        fit="推荐方案正在生成中",
                        reasons=["系统正在处理"],
                        tradeoffs=["需要等待完整分析"]
                    )
                ],
                elimination=[
                    Elimination(
                        title="分析状态",
                        level="处理中",
                        icon="fa-spinner",
                        bullets=["场景分析功能暂时不可用", "建议查看产品对比数据"]
                    )
                ]
            )
            state.scenario_matcher_output = default_output
            return state
    
    async def _run_report_assembler(self, state: AgentState) -> AgentState:
        """运行报告组装Agent"""
        try:
            logger.info("开始运行报告组装Agent...")
            
            # 获取所有前面的输出 - 放宽检查条件
            if not state.product_transformer_output:
                raise ValueError("产品转换Agent输出未准备好")
            
            # 构建输入数据，处理可能为空的输出
            input_data = {
                "user_query": state.user_query,
                "eventic_graph": state.eventic_graph,
                "summary_base": state.summary_base,
                "data_normalizer_output": state.data_normalizer_output.model_dump() if state.data_normalizer_output else {},
                "requirement_analyzer_output": state.requirement_analyzer_output.model_dump() if state.requirement_analyzer_output else {},
                "product_transformer_output": state.product_transformer_output.model_dump(),
                "scoring_calculator_output": state.scoring_calculator_output.model_dump() if state.scoring_calculator_output else {},
                "scenario_matcher_output": state.scenario_matcher_output.model_dump() if state.scenario_matcher_output else {}
            }
            
            output = self.report_assembler.run(**input_data)
            
            # 更新状态
            state.report_assembler_output = output
            state.final_report_data = output.reportData
            
            # 保存输出到文件
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write("=== 报告组装Agent输出 ===\n")
                f.write(f"输出类型: {type(output)}\n")
                f.write(f"输出内容: {output}\n")
                if hasattr(output, 'model_dump'):
                    f.write(f"输出字典: {output.model_dump()}\n")
                elif hasattr(output, 'dict'):
                    f.write(f"输出字典: {output.dict()}\n")
                f.write("==============================\n\n")
            
            # 详细日志输出
            logger.info("=== 报告组装Agent输出 ===")
            logger.info(f"输出类型: {type(output)}")
            logger.info(f"输出内容: {output}")
            if hasattr(output, 'model_dump'):
                logger.info(f"输出字典: {output.model_dump()}")
            elif hasattr(output, 'dict'):
                logger.info(f"输出字典: {output.dict()}")
            logger.info("================================")
            
            logger.info("报告组装Agent运行完成")
            return state
            
        except Exception as e:
            logger.error(f"报告组装Agent运行失败: {e}")
            state.errors.append(f"报告组装失败: {str(e)}")
            # 即使失败，也尝试创建一个基础报告
            try:
                from models import ReportAssemblerOutput, ReportData, Hero, GraphInsights, DecisionFactor, Table
                from models import Badge, BadgeTone
                
                # 创建基础报告数据
                basic_report = ReportData(
                    meta={
                        "title": "基础商品推荐报告",
                        "description": "基于可用数据的推荐分析",
                        "keywords": "商品推荐,基础分析"
                    },
                    nav=[
                        {"title": "产品对比", "href": "#products"},
                        {"title": "基础推荐", "href": "#recommendations"}
                    ],
                    hero=Hero(
                        title="基础商品推荐报告",
                        subtitle="基于可用数据生成的基础推荐",
                        chips=[
                            {"text": "基础推荐", "color": "info"},
                            {"text": "数据有限", "color": "warning"}
                        ],
                        stats=[
                            {"label": "分析产品", "value": str(len(state.product_transformer_output.products)) if state.product_transformer_output else "0"},
                            {"label": "推荐状态", "value": "基础版"},
                            {"label": "完整度", "value": "70%"}
                        ]
                    ),
                    graphInsights=GraphInsights(
                        dimensions=[
                            {"icon": "fa-info-circle", "title": "基础分析", "description": "基于可用数据进行基础推荐分析"}
                        ]
                    ),
                    decisionFactors=[
                        DecisionFactor(icon="fa-cog", title="核心功能", description="产品主要功能的实现程度"),
                        DecisionFactor(icon="fa-star", title="品质水平", description="产品的整体质量水平"),
                        DecisionFactor(icon="fa-coins", title="性价比", description="价格与配置的平衡关系")
                    ],
                    products=state.product_transformer_output.products if state.product_transformer_output else [],
                    charts=[],
                    table=Table(
                        title="产品对比表",
                        notes=["数据来源于可用信息"],
                        columns=["产品名称", "价格", "核心特性"]
                    ),
                    scenarios=[],
                    elimination=[],
                    recommendations=[]
                )
                
                basic_output = ReportAssemblerOutput(reportData=basic_report)
                state.report_assembler_output = basic_output
                state.final_report_data = basic_report
                
                logger.info("创建了基础报告作为备用")
                return state
                
            except Exception as fallback_error:
                logger.error(f"创建备用报告也失败: {fallback_error}")
                state.errors.append(f"备用报告创建失败: {str(fallback_error)}")
                return state
    
    async def generate_report(self, user_query: str, eventic_graph: str, summary_base: str) -> Dict[str, Any]:
        """
        生成完整的推荐报告
        
        Args:
            user_query: 用户查询
            eventic_graph: 事理图谱
            summary_base: 基础数据
            
        Returns:
            完整的报告数据
        """
        try:
            logger.info("开始生成推荐报告...")
            
            # 清空test.txt文件，准备记录新的输出
            with open("test.txt", "w", encoding="utf-8") as f:
                f.write("=== 泛商品推荐报告生成系统 - 完整运行日志 ===\n")
                f.write(f"开始时间: {asyncio.get_event_loop().time()}\n")
                f.write(f"用户查询: {user_query[:100]}...\n")
                f.write(f"事理图谱: {eventic_graph[:100]}...\n")
                f.write(f"基础数据: {summary_base[:100]}...\n")
                f.write("=" * 80 + "\n\n")
            
            # 创建初始状态
            initial_state = AgentState(
                user_query=user_query,
                eventic_graph=eventic_graph,
                summary_base=summary_base
            )
            
            # 运行图，提供checkpointer配置
            config = {"configurable": {"thread_id": "default"}}
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # 检查返回的状态类型
            if isinstance(final_state, AgentState):
                # 如果返回的是AgentState对象
                if final_state.errors:
                    logger.warning(f"报告生成过程中存在错误: {final_state.errors}")
                
                # 返回最终结果
                if final_state.final_report_data:
                    logger.info("推荐报告生成完成")
                    
                    # 保存最终结果到文件
                    with open("test.txt", "a", encoding="utf-8") as f:
                        f.write("=== 最终结果 ===\n")
                        f.write(f"返回类型: AgentState\n")
                        f.write(f"最终报告数据: {final_state.final_report_data}\n")
                        f.write(f"错误信息: {final_state.errors}\n")
                        f.write("=" * 80 + "\n")
                    
                    if hasattr(final_state.final_report_data, 'model_dump'):
                        return final_state.final_report_data.model_dump()
                    else:
                        return final_state.final_report_data.dict()
                else:
                    logger.error("报告生成失败，未获得最终数据")
                    
                    # 保存错误信息到文件
                    with open("test.txt", "a", encoding="utf-8") as f:
                        f.write("=== 错误信息 ===\n")
                        f.write("报告生成失败，未获得最终数据\n")
                        f.write(f"状态内容: {final_state}\n")
                        f.write("=" * 80 + "\n")
                    
                    return {"error": "报告生成失败，未获得最终数据"}
            elif isinstance(final_state, dict):
                # 如果返回的是字典，从中提取最终报告数据
                logger.info("从字典格式中提取最终报告数据")
                
                # 保存字典状态到文件
                with open("test.txt", "a", encoding="utf-8") as f:
                    f.write("=== 返回状态分析 ===\n")
                    f.write(f"返回类型: dict\n")
                    f.write(f"字典键: {list(final_state.keys())}\n")
                    f.write(f"字典内容: {final_state}\n")
                    f.write("=" * 80 + "\n")
                
                # 检查是否有最终报告数据
                if "final_report_data" in final_state and final_state["final_report_data"]:
                    logger.info("成功提取最终报告数据")
                    
                    # 保存成功信息到文件
                    with open("test.txt", "a", encoding="utf-8") as f:
                        f.write("=== 成功提取 ===\n")
                        f.write("从final_report_data字段成功提取报告数据\n")
                        f.write("=" * 80 + "\n")
                    
                    return final_state["final_report_data"]
                elif "report_assembler_output" in final_state and final_state["report_assembler_output"]:
                    # 如果有报告组装输出，从中提取报告数据
                    report_output = final_state["report_assembler_output"]
                    if isinstance(report_output, dict) and "reportData" in report_output:
                        logger.info("从报告组装输出中提取报告数据")
                        
                        # 保存成功信息到文件
                        with open("test.txt", "a", encoding="utf-8") as f:
                            f.write("=== 成功提取 ===\n")
                            f.write("从report_assembler_output.reportData字段成功提取报告数据\n")
                            f.write("=" * 80 + "\n")
                        
                        return report_output["reportData"]
                    elif hasattr(report_output, 'reportData'):
                        logger.info("从报告组装输出对象中提取报告数据")
                        
                        # 保存成功信息到文件
                        with open("test.txt", "a", encoding="utf-8") as f:
                            f.write("=== 成功提取 ===\n")
                            f.write("从report_assembler_output.reportData对象成功提取报告数据\n")
                            f.write("=" * 80 + "\n")
                        
                        if hasattr(report_output.reportData, 'model_dump'):
                            return report_output.reportData.model_dump()
                        else:
                            return report_output.reportData.dict()
                
                # 如果都没有，返回错误
                logger.warning(f"返回了意外的字典格式: {final_state}")
                
                # 保存错误信息到文件
                with open("test.txt", "a", encoding="utf-8") as f:
                    f.write("=== 错误信息 ===\n")
                    f.write("返回了意外的字典格式，无法提取报告数据\n")
                    f.write(f"字典内容: {final_state}\n")
                    f.write("=" * 80 + "\n")
                
                return {"error": "报告生成失败，返回格式异常"}
            else:
                # 如果返回的是其他类型
                logger.warning(f"返回的状态类型异常: {type(final_state)}")
                
                # 保存错误信息到文件
                with open("test.txt", "a", encoding="utf-8") as f:
                    f.write("=== 错误信息 ===\n")
                    f.write(f"返回的状态类型异常: {type(final_state)}\n")
                    f.write(f"状态内容: {final_state}\n")
                    f.write("=" * 80 + "\n")
                
                return {"error": "报告生成失败，状态对象异常"}
                
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            
            # 保存异常信息到文件
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write("=== 异常信息 ===\n")
                f.write(f"报告生成过程中发生异常: {str(e)}\n")
                f.write("=" * 80 + "\n")
            
            return {"error": f"报告生成失败: {str(e)}"}

def main():
    """主函数"""
    # 从constant.py导入示例数据
    from constant import USER_QUERY, EVENTIC_GRAPH, SUMMARY_BASE
    
    async def run_example():
        """运行示例"""
        generator = ReportGenerator()
        
        # 生成报告
        result = await generator.generate_report(
            user_query=USER_QUERY,
            eventic_graph=EVENTIC_GRAPH,
            summary_base=SUMMARY_BASE
        )
        
        # 输出结果
        if "error" not in result:
            print("报告生成成功！")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 保存到文件
            with open("generated_report.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("报告已保存到 generated_report.json")
        else:
            print(f"报告生成失败: {result['error']}")
    
    # 运行示例
    asyncio.run(run_example())

if __name__ == "__main__":
    main() 