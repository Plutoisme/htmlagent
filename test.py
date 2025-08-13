#!/usr/bin/env python3
"""
HTML修复Agent测试脚本
"""

import os
import time
from htmlagent import HTMLAgent

def create_test_html():
    """创建测试用的HTML文件"""
    test_html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>比亚迪元PLUS 2025款</title>
</head>
<body>
    <div class="container mx-auto p-6">
        <div class="flex items-center mb-6 p-4 bg-blue-50 rounded-lg">
            <div class="flex-shrink-0 mr-4">
                <!-- 问题就在这一行 -->
                <div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16" />
            </div>
            <div>
                <h4 class="font-bold text-lg">比亚迪元PLUS 2025款</h4>
                <p class="text-blue-600 font-medium">14.58万元</p>
            </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h4 class="font-bold mb-2">安全配置</h4>
                <p><span class="font-medium">主动安全：</span>ESP/胎压监测标配</p>
                <p><span class="font-medium">被动安全：</span>4安全气囊</p>
            </div>
            div> <!-- 此处是错误的 -->
                <h4 class="font-bold mb-2">使用成本</h4>
                <p><span class="font-medium">单次充满：</span>参数缺失</p>
                <p><span class="font-medium">百公里电费：</span>约10.32元</p>
                <p><span class="font-medium">口碑：</span>冬季开空调约300km（30%衰减）</p>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    with open('input.html', 'w', encoding='utf-8') as f:
        f.write(test_html_content)
    
    print("✅ 测试HTML文件已创建: input.html")

def main():
    """主测试函数"""
    print("🚀 开始HTML修复Agent测试")
    
    # 检查是否存在input.html，如果不存在则创建
    if not os.path.exists('input.html'):
        print("📝 创建测试HTML文件...")
        create_test_html()
    else:
        print("📄 使用现有的input.html文件")
    
    try:
        # 初始化HTMLAgent
        print("🔧 初始化HTMLAgent...")
        agent = HTMLAgent()
        print("✅ HTMLAgent初始化成功")
        
        # 修复HTML文件
        print("🔍 开始修复HTML文件...")
        
        result = agent.repair_html('input3.html', 'output3.html')
        
        if result["success"]:
            print("✅ HTML修复成功!")
            print(f"📁 输入文件: {result['input_file']}")
            print(f"📁 输出文件: {result['output_file']}")
            
            # 显示计时信息
            if "model_call_time" in result:
                print(f"🤖 大模型调用耗时: {result['model_call_time']:.2f}秒")
            
        else:
            print("❌ HTML修复失败:")
            print(result["error"])
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        print("请检查:")
        print("1. 环境变量SILICONFLOW_API_KEY是否正确设置")
        print("2. 网络连接是否正常")
        print("3. 依赖包是否已安装 (pip install -r requirements.txt)")

if __name__ == "__main__":
    main() 