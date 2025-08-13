#!/usr/bin/env python3
"""
Diff生成器模块
实现从原始内容到修改后内容的unified diff格式生成
"""

import difflib
from typing import List, Tuple, Optional
import re


class DiffGenerator:
    """Unified Diff生成器"""
    
    def __init__(self, context_lines: int = 3):
        """
        初始化Diff生成器
        
        Args:
            context_lines: 上下文行数，默认为3行
        """
        self.context_lines = context_lines
    
    def generate_unified_diff(self, 
                            original_content: str, 
                            modified_content: str, 
                            file_path: str = "file.html",
                            original_name: str = "a",
                            modified_name: str = "b") -> str:
        """
        生成unified diff格式的补丁
        
        Args:
            original_content: 原始内容
            modified_content: 修改后的内容
            file_path: 文件路径
            original_name: 原始文件标识符
            modified_name: 修改后文件标识符
            
        Returns:
            str: unified diff格式的补丁字符串
        """
        # 标准化内容，去除空行
        original_clean = self._remove_empty_lines(original_content)
        modified_clean = self._remove_empty_lines(modified_content)
        
        # 分割内容为行
        original_lines = original_clean.splitlines(keepends=True)
        modified_lines = modified_clean.splitlines(keepends=True)
        
        # 使用difflib生成unified diff
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"{original_name}/{file_path}",
            tofile=f"{modified_name}/{file_path}",
            lineterm='',
            n=self.context_lines
        )
        
        # 转换为字符串
        diff_content = '\n'.join(diff)
        
        # 如果没有差异，返回空字符串
        if not diff_content.strip():
            return ""
        
        return diff_content
    
    def _remove_empty_lines(self, content: str) -> str:
        """
        去除内容中的空行
        
        Args:
            content: 原始内容
            
        Returns:
            str: 去除空行后的内容
        """
        lines = content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)
    
    def generate_html_specific_diff(self, 
                                  original_content: str, 
                                  modified_content: str, 
                                  file_path: str = "file.html") -> str:
        """
        生成HTML特定的diff，优化HTML标签的显示
        
        Args:
            original_content: 原始HTML内容
            modified_content: 修改后的HTML内容
            file_path: 文件路径
            
        Returns:
            str: HTML优化的unified diff
        """
        # 预处理HTML内容，标准化空白字符
        original_clean = self._normalize_html_content(original_content)
        modified_clean = self._normalize_html_content(modified_content)
        
        # 生成标准diff
        diff_content = self.generate_unified_diff(
            original_clean, 
            modified_clean, 
            file_path
        )
        
        # 如果没有差异，返回空字符串
        if not diff_content.strip():
            return ""
        
        # 后处理diff内容，确保格式一致性
        processed_diff = self._post_process_diff(diff_content, original_clean, modified_clean)
        
        return processed_diff
    
    def _post_process_diff(self, diff_content: str, original_content: str, modified_content: str) -> str:
        """
        后处理diff内容，确保格式一致性
        
        Args:
            diff_content: 原始diff内容
            original_content: 原始内容
            modified_content: 修改后的内容
            
        Returns:
            str: 处理后的diff内容
        """
        lines = diff_content.split('\n')
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.startswith('@@'):
                # 处理变更块头
                processed_lines.append(line)
                i += 1
                
                # 收集变更块内容
                hunk_lines = []
                while i < len(lines) and not lines[i].startswith('@@'):
                    hunk_lines.append(lines[i])
                    i += 1
                
                # 重新计算行数
                corrected_hunk = self._correct_hunk_line_counts(hunk_lines)
                processed_lines.extend(corrected_hunk)
            else:
                processed_lines.append(line)
                i += 1
        
        return '\n'.join(processed_lines)
    
    def _correct_hunk_line_counts(self, hunk_lines: List[str]) -> List[str]:
        """
        修正变更块的行数计算
        
        Args:
            hunk_lines: 变更块行列表
            
        Returns:
            List[str]: 修正后的变更块行列表
        """
        if not hunk_lines:
            return hunk_lines
        
        # 统计各种类型的行数
        context_count = 0
        deletion_count = 0
        addition_count = 0
        
        for line in hunk_lines:
            if line.startswith(' '):
                context_count += 1
            elif line.startswith('-'):
                deletion_count += 1
            elif line.startswith('+'):
                addition_count += 1
        
        # 如果只有上下文行，说明没有实际变更
        if deletion_count == 0 and addition_count == 0:
            return hunk_lines
        
        # 返回原始行（保持difflib的原始格式）
        return hunk_lines
    
    def _normalize_html_content(self, content: str) -> str:
        """
        标准化HTML内容，处理空白字符和换行
        
        Args:
            content: HTML内容
            
        Returns:
            str: 标准化后的内容
        """
        # 标准化换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 分割为行
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            # 去除行首行尾空白
            stripped_line = line.strip()
            if stripped_line:
                # 有内容的行，保持原有缩进
                normalized_lines.append(line)
            # 空行不添加，避免diff中的空行问题
        
        return '\n'.join(normalized_lines)
    
    def create_patch_header(self, file_path: str, description: str = "") -> str:
        """
        创建补丁文件头
        
        Args:
            file_path: 文件路径
            description: 补丁描述
            
        Returns:
            str: 补丁文件头
        """
        header = f"""# HTML修复补丁
# 文件: {file_path}
# 生成时间: {self._get_timestamp()}
"""
        
        if description:
            header += f"# 描述: {description}\n"
        
        header += "#\n"
        return header
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_diff_content(self, diff_content: str) -> Tuple[bool, Optional[str]]:
        """
        验证diff内容的格式是否正确
        
        Args:
            diff_content: diff内容
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not diff_content.strip():
            return True, None
        
        lines = diff_content.split('\n')
        
        # 检查是否包含必要的diff标记
        has_header = any(line.startswith('---') for line in lines)
        has_file_info = any(line.startswith('+++') for line in lines)
        has_hunk_header = any(line.startswith('@@') for line in lines)
        
        if not has_header:
            return False, "缺少文件头标记 (---)"
        
        if not has_file_info:
            return False, "缺少文件信息标记 (+++)"
        
        if not has_hunk_header:
            return False, "缺少变更块标记 (@@)"
        
        # 检查变更块格式
        for line in lines:
            if line.startswith('@@'):
                if not re.match(r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@', line):
                    return False, f"无效的变更块格式: {line}"
        
        return True, None


def generate_unified_diff(original_content: str, 
                         modified_content: str, 
                         file_path: str = "file.html") -> str:
    """
    便捷函数：生成unified diff
    
    Args:
        original_content: 原始内容
        modified_content: 修改后的内容
        file_path: 文件路径
        
    Returns:
        str: unified diff格式的补丁
    """
    generator = DiffGenerator()
    return generator.generate_unified_diff(original_content, modified_content, file_path)


def generate_html_diff(original_content: str, 
                      modified_content: str, 
                      file_path: str = "file.html") -> str:
    """
    便捷函数：生成HTML特定的diff
    
    Args:
        original_content: 原始HTML内容
        modified_content: 修改后的HTML内容
        file_path: 文件路径
        
    Returns:
        str: HTML优化的unified diff
    """
    generator = DiffGenerator()
    return generator.generate_html_specific_diff(original_content, modified_content, file_path)


if __name__ == "__main__":
    # 测试代码
    original = """<div class="container">
    <h1>标题</h1>
    <p>段落内容</p>
</div>"""
    
    modified = """<div class="container">
    <h1>标题</h1>
    <p>段落内容</p>
    <p>新增段落</p>
</div>"""
    
    generator = DiffGenerator()
    diff = generator.generate_html_specific_diff(original, modified, "test.html")
    print("生成的diff:")
    print(diff)
    
    # 验证diff
    is_valid, error = generator.validate_diff_content(diff)
    print(f"\nDiff验证结果: {'有效' if is_valid else f'无效 - {error}'}") 