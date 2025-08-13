# HTML修复Agent - 基于Diff补丁的重构版本

这是一个基于DeepSeek-V3模型的HTML代码修复Agent，采用科学的diff补丁机制实现鲁棒的文件修改控制。

## 🚀 重构目标

从原有的"基于行号字典"的脆弱架构，重构为"基于统一diff补丁"的鲁棒架构，实现：

- 🔍 **上下文感知**：基于内容锚点而非绝对行号进行修改
- 🛠️ **标准diff格式**：使用unified diff格式，支持版本控制和回滚
- 🎯 **精确修改**：通过上下文匹配确保修改的准确性
- 🔄 **原子操作**：支持完整的diff应用，失败时自动回滚

## 🏗️ 新架构设计

### 核心思想：Git-like Diff补丁机制

新架构借鉴Git的diff和patch机制，实现以下核心功能：

1. **`generate_diff`**：生成从原始代码到修复后代码的unified diff
2. **`apply_diff`**：应用diff补丁到目标文件
3. **`validate_diff`**：验证diff补丁的有效性和安全性
4. **`rollback_changes`**：在修改失败时自动回滚

### 架构对比

| 特性 | 旧架构 | 新架构 |
|------|--------|--------|
| 修改方式 | 行号字典 | Unified Diff补丁 |
| 上下文感知 | ❌ 无 | ✅ 基于内容锚点 |
| 版本控制 | ❌ 无 | ✅ 支持diff格式 |
| 回滚机制 | ❌ 无 | ✅ 自动回滚 |
| 错误处理 | 基础 | 详细错误信息 |
| 安全性 | 低 | 高（验证+回滚） |

## 📋 开发阶段规划

### 阶段1：核心Diff工具开发 (Week 1)
- [ ] 实现 `diff_generator.py` - 生成unified diff
- [ ] 实现 `diff_applier.py` - 应用diff补丁
- [ ] 实现 `diff_validator.py` - 验证diff有效性
- [ ] 添加 `unified_diff` 库依赖

### 阶段2：Agent重构 (Week 2)
- [ ] 重构 `HTMLAgent` 类，集成diff工具
- [ ] 更新prompt，支持diff生成
- [ ] 实现新的工作流程：分析 → 生成diff → 应用 → 验证
- [ ] 添加回滚机制

### 阶段3：测试和优化 (Week 3)
- [ ] 编写全面的测试用例
- [ ] 性能优化和错误处理
- [ ] 文档更新和示例完善
- [ ] 集成测试和端到端验证

## 🔧 新的工具集

### 1. Diff生成工具
```python
def generate_unified_diff(original_content: str, modified_content: str, 
                         file_path: str = "file.html") -> str:
    """生成unified diff格式的补丁"""
```

### 2. Diff应用工具
```python
def apply_unified_diff(file_path: str, diff_content: str) -> Dict[str, Any]:
    """应用unified diff补丁到文件"""
```

### 3. Diff验证工具
```python
def validate_diff(diff_content: str, target_file: str) -> Dict[str, Any]:
    """验证diff补丁的有效性和安全性"""
```

### 4. 回滚工具
```python
def rollback_changes(file_path: str, backup_path: str) -> bool:
    """回滚文件到备份状态"""
```

## 🎯 新的工作流程

```
1. 读取原始HTML文件
   ↓
2. Agent分析HTML错误
   ↓
3. 生成修复后的HTML内容
   ↓
4. 生成unified diff补丁
   ↓
5. 验证diff补丁
   ↓
6. 应用diff补丁
   ↓
7. 验证修改结果
   ↓
8. 成功完成或回滚
```

## 📦 新的依赖

```bash
# 新增diff相关依赖
unified-diff>=0.3.0
patch>=1.16.0

# 原有依赖保持不变
openai>=1.0.0
langchain>=0.1.0
langchain-openai>=0.1.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

## 🔄 迁移策略

### 向后兼容
- 保留原有的 `repair_html()` 和 `repair_html_content()` 接口
- 内部实现改为新的diff机制
- 添加新的diff相关方法供高级用户使用

### 渐进式升级
1. **第一阶段**：新架构与旧架构并存
2. **第二阶段**：默认使用新架构，旧架构标记为deprecated
3. **第三阶段**：完全移除旧架构

## 📊 预期改进效果

- **准确性提升**：从90%提升到98%+
- **鲁棒性提升**：支持并发修改和复杂场景
- **可维护性**：标准diff格式，便于调试和版本控制
- **扩展性**：支持其他文件类型的修复

## 🧪 测试策略

### 单元测试
- Diff生成和应用的准确性
- 各种HTML错误类型的修复
- 边界情况和错误处理

### 集成测试
- 端到端的HTML修复流程
- 大文件和复杂HTML的处理
- 并发修改场景

### 回归测试
- 确保新架构不破坏现有功能
- 性能基准测试
- 兼容性验证

---

## 📝 开发日志

### 2024-12-19
- ✅ 完成现有架构分析
- ✅ 设计新架构方案
- ✅ 制定开发阶段规划
- ✅ 完成阶段1开发：核心Diff工具
- ✅ 完成阶段2开发：Agent重构
- ✅ 完成阶段3开发：测试和优化

### 阶段1完成内容 (Week 1)
- ✅ 实现 `diff_generator.py` - 生成unified diff
- ✅ 实现 `diff_applier.py` - 应用diff补丁
- ✅ 实现 `diff_validator.py` - 验证diff有效性
- ✅ 实现 `diff_tools.py` - 整合所有diff功能
- ✅ 添加 `unified-diff` 库依赖

### 阶段2完成内容 (Week 2)
- ✅ 重构 `HTMLAgent` 类，集成diff工具
- ✅ 更新prompt，支持diff生成
- ✅ 实现新的工作流程：分析 → 生成diff → 应用 → 验证
- ✅ 添加回滚机制和备份管理
- ✅ 保持向后兼容性

### 阶段3完成内容 (Week 3)
- ✅ 编写全面的测试用例
- ✅ 性能优化和错误处理
- ✅ 文档更新和示例完善
- ✅ 集成测试和端到端验证
- ✅ 性能基准测试完成

### 🎉 重构完成！
所有三个阶段已全部完成，新架构已成功部署并测试通过！

---

*此README将在重构过程中持续更新，反映最新的架构设计和开发进度。* 