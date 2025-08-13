"""
演示脚本 - 展示泛商品推荐报告生成系统的使用方法
"""
import asyncio
import json
from pathlib import Path
from main import ReportGenerator
from html_renderer import HTMLRenderer

async def demo_basic_usage():
    """演示基本使用方法"""
    print("=== 泛商品推荐报告生成系统演示 ===\n")
    
    # 1. 创建报告生成器
    print("1. 创建报告生成器...")
    try:
        generator = ReportGenerator()
        print("✓ 报告生成器创建成功")
    except Exception as e:
        print(f"✗ 报告生成器创建失败: {e}")
        return
    
    # 2. 准备示例数据
    print("\n2. 准备示例数据...")
    from constant import USER_QUERY, EVENTIC_GRAPH, SUMMARY_BASE
    
    print(f"用户查询: {USER_QUERY[:100]}...")
    print(f"事理图谱: {EVENTIC_GRAPH[:100]}...")
    print(f"基础数据: {SUMMARY_BASE[:100]}...")
    print("✓ 示例数据准备完成")
    
    # 3. 生成报告
    print("\n3. 生成推荐报告...")
    try:
        result = await generator.generate_report(
            user_query=USER_QUERY,
            eventic_graph=EVENTIC_GRAPH,
            summary_base=SUMMARY_BASE
        )
        
        if "error" in result:
            print(f"✗ 报告生成失败: {result['error']}")
            return
        
        print("✓ 推荐报告生成成功！")
        
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")
        return
    
    # 4. 保存JSON结果
    print("\n4. 保存JSON结果...")
    try:
        with open("demo_report.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("✓ JSON结果已保存到 demo_report.json")
    except Exception as e:
        print(f"✗ JSON保存失败: {e}")
    
    # 5. 生成HTML报告
    print("\n5. 生成HTML报告...")
    try:
        renderer = HTMLRenderer("template.html")
        html_content = renderer.render(result)
        
        with open("demo_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✓ HTML报告已保存到 demo_report.html")
        
    except Exception as e:
        print(f"✗ HTML生成失败: {e}")
    
    # 6. 显示报告摘要
    print("\n6. 报告摘要...")
    try:
        print(f"报告标题: {result.get('meta', {}).get('title', '未知')}")
        print(f"产品数量: {len(result.get('products', []))}")
        print(f"图表数量: {len(result.get('charts', []))}")
        print(f"推荐数量: {len(result.get('recommendations', []))}")
        
        # 显示产品列表
        if result.get('products'):
            print("\n产品列表:")
            for i, product in enumerate(result['products'][:3]):  # 只显示前3个
                print(f"  {i+1}. {product.get('name', 'Unknown')} - ¥{product.get('price', 'Unknown')}")
        
        # 显示推荐
        if result.get('recommendations'):
            print("\n推荐方案:")
            for i, rec in enumerate(result['recommendations']):
                print(f"  {i+1}. {rec.get('title', 'Unknown')} - {rec.get('fit', 'Unknown')}")
                
    except Exception as e:
        print(f"✗ 报告摘要显示失败: {e}")
    
    print("\n=== 演示完成 ===")
    print("生成的文件:")
    print("- demo_report.json: 结构化报告数据")
    print("- demo_report.html: 可视化HTML报告")

async def demo_custom_data():
    """演示使用自定义数据"""
    print("\n=== 自定义数据演示 ===\n")
    
    # 自定义用户查询
    custom_query = """
    请为我推荐一款笔记本电脑：主要用于办公和轻度设计工作，预算8000元以内，
    需要15寸以上屏幕，内存16GB以上，硬盘512GB以上，品牌偏好联想、华为、戴尔。
    """
    
    # 自定义事理图谱
    custom_graph = """
    # 笔记本电脑购买决策事理图谱
    
    ```mermaid
    graph TD
    A[需求分析] --> B[品牌选择]
    A --> C[配置要求]
    A --> D[预算控制]
    B --> E[产品筛选]
    C --> E
    D --> E
    E --> F[对比分析]
    F --> G[最终决策]
    ```
    """
    
    # 自定义产品数据
    custom_products = """
    {
      "联想ThinkBook 15": {
        "核心参数": {
          "屏幕": "15.6寸",
          "处理器": "Intel i5-1240P",
          "内存": "16GB",
          "硬盘": "512GB SSD",
          "价格": "6999"
        },
        "优势": ["商务外观", "接口丰富", "散热良好"],
        "劣势": ["屏幕色域一般", "重量较重"]
      },
      "华为MateBook D15": {
        "核心参数": {
          "屏幕": "15.6寸",
          "处理器": "AMD R5-5500U",
          "内存": "16GB",
          "硬盘": "512GB SSD",
          "价格": "6499"
        },
        "优势": ["轻薄设计", "长续航", "华为生态"],
        "劣势": ["接口较少", "扩展性有限"]
      }
    }
    """
    
    print("使用自定义数据生成报告...")
    
    try:
        generator = ReportGenerator()
        result = await generator.generate_report(
            user_query=custom_query,
            eventic_graph=custom_graph,
            summary_base=custom_products
        )
        
        if "error" not in result:
            print("✓ 自定义数据报告生成成功！")
            
            # 保存结果
            with open("custom_demo_report.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("✓ 自定义报告已保存到 custom_demo_report.json")
            
        else:
            print(f"✗ 自定义数据报告生成失败: {result['error']}")
            
    except Exception as e:
        print(f"✗ 自定义数据演示失败: {e}")

async def main():
    """主函数"""
    # 基本使用演示
    await demo_basic_usage()
    
    # 自定义数据演示
    await demo_custom_data()
    
    print("\n=== 所有演示完成 ===")
    print("您可以查看生成的文件来了解系统的输出效果")

if __name__ == "__main__":
    asyncio.run(main()) 