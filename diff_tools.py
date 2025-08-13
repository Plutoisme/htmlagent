#!/usr/bin/env python3
"""
Diff工具模块
整合所有diff功能，为Agent提供统一的接口
"""

from typing import Dict, Any, Optional
from diff_generator import DiffGenerator, generate_html_diff
from diff_applier import DiffApplier, apply_unified_diff
from diff_validator import DiffValidator, validate_diff


class DiffTools:
    """Diff工具集合"""
    
    def __init__(self, backup_dir: str = ".backup"):
        """
        初始化Diff工具集合
        
        Args:
            backup_dir: 备份目录
        """
        self.generator = DiffGenerator()
        self.applier = DiffApplier(backup_dir)
        self.validator = DiffValidator()
    
    def repair_html_with_diff(self, 
                             file_path: str, 
                             original_content: str, 
                             repaired_content: str,
                             description: str = "HTML修复") -> Dict[str, Any]:
        """
        使用diff机制修复HTML文件
        
        Args:
            file_path: 目标文件路径
            original_content: 原始HTML内容
            repaired_content: 修复后的HTML内容
            description: 修复描述
            
        Returns:
            Dict[str, Any]: 修复结果
        """
        try:
            # 步骤1: 生成diff
            print("🔍 生成HTML修复diff...")
            diff_content = self.generator.generate_html_specific_diff(
                original_content, 
                repaired_content, 
                file_path
            )
            
            if not diff_content.strip():
                return {
                    "success": True,
                    "message": "没有发现需要修复的内容",
                    "diff_content": "",
                    "changes_applied": 0
                }
            
            # 步骤2: 验证diff
            print("✅ 验证diff格式...")
            validation_result = self.validator.validate_diff(diff_content, file_path)
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Diff验证失败: {'; '.join(validation_result['errors'])}",
                    "validation_result": validation_result
                }
            
            # 步骤3: 应用diff
            print("🛠️ 应用diff到文件...")
            apply_result = self.applier.apply_unified_diff(file_path, diff_content)
            
            if not apply_result["success"]:
                return {
                    "success": False,
                    "error": f"应用diff失败: {apply_result['error']}",
                    "apply_result": apply_result
                }
            
            # 步骤4: 返回成功结果
            return {
                "success": True,
                "message": "HTML修复成功",
                "diff_content": diff_content,
                "changes_applied": apply_result["changes_applied"],
                "backup_path": apply_result["backup_path"],
                "validation_result": validation_result,
                "apply_result": apply_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"修复过程中发生异常: {str(e)}"
            }
    
    def generate_repair_diff(self, 
                           original_content: str, 
                           repaired_content: str, 
                           file_path: str = "file.html") -> Dict[str, Any]:
        """
        生成修复diff（不应用）
        
        Args:
            original_content: 原始HTML内容
            repaired_content: 修复后的HTML内容
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: diff生成结果
        """
        try:
            diff_content = self.generator.generate_html_specific_diff(
                original_content, 
                repaired_content, 
                file_path
            )
            
            if not diff_content.strip():
                return {
                    "success": True,
                    "message": "没有发现需要修复的内容",
                    "diff_content": "",
                    "changes_count": 0
                }
            
            # 验证diff
            validation_result = self.validator.validate_diff(diff_content)
            
            return {
                "success": True,
                "message": "Diff生成成功",
                "diff_content": diff_content,
                "validation_result": validation_result,
                "changes_count": validation_result["info"]["hunk_count"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"生成diff失败: {str(e)}"
            }
    
    def apply_diff_patch(self, file_path: str, diff_content: str) -> Dict[str, Any]:
        """
        应用diff补丁到文件
        
        Args:
            file_path: 目标文件路径
            diff_content: diff内容
            
        Returns:
            Dict[str, Any]: 应用结果
        """
        # 先验证
        validation_result = self.validator.validate_diff(diff_content, file_path)
        
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": f"Diff验证失败: {'; '.join(validation_result['errors'])}",
                "validation_result": validation_result
            }
        
        # 再应用
        return self.applier.apply_unified_diff(file_path, diff_content)
    
    def validate_diff_patch(self, diff_content: str, target_file: str = None) -> Dict[str, Any]:
        """
        验证diff补丁
        
        Args:
            diff_content: diff内容
            target_file: 目标文件路径（可选）
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.validator.validate_diff(diff_content, target_file)
    
    def rollback_file(self, file_path: str, backup_path: str) -> bool:
        """
        回滚文件到备份状态
        
        Args:
            file_path: 文件路径
            backup_path: 备份文件路径
            
        Returns:
            bool: 回滚是否成功
        """
        return self.applier.rollback_changes(file_path, backup_path)
    
    def list_backups(self, file_path: str = None) -> list:
        """
        列出备份文件
        
        Args:
            file_path: 特定文件的备份（可选）
            
        Returns:
            list: 备份文件列表
        """
        return self.applier.list_backups(file_path)


# 便捷函数
def repair_html_with_diff(file_path: str, 
                         original_content: str, 
                         repaired_content: str,
                         description: str = "HTML修复") -> Dict[str, Any]:
    """
    便捷函数：使用diff机制修复HTML文件
    """
    tools = DiffTools()
    return tools.repair_html_with_diff(file_path, original_content, repaired_content, description)


def generate_repair_diff(original_content: str, 
                        repaired_content: str, 
                        file_path: str = "file.html") -> Dict[str, Any]:
    """
    便捷函数：生成修复diff
    """
    tools = DiffTools()
    return tools.generate_repair_diff(original_content, repaired_content, file_path)


def apply_diff_patch(file_path: str, diff_content: str) -> Dict[str, Any]:
    """
    便捷函数：应用diff补丁
    """
    tools = DiffTools()
    return tools.apply_diff_patch(file_path, diff_content)


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试Diff工具集合")
    print("=" * 50)
    
    # 测试HTML内容
    original_html = """    <div class="container">
        <h1>标题</h1>
        <p>段落内容</p>
        <div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16" />
    </div>"""
    
    repaired_html = """    <div class="container">
        <h1>标题</h1>
        <p>段落内容</p>
        <div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16"></div>
    </div>"""
    
    # 测试diff生成
    print("1. 测试diff生成...")
    diff_result = generate_repair_diff(original_html, repaired_html, "test.html")
    
    if diff_result["success"]:
        print("✅ Diff生成成功")
        print(f"📊 变更数量: {diff_result['changes_count']}")
        print("\n生成的diff:")
        print(diff_result["diff_content"])
    else:
        print(f"❌ Diff生成失败: {diff_result['error']}")
    
    print("\n" + "=" * 50)
    
    # 测试diff验证
    print("2. 测试diff验证...")
    if diff_result["success"]:
        validation_result = validate_diff(diff_result["diff_content"])
        print(f"✅ Diff验证结果: {'有效' if validation_result['valid'] else '无效'}")
        
        if validation_result["info"]:
            print("📊 统计信息:")
            for key, value in validation_result["info"].items():
                print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # 测试文件修复
    print("3. 测试文件修复...")
    
    # 创建测试文件 - 使用与diff生成时完全相同的原始内容
    with open("test_repair.html", "w", encoding="utf-8") as f:
        f.write(original_html)
    
    print("📄 原始文件内容:")
    print(original_html)
    print("\n" + "-" * 30)
    
    repair_result = repair_html_with_diff("test_repair.html", original_html, repaired_html, "测试修复")
    
    if repair_result["success"]:
        print("✅ HTML修复成功")
        print(f"📊 应用变更: {repair_result['changes_applied']}")
        print(f"💾 备份路径: {repair_result['backup_path']}")
        
        # 显示修复后的内容
        with open("test_repair.html", "r", encoding="utf-8") as f:
            print("\n修复后的内容:")
            print(f.read())
    else:
        print(f"❌ HTML修复失败: {repair_result['error']}")
        
        # 如果失败，显示详细的错误信息
        if "validation_result" in repair_result:
            print("\n详细验证结果:")
            print(repair_result["validation_result"])
    
    # 清理测试文件
    import os
    if os.path.exists("test_repair.html"):
        os.remove("test_repair.html") 