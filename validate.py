#!/usr/bin/env python3
"""
HTML修复Agent验证脚本
"""

import os
import sys
from typing import Dict, Any

def test_imports():
    """测试所有必要的导入"""
    print("🔍 测试导入...")
    
    try:
        from dotenv import load_dotenv
        print("✅ dotenv 导入成功")
    except ImportError as e:
        print(f"❌ dotenv 导入失败: {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✅ openai 导入成功")
    except ImportError as e:
        print(f"❌ openai 导入失败: {e}")
        return False
    
    try:
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        print("✅ langchain.agents 导入成功")
    except ImportError as e:
        print(f"❌ langchain.agents 导入失败: {e}")
        return False
    
    try:
        from langchain_openai import ChatOpenAI
        print("✅ langchain_openai 导入成功")
    except ImportError as e:
        print(f"❌ langchain_openai 导入失败: {e}")
        return False
    
    try:
        from htmlagent import HTMLAgent
        print("✅ HTMLAgent 导入成功")
    except ImportError as e:
        print(f"❌ HTMLAgent 导入失败: {e}")
        return False
    
    return True

def test_tools():
    """测试工具函数"""
    print("\n🔍 测试工具函数...")
    
    try:
        from tools import modify_file_tool
        
        # 创建测试文件
        test_content = "line1\nline2\nline3\n"
        with open('test_validate.html', 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 测试修改
        result = modify_file_tool('test_validate.html', {"2": "modified_line2"})
        
        if result.get("success"):
            print("✅ modify_file_tool 测试成功")
            
            # 清理测试文件
            os.remove('test_validate.html')
            return True
        else:
            print(f"❌ modify_file_tool 测试失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False

def test_agent_initialization():
    """测试Agent初始化"""
    print("\n🔍 测试Agent初始化...")
    
    try:
        from htmlagent import HTMLAgent
        
        # 检查环境变量
        api_key = os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            print("⚠️  SILICONFLOW_API_KEY 未设置，跳过Agent初始化测试")
            return True
        
        # 尝试初始化Agent
        agent = HTMLAgent()
        print("✅ HTMLAgent 初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ HTMLAgent 初始化失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🚀 开始HTML修复Agent验证")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查依赖安装")
        sys.exit(1)
    
    # 测试工具函数
    if not test_tools():
        print("\n❌ 工具函数测试失败")
        sys.exit(1)
    
    # 测试Agent初始化
    if not test_agent_initialization():
        print("\n❌ Agent初始化测试失败")
        sys.exit(1)
    
    print("\n🎉 所有验证通过！")
    print("✅ 项目可以正常使用")

if __name__ == "__main__":
    main() 