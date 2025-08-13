"""
系统测试脚本 - 测试整个报告生成系统
"""
import asyncio
import json
import logging
from pathlib import Path
from main import ReportGenerator
from html_renderer import HTMLRenderer
from constant import USER_QUERY, EVENTIC_GRAPH, SUMMARY_BASE

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_system():
    """测试整个系统"""
    try:
        logger.info("开始系统测试...")
        
        # 1. 测试报告生成
        logger.info("1. 测试报告生成...")
        generator = ReportGenerator()
        
        result = await generator.generate_report(
            user_query=USER_QUERY,
            eventic_graph=EVENTIC_GRAPH,
            summary_base=SUMMARY_BASE
        )
        
        if "error" in result:
            logger.error(f"报告生成失败: {result['error']}")
            return False
        
        logger.info("报告生成成功！")
        
        # 2. 保存JSON结果
        logger.info("2. 保存JSON结果...")
        
        # 确保result是字典格式
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
        elif hasattr(result, 'dict'):
            result_dict = result.dict()
        else:
            result_dict = result
            
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        logger.info("JSON结果已保存到 test_report.json")
        
        # 3. 测试HTML渲染
        logger.info("3. 测试HTML渲染...")
        renderer = HTMLRenderer("template.html")
        
        try:
            html_content = renderer.render(result)
            logger.info("HTML渲染成功！")
            
            # 保存HTML文件
            with open("test_report.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("HTML报告已保存到 test_report.html")
            
        except Exception as e:
            logger.error(f"HTML渲染失败: {e}")
            return False
        
        # 4. 验证数据结构
        logger.info("4. 验证数据结构...")
        required_sections = [
            "meta", "nav", "hero", "graphInsights", "decisionFactors",
            "products", "charts", "table", "scenarios", "elimination", "recommendations"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in result:
                missing_sections.append(section)
        
        if missing_sections:
            logger.warning(f"缺少以下部分: {missing_sections}")
        else:
            logger.info("所有必需的数据部分都存在")
        
        # 5. 验证产品数据
        logger.info("5. 验证产品数据...")
        if "products" in result and result["products"]:
            logger.info(f"产品数量: {len(result['products'])}")
            for i, product in enumerate(result["products"]):
                logger.info(f"产品 {i+1}: {product.get('name', 'Unknown')} (ID: {product.get('id', 'Unknown')})")
        else:
            logger.warning("没有产品数据")
        
        # 6. 验证图表配置
        logger.info("6. 验证图表配置...")
        if "charts" in result and result["charts"]:
            logger.info(f"图表数量: {len(result['charts'])}")
            for i, chart in enumerate(result["charts"]):
                logger.info(f"图表 {i+1}: {chart.get('title', 'Unknown')} (类型: {chart.get('type', 'Unknown')})")
        else:
            logger.warning("没有图表配置")
        
        logger.info("系统测试完成！")
        return True
        
    except Exception as e:
        logger.error(f"系统测试失败: {e}")
        return False

def test_individual_agents():
    """测试各个Agent"""
    logger.info("开始测试各个Agent...")
    
    try:
        from llm_client import SiliconFlowClient
        from agents.data_normalizer import DataNormalizerAgent
        from agents.requirement_analyzer import RequirementAnalyzerAgent
        
        # 测试LLM客户端
        logger.info("测试LLM客户端...")
        try:
            client = SiliconFlowClient()
            logger.info("LLM客户端初始化成功")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            return False
        
        # 测试数据规范化Agent
        logger.info("测试数据规范化Agent...")
        try:
            normalizer = DataNormalizerAgent(client)
            logger.info("数据规范化Agent初始化成功")
        except Exception as e:
            logger.error(f"数据规范化Agent初始化失败: {e}")
            return False
        
        # 测试需求分析Agent
        logger.info("测试需求分析Agent...")
        try:
            analyzer = RequirementAnalyzerAgent(client)
            logger.info("需求分析Agent初始化成功")
        except Exception as e:
            logger.error(f"需求分析Agent初始化失败: {e}")
            return False
        
        logger.info("所有Agent初始化成功！")
        return True
        
    except Exception as e:
        logger.error(f"Agent测试失败: {e}")
        return False

async def main():
    """主函数"""
    logger.info("=== 泛商品推荐报告生成系统测试 ===")
    
    # 测试各个Agent
    if not test_individual_agents():
        logger.error("Agent测试失败，退出")
        return
    
    # 测试整个系统
    if not await test_system():
        logger.error("系统测试失败")
        return
    
    logger.info("=== 所有测试通过！系统运行正常 ===")

if __name__ == "__main__":
    asyncio.run(main()) 