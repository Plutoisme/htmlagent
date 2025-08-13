#!/usr/bin/env python3
"""
修复后的系统测试脚本
"""
import asyncio
import json
import logging
from main import ReportGenerator

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_fixed_system():
    """测试修复后的系统"""
    try:
        logger.info("开始测试修复后的系统...")
        
        # 从constant.py导入示例数据
        from constant import USER_QUERY, EVENTIC_GRAPH, SUMMARY_BASE
        
        # 创建报告生成器
        generator = ReportGenerator()
        
        # 生成报告
        logger.info("开始生成报告...")
        result = await generator.generate_report(
            user_query=USER_QUERY,
            eventic_graph=EVENTIC_GRAPH,
            summary_base=SUMMARY_BASE
        )
        
        # 检查结果
        if "error" not in result:
            logger.info("报告生成成功！")
            
            # 保存到文件
            with open("fixed_report.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info("报告已保存到 fixed_report.json")
            
            # 输出关键信息
            logger.info("=== 报告概览 ===")
            if "meta" in result:
                logger.info(f"标题: {result['meta'].get('title', 'N/A')}")
                logger.info(f"描述: {result['meta'].get('description', 'N/A')}")
            
            if "hero" in result:
                logger.info(f"主标题: {result['hero'].get('title', 'N/A')}")
                logger.info(f"副标题: {result['hero'].get('subtitle', 'N/A')}")
            
            if "products" in result:
                logger.info(f"产品数量: {len(result['products'])}")
                for i, product in enumerate(result['products'][:3]):  # 只显示前3个
                    logger.info(f"产品{i+1}: {product.get('name', 'N/A')} - {product.get('price', 'N/A')}元")
            
            if "scenarios" in result:
                logger.info(f"场景分析数量: {len(result['scenarios'])}")
            
            if "recommendations" in result:
                logger.info(f"推荐方案数量: {len(result['recommendations'])}")
            
            if "elimination" in result:
                logger.info(f"淘汰说明数量: {len(result['elimination'])}")
            
            logger.info("================================")
            
            return True
        else:
            logger.error(f"报告生成失败: {result['error']}")
            return False
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        return False

async def test_individual_agents():
    """测试各个Agent的独立运行"""
    try:
        logger.info("开始测试各个Agent...")
        
        from constant import USER_QUERY, EVENTIC_GRAPH, SUMMARY_BASE
        from llm_client import SiliconFlowClient
        from config import SILICONFLOW_CONFIG
        
        # 初始化LLM客户端
        llm_client = SiliconFlowClient(api_key=SILICONFLOW_CONFIG["api_key"])
        
        # 测试场景匹配Agent
        logger.info("测试场景匹配Agent...")
        from agents.scenario_matcher import ScenarioMatcherAgent
        scenario_agent = ScenarioMatcherAgent(llm_client)
        
        # 创建测试产品数据
        test_products = [
            {
                "id": "test-product-1",
                "name": "测试产品1",
                "price": 1000,
                "type": "测试类型",
                "attributes": {"测试属性": "测试值"}
            }
        ]
        
        test_scoring = {
            "test-product-1": {
                "total": 85,
                "价格": 15,
                "核心性能": 20,
                "品质配置": 25,
                "适用性": 25
            }
        }
        
        test_charts = [
            {
                "id": "test-chart",
                "title": "测试图表",
                "type": "bar",
                "metricKey": "test"
            }
        ]
        
        scenario_output = scenario_agent.run(
            user_query=USER_QUERY,
            eventic_graph=EVENTIC_GRAPH,
            summary_base=SUMMARY_BASE,
            products=test_products,
            scoring_results=test_scoring,
            charts=test_charts
        )
        
        logger.info(f"场景匹配Agent输出: {scenario_output}")
        logger.info(f"场景数量: {len(scenario_output.scenarios)}")
        logger.info(f"推荐数量: {len(scenario_output.recommendations)}")
        logger.info(f"淘汰说明数量: {len(scenario_output.elimination)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Agent测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("=== 修复后的系统测试 ===")
    
    # 测试各个Agent
    logger.info("1. 测试各个Agent...")
    agent_result = asyncio.run(test_individual_agents())
    
    if agent_result:
        logger.info("Agent测试通过")
        
        # 测试完整系统
        logger.info("2. 测试完整系统...")
        system_result = asyncio.run(test_fixed_system())
        
        if system_result:
            logger.info("系统测试通过！")
            logger.info("所有问题已修复，系统运行正常。")
        else:
            logger.error("系统测试失败")
    else:
        logger.error("Agent测试失败")

if __name__ == "__main__":
    main() 