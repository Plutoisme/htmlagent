#!/usr/bin/env python3
"""
Diff应用器模块
实现unified diff补丁的应用到目标文件
"""

import os
import re
import shutil
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime


class DiffApplier:
    """Unified Diff应用器"""
    
    def __init__(self, backup_dir: str = ".backup"):
        """
        初始化Diff应用器
        
        Args:
            backup_dir: 备份目录
        """
        self.backup_dir = backup_dir
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """确保备份目录存在"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def apply_unified_diff(self, file_path: str, diff_content: str) -> Dict[str, Any]:
        """
        应用unified diff补丁到目标文件
        
        Args:
            file_path: 目标文件路径
            diff_content: unified diff内容
            
        Returns:
            Dict[str, Any]: 应用结果
        """
        try:
            # 验证文件存在
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"目标文件不存在: {file_path}"
                }
            
            # 验证diff内容
            if not diff_content.strip():
                return {
                    "success": False,
                    "error": "Diff内容为空"
                }
            
            # 创建备份
            backup_path = self._create_backup(file_path)
            
            # 解析diff内容
            parsed_diff = self._parse_unified_diff(diff_content)
            if not parsed_diff["valid"]:
                return {
                    "success": False,
                    "error": f"Diff格式无效: {parsed_diff['error']}"
                }
            
            # 读取目标文件
            with open(file_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            # 应用变更
            modified_lines = self._apply_changes(original_lines, parsed_diff["hunks"])
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            
            return {
                "success": True,
                "message": f"成功应用diff到文件: {file_path}",
                "backup_path": backup_path,
                "changes_applied": len(parsed_diff["hunks"]),
                "original_lines": len(original_lines),
                "modified_lines": len(modified_lines)
            }
            
        except Exception as e:
            # 如果失败，尝试回滚
            if 'backup_path' in locals():
                self._rollback_from_backup(file_path, backup_path)
            
            return {
                "success": False,
                "error": f"应用diff失败: {str(e)}",
                "backup_path": backup_path if 'backup_path' in locals() else None
            }
    
    def _create_backup(self, file_path: str) -> str:
        """
        创建文件备份
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 备份文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _parse_unified_diff(self, diff_content: str) -> Dict[str, Any]:
        """
        解析unified diff内容
        
        Args:
            diff_content: diff内容
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        lines = diff_content.split('\n')
        hunks = []
        current_hunk = None
        
        for line in lines:
            # 文件头信息
            if line.startswith('---') or line.startswith('+++'):
                continue
            
            # 变更块头
            elif line.startswith('@@'):
                if current_hunk:
                    hunks.append(current_hunk)
                
                # 解析 @@ -start,count +start,count @@ 格式
                match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2)) if match.group(2) else 1
                    new_start = int(match.group(3))
                    new_count = int(match.group(4)) if match.group(4) else 1
                    
                    current_hunk = {
                        "old_start": old_start,
                        "old_count": old_count,
                        "new_start": new_start,
                        "new_count": new_count,
                        "changes": []
                    }
                else:
                    return {
                        "valid": False,
                        "error": f"无效的变更块头: {line}"
                    }
            
            # 变更内容
            elif current_hunk and line:
                if line.startswith(' '):
                    # 上下文行
                    current_hunk["changes"].append({
                        "type": "context",
                        "line": line[1:],
                        "action": "keep"
                    })
                elif line.startswith('-'):
                    # 删除行
                    current_hunk["changes"].append({
                        "type": "deletion",
                        "line": line[1:],
                        "action": "delete"
                    })
                elif line.startswith('+'):
                    # 新增行
                    current_hunk["changes"].append({
                        "type": "addition",
                        "line": line[1:],
                        "action": "add"
                    })
        
        # 添加最后一个hunk
        if current_hunk:
            hunks.append(current_hunk)
        
        return {
            "valid": True,
            "hunks": hunks
        }
    
    def _validate_context(self, lines: List[str], hunk: Dict, start_line: int) -> bool:
        """
        验证变更块的上下文是否匹配
        
        Args:
            lines: 文件行列表
            hunk: 变更块
            start_line: 起始行号
            
        Returns:
            bool: 上下文是否匹配
        """
        if start_line < 0 or start_line >= len(lines):
            return False
        
        # 检查上下文行
        context_lines = [change for change in hunk["changes"] if change["type"] == "context"]
        
        # 如果没有上下文行，直接返回True（可能是纯新增的变更块）
        if not context_lines:
            return True
        
        # 检查是否有足够的行数
        if start_line + len(context_lines) > len(lines):
            return False
        
        # 使用宽松的上下文匹配，忽略空行差异
        return self._validate_context_relaxed(lines, hunk, start_line)
    
    def _validate_context_relaxed(self, lines: List[str], hunk: Dict, start_line: int) -> bool:
        """
        宽松的上下文匹配验证，忽略空行差异
        
        Args:
            lines: 文件行列表
            hunk: 变更块
            start_line: 起始行号
            
        Returns:
            bool: 上下文是否匹配
        """
        # 获取非空上下文行
        context_changes = [change for change in hunk["changes"] if change["type"] == "context"]
        non_empty_contexts = [change for change in context_changes if change["line"].strip()]
        
        if not non_empty_contexts:
            return True
        
        # 检查每个非空上下文行
        for change in non_empty_contexts:
            expected = change["line"].strip()
            
            # 在文件行中查找匹配的内容
            found = False
            for i in range(start_line, min(start_line + len(lines), len(lines))):
                actual = lines[i].strip()
                if expected == actual:
                    found = True
                    break
            
            if not found:
                return False
        
        return True
    
    def _smart_context_match(self, expected: str, actual: str) -> bool:
        """
        智能上下文匹配，处理HTML中的空白字符差异
        
        Args:
            expected: 期望的内容
            actual: 实际的内容
            
        Returns:
            bool: 是否匹配
        """
        # 标准化空白字符
        expected_norm = ' '.join(expected.split())
        actual_norm = ' '.join(actual.split())
        
        # 如果标准化后匹配，返回True
        if expected_norm == actual_norm:
            return True
        
        # 如果原始内容匹配，返回True
        if expected == actual:
            return True
        
        # 如果去除所有空白后匹配，返回True
        expected_clean = ''.join(expected.split())
        actual_clean = ''.join(actual.split())
        if expected_clean == actual_clean:
            return True
        
        return False
    
    def _apply_changes(self, original_lines: List[str], hunks: List[Dict]) -> List[str]:
        """
        应用变更到原始行列表
        
        Args:
            original_lines: 原始行列表
            hunks: 变更块列表
            
        Returns:
            List[str]: 修改后的行列表
        """
        # 转换为可变列表
        modified_lines = original_lines.copy()
        
        # 按行号排序hunks，从后往前处理，避免行号偏移
        sorted_hunks = sorted(hunks, key=lambda x: x["old_start"], reverse=True)
        
        for hunk in sorted_hunks:
            old_start = hunk["old_start"] - 1  # 转换为0索引
            old_end = old_start + hunk["old_count"]
            
            # 验证上下文匹配
            if not self._validate_context(modified_lines, hunk, old_start):
                raise ValueError(f"上下文不匹配，无法应用变更块: {hunk}")
            
            # 应用变更
            new_lines = []
            for change in hunk["changes"]:
                if change["action"] == "keep":
                    # 保持原有行，确保有换行符
                    line_content = change["line"]
                    if not line_content.endswith('\n'):
                        line_content += '\n'
                    new_lines.append(line_content)
                elif change["action"] == "delete":
                    # 跳过删除的行
                    continue
                elif change["action"] == "add":
                    # 新增行，确保有换行符
                    line_content = change["line"]
                    if not line_content.endswith('\n'):
                        line_content += '\n'
                    new_lines.append(line_content)
            
            # 替换原内容
            modified_lines[old_start:old_end] = new_lines
        
        return modified_lines
    
    def _rollback_from_backup(self, file_path: str, backup_path: str):
        """
        从备份恢复文件
        
        Args:
            file_path: 目标文件路径
            backup_path: 备份文件路径
        """
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
        except Exception as e:
            # 记录回滚失败，但不抛出异常
            print(f"警告：回滚失败: {str(e)}")
    
    def rollback_changes(self, file_path: str, backup_path: str) -> bool:
        """
        回滚文件到备份状态
        
        Args:
            file_path: 文件路径
            backup_path: 备份文件路径
            
        Returns:
            bool: 回滚是否成功
        """
        try:
            if not os.path.exists(backup_path):
                return False
            
            shutil.copy2(backup_path, file_path)
            return True
            
        except Exception as e:
            print(f"回滚失败: {str(e)}")
            return False
    
    def list_backups(self, file_path: str = None) -> List[Dict[str, Any]]:
        """
        列出备份文件
        
        Args:
            file_path: 特定文件的备份（可选）
            
        Returns:
            List[Dict[str, Any]]: 备份文件列表
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.bak'):
                backup_path = os.path.join(self.backup_dir, filename)
                stat = os.stat(backup_path)
                
                backup_info = {
                    "filename": filename,
                    "path": backup_path,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                }
                
                # 如果指定了文件，只返回该文件的备份
                if file_path:
                    if filename.startswith(os.path.basename(file_path)):
                        backups.append(backup_info)
                else:
                    backups.append(backup_info)
        
        # 按创建时间排序
        backups.sort(key=lambda x: x["created"], reverse=True)
        return backups


