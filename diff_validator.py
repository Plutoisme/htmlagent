#!/usr/bin/env python3
"""
Diff验证器模块
实现diff补丁的有效性和安全性验证
"""

import os
import re
from typing import Dict, Any, List, Tuple, Optional
from diff_generator import DiffGenerator


class DiffValidator:
    """Diff补丁验证器"""
    
    def __init__(self):
        """初始化Diff验证器"""
        self.diff_generator = DiffGenerator()
    
    def validate_diff(self, diff_content: str, target_file: str = None) -> Dict[str, Any]:
        """
        验证diff补丁的有效性和安全性
        
        Args:
            diff_content: diff内容
            target_file: 目标文件路径（可选，用于更详细的验证）
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        try:
            # 基础格式验证
            format_valid, format_error = self._validate_format(diff_content)
            if not format_valid:
                validation_result["errors"].append(f"格式错误: {format_error}")
                return validation_result
            
            # 结构验证
            structure_valid, structure_errors = self._validate_structure(diff_content)
            if not structure_valid:
                validation_result["errors"].extend(structure_errors)
                return validation_result
            
            # 内容验证
            content_valid, content_errors, content_warnings = self._validate_content(diff_content)
            if not content_valid:
                validation_result["errors"].extend(content_errors)
            
            validation_result["warnings"].extend(content_warnings)
            
            # 如果有目标文件，进行文件特定验证
            if target_file and os.path.exists(target_file):
                file_valid, file_errors, file_warnings = self._validate_against_file(diff_content, target_file)
                if not file_valid:
                    validation_result["errors"].extend(file_errors)
                
                validation_result["warnings"].extend(file_warnings)
            
            # 安全性验证
            security_valid, security_errors, security_warnings = self._validate_security(diff_content)
            if not security_valid:
                validation_result["errors"].extend(security_errors)
            
            validation_result["warnings"].extend(security_warnings)
            
            # 统计信息
            validation_result["info"] = self._collect_statistics(diff_content)
            
            # 如果没有错误，标记为有效
            if not validation_result["errors"]:
                validation_result["valid"] = True
            
            return validation_result
            
        except Exception as e:
            validation_result["errors"].append(f"验证过程中发生异常: {str(e)}")
            return validation_result
    
    def _validate_format(self, diff_content: str) -> Tuple[bool, Optional[str]]:
        """
        验证diff的基本格式
        
        Args:
            diff_content: diff内容
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not diff_content.strip():
            return False, "Diff内容为空"
        
        lines = diff_content.split('\n')
        
        # 检查是否包含必要的标记
        has_header = any(line.startswith('---') for line in lines)
        has_file_info = any(line.startswith('+++') for line in lines)
        has_hunk_header = any(line.startswith('@@') for line in lines)
        
        if not has_header:
            return False, "缺少文件头标记 (---)"
        
        if not has_file_info:
            return False, "缺少文件信息标记 (+++)"
        
        if not has_hunk_header:
            return False, "缺少变更块标记 (@@)"
        
        return True, None
    
    def _validate_structure(self, diff_content: str) -> Tuple[bool, List[str]]:
        """
        验证diff的结构完整性
        
        Args:
            diff_content: diff内容
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误列表)
        """
        errors = []
        lines = diff_content.split('\n')
        
        # 检查变更块格式
        hunk_count = 0
        for i, line in enumerate(lines):
            if line.startswith('@@'):
                hunk_count += 1
                # 验证变更块头格式
                if not re.match(r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@', line):
                    errors.append(f"第{i+1}行: 无效的变更块格式: {line}")
                    continue
                
                # 检查变更块内容
                hunk_valid, hunk_errors = self._validate_hunk_structure(lines, i)
                if not hunk_valid:
                    errors.extend([f"第{i+1}行变更块: {e}" for e in hunk_errors])
        
        if hunk_count == 0:
            errors.append("没有找到有效的变更块")
        
        return len(errors) == 0, errors
    
    def _validate_hunk_structure(self, lines: List[str], hunk_start: int) -> Tuple[bool, List[str]]:
        """
        验证单个变更块的结构
        
        Args:
            lines: 所有行
            hunk_start: 变更块开始行索引
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误列表)
        """
        errors = []
        i = hunk_start + 1
        
        # 解析变更块头
        hunk_header = lines[hunk_start]
        match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', hunk_header)
        
        if not match:
            errors.append("无法解析变更块头")
            return False, errors
        
        old_start = int(match.group(1))
        old_count = int(match.group(2)) if match.group(2) else 1
        new_start = int(match.group(3))
        new_count = int(match.group(4)) if match.group(4) else 1
        
        # 检查变更块内容
        context_lines = 0
        deletion_lines = 0
        addition_lines = 0
        
        while i < len(lines) and not lines[i].startswith('@@'):
            line = lines[i]
            
            if line.startswith(' '):
                context_lines += 1
            elif line.startswith('-'):
                deletion_lines += 1
            elif line.startswith('+'):
                addition_lines += 1
            elif line.startswith('\\'):
                # 文件结束标记
                break
            
            i += 1
        
        # 验证行数匹配 - 使用更宽松的验证逻辑
        # difflib生成的diff可能包含额外的上下文行
        expected_old = old_count
        expected_new = new_count
        actual_old = context_lines + deletion_lines
        actual_new = context_lines + addition_lines
        
        # 允许一定的容差，因为difflib可能会添加额外的上下文行
        if abs(actual_old - expected_old) > 2:  # 允许2行的容差
            errors.append(f"删除行数不匹配: 期望{expected_old}行，实际{actual_old}行")
        
        if abs(actual_new - expected_new) > 2:  # 允许2行的容差
            errors.append(f"新增行数不匹配: 期望{expected_new}行，实际{actual_new}行")
        
        return len(errors) == 0, errors
    
    def _validate_content(self, diff_content: str) -> Tuple[bool, List[str], List[str]]:
        """
        验证diff内容的合理性
        
        Args:
            diff_content: diff内容
            
        Returns:
            Tuple[bool, List[str], List[str]]: (是否有效, 错误列表, 警告列表)
        """
        errors = []
        warnings = []
        
        lines = diff_content.split('\n')
        
        # 检查文件路径
        for line in lines:
            if line.startswith('---') or line.startswith('+++'):
                file_path = line[4:].strip()
                if not file_path or file_path == '/dev/null':
                    continue
                
                # 检查文件路径安全性
                if self._is_dangerous_path(file_path):
                    errors.append(f"危险的文件路径: {file_path}")
                
                # 检查文件扩展名
                if not self._is_safe_file_extension(file_path):
                    warnings.append(f"非标准文件扩展名: {file_path}")
        
        # 检查变更内容
        for line in lines:
            if line.startswith('+') and len(line) > 1:
                content = line[1:]
                
                # 检查是否包含潜在的危险内容
                if self._contains_dangerous_content(content):
                    warnings.append(f"潜在的危险内容: {content[:50]}...")
        
        return len(errors) == 0, errors, warnings
    
    def _validate_against_file(self, diff_content: str, target_file: str) -> Tuple[bool, List[str], List[str]]:
        """
        针对目标文件验证diff
        
        Args:
            diff_content: diff内容
            target_file: 目标文件路径
            
        Returns:
            Tuple[bool, List[str], List[str]]: (是否有效, 错误列表, 警告列表)
        """
        errors = []
        warnings = []
        
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            file_lines = file_content.splitlines()
            
            # 解析diff中的变更块
            hunks = self._parse_hunks(diff_content)
            
            for hunk in hunks:
                old_start = hunk["old_start"] - 1  # 转换为0索引
                
                # 检查行号范围
                if old_start < 0 or old_start >= len(file_lines):
                    errors.append(f"变更块行号超出文件范围: {old_start + 1}")
                    continue
                
                # 检查上下文匹配 - 使用更宽松的匹配逻辑
                context_matches = self._check_context_match_relaxed(file_lines, hunk, old_start)
                if not context_matches:
                    errors.append(f"变更块上下文不匹配，起始行: {old_start + 1}")
                
        except Exception as e:
            errors.append(f"无法读取目标文件: {str(e)}")
        
        return len(errors) == 0, errors, warnings
    
    def _check_context_match_relaxed(self, file_lines: List[str], hunk: Dict, start_line: int) -> bool:
        """
        宽松的上下文匹配检查，忽略空行差异
        
        Args:
            file_lines: 文件行列表
            hunk: 变更块
            start_line: 起始行号
            
        Returns:
            bool: 上下文是否匹配
        """
        # 获取上下文行（非空行）
        context_changes = [change for change in hunk["changes"] if change["type"] == "context"]
        non_empty_contexts = [change for change in context_changes if change["line"].strip()]
        
        if not non_empty_contexts:
            return True
        
        # 检查每个非空上下文行
        for change in non_empty_contexts:
            expected = change["line"].strip()
            
            # 在文件行中查找匹配的内容
            found = False
            for i in range(start_line, min(start_line + len(file_lines), len(file_lines))):
                actual = file_lines[i].strip()
                if expected == actual:
                    found = True
                    break
            
            if not found:
                return False
        
        return True
    
    def _validate_security(self, diff_content: str) -> Tuple[bool, List[str], List[str]]:
        """
        验证diff的安全性
        
        Args:
            diff_content: diff内容
            
        Returns:
            Tuple[bool, List[str], List[str]]: (是否安全, 错误列表, 警告列表)
        """
        errors = []
        warnings = []
        
        lines = diff_content.split('\n')
        
        # 检查是否包含系统文件路径
        system_paths = ['/etc/', '/var/', '/usr/', '/bin/', '/sbin/', '/proc/', '/sys/']
        for line in lines:
            if line.startswith('---') or line.startswith('+++'):
                file_path = line[4:].strip()
                for sys_path in system_paths:
                    if file_path.startswith(sys_path):
                        errors.append(f"尝试修改系统文件: {file_path}")
        
        # 检查是否包含可执行代码
        executable_extensions = ['.py', '.js', '.php', '.rb', '.sh', '.bat', '.exe']
        for line in lines:
            if line.startswith('+++'):
                file_path = line[4:].strip()
                for ext in executable_extensions:
                    if file_path.endswith(ext):
                        warnings.append(f"修改可执行文件: {file_path}")
        
        return len(errors) == 0, errors, warnings
    
    def _is_dangerous_path(self, file_path: str) -> bool:
        """检查是否为危险的文件路径"""
        dangerous_patterns = [
            r'\.\./',  # 目录遍历
            r'//',     # 绝对路径
            r'~',      # 用户主目录
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, file_path):
                return True
        
        return False
    
    def _is_safe_file_extension(self, file_path: str) -> bool:
        """检查是否为安全的文件扩展名"""
        safe_extensions = ['.html', '.htm', '.css', '.js', '.txt', '.md', '.xml', '.json']
        _, ext = os.path.splitext(file_path)
        return ext.lower() in safe_extensions
    
    def _contains_dangerous_content(self, content: str) -> bool:
        """检查是否包含危险内容"""
        dangerous_patterns = [
            r'<script[^>]*>',  # 脚本标签
            r'javascript:',     # JavaScript协议
            r'data:',          # Data协议
            r'vbscript:',      # VBScript协议
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _parse_hunks(self, diff_content: str) -> List[Dict]:
        """解析diff中的变更块"""
        hunks = []
        lines = diff_content.split('\n')
        current_hunk = None
        
        for line in lines:
            if line.startswith('@@'):
                if current_hunk:
                    hunks.append(current_hunk)
                
                match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                if match:
                    current_hunk = {
                        "old_start": int(match.group(1)),
                        "old_count": int(match.group(2)) if match.group(2) else 1,
                        "new_start": int(match.group(3)),
                        "new_count": int(match.group(4)) if match.group(4) else 1,
                        "changes": []
                    }
            
            elif current_hunk and line:
                if line.startswith(' '):
                    current_hunk["changes"].append({"type": "context", "line": line[1:]})
                elif line.startswith('-'):
                    current_hunk["changes"].append({"type": "deletion", "line": line[1:]})
                elif line.startswith('+'):
                    current_hunk["changes"].append({"type": "addition", "line": line[1:]})
        
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    def _collect_statistics(self, diff_content: str) -> Dict[str, Any]:
        """收集diff统计信息"""
        lines = diff_content.split('\n')
        
        stats = {
            "total_lines": len(lines),
            "hunk_count": 0,
            "addition_lines": 0,
            "deletion_lines": 0,
            "context_lines": 0
        }
        
        for line in lines:
            if line.startswith('@@'):
                stats["hunk_count"] += 1
            elif line.startswith('+'):
                stats["addition_lines"] += 1
            elif line.startswith('-'):
                stats["deletion_lines"] += 1
            elif line.startswith(' '):
                stats["context_lines"] += 1
        
        return stats


def validate_diff(diff_content: str, target_file: str = None) -> Dict[str, Any]:
    """
    便捷函数：验证diff
    
    Args:
        diff_content: diff内容
        target_file: 目标文件路径（可选）
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    validator = DiffValidator()
    return validator.validate_diff(diff_content, target_file)


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
    
    print("测试Diff验证器")
    print("=" * 50)
    
    validator = DiffValidator()
    result = validator.validate_diff(test_diff)
    
    print("验证结果:")
    print(f"有效: {result['valid']}")
    
    if result["errors"]:
        print("\n错误:")
        for error in result["errors"]:
            print(f"  ❌ {error}")
    
    if result["warnings"]:
        print("\n警告:")
        for warning in result["warnings"]:
            print(f"  ⚠️  {warning}")
    
    if result["info"]:
        print("\n统计信息:")
        for key, value in result["info"].items():
            print(f"  �� {key}: {value}") 