def apply_unified_diff(file_path: str, diff_content: str) -> Dict[str, Any]:
    """
    便捷函数：应用unified diff
    
    Args:
        file_path: 目标文件路径
        diff_content: diff内容
        
    Returns:
        Dict[str, Any]: 应用结果
    """
    applier = DiffApplier()
    return applier.apply_unified_diff(file_path, diff_content)


def rollback_changes(file_path: str, backup_path: str) -> bool:
    """
    便捷函数：回滚文件
    
    Args:
        file_path: 文件路径
        backup_path: 备份文件路径
        
    Returns:
        bool: 回滚是否成功
    """
    applier = DiffApplier()
    return applier.rollback_changes(file_path, backup_path)


if __name__ == "__main__":
    # 测试代码
    test_diff = """--- a/test.html
+++ b/test.html
@@ -1,3 +1,4 @@
 <div class="container">
     <h1>标题</h1>
     <p>段落内容</p>
+    <p>新增段落</p>
 </div>"""
    
    # 创建测试文件
    test_content = """<div class="container">
    <h1>标题</h1>
    <p>段落内容</p>
</div>"""
    
    with open("test.html", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("原始文件内容:")
    print(test_content)
    print("\n" + "="*50)
    
    # 应用diff
    applier = DiffApplier()
    result = applier.apply_unified_diff("test.html", test_diff)
    
    print("应用结果:")
    print(result)
    
    if result["success"]:
        print("\n修改后的文件内容:")
        with open("test.html", "r", encoding="utf-8") as f:
            print(f.read())
    
    # 清理测试文件
    if os.path.exists("test.html"):
        os.remove("test.html") 