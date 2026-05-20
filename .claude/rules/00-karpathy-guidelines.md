# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes.
Derived from Andrej Karpathy's observations on LLM coding pitfalls.

> 行为准则：用于规避大模型编写代码时常见错误
> 源自 Andrej Karpathy 对 LLM 编码常见坑点总结

---

## 1. Think Before Coding

State your assumptions explicitly. If uncertain, ask.
If multiple interpretations exist, present them - don't pick silently.
If a simpler approach exists, say so. Push back when warranted.
If something is unclear, stop. Name what's confusing. Ask.

> 1. 编码前先思考
>    明确列出所有前提假设，存在不确定点必须主动提问确认。
>    若需求存在多种解读，全部列出，不得私自默认选择一种。
>    如有更简洁可行的实现方案主动说明，不合理需求可适当婉拒。
>    遇到需求模糊不清立刻停止开发，指出疑问点并向用户确认。

---

## 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.
No features beyond what was asked.
No abstractions for single-use code.
No "flexibility" or "configurability" that wasn't requested.
No error handling for impossible scenarios.
If you write 200 lines and it could be 50, rewrite it.
Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

> 2. 简洁至上
>    用最少代码解决当前需求，不写超前、推测性冗余代码。
>    不开发需求以外的额外功能。
>    不为仅单次使用的代码做抽象封装。
>    不私自增加未要求的灵活性、可配置性设计。
>    不为理论上不可能发生的场景做异常捕获处理。
>    能用50行完成就不要写200行，冗余复杂必须精简重写。
>    自我校验：以资深工程师视角判断是否过度复杂，是则立刻简化。

---

## 3. Surgical Changes

Touch only what you must. Clean up only your own mess.
When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.

> 3. 外科手术式最小改动
>    只修改任务必须改动的代码，仅清理自己改动产生的冗余问题。
>    编辑已有代码严格遵守：
>
> - 不顺手优化周边代码、注释、排版格式。
> - 无故障正常运行的代码，不随意重构。
> - 严格沿用项目现有代码风格，即便个人习惯写法不同。

---

## 4. Goal-Driven Execution

Transform tasks into verifiable goals.
Break into small, testable steps.
Loop until verified.

Examples:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan.

> 4. 目标驱动执行
>    将需求转化为可落地、可验证的明确目标。
>    拆解为细小、可独立测试的分步任务。
>    迭代开发直至功能验证通过。
>
> 示例参考：
>
> - 增加数据校验 → 先编写非法输入测试用例，再编码实现通过测试
> - 修复程序Bug → 先编写可复现Bug的测试，再修复代码
> - 重构模块代码 → 保证重构前后测试全部正常通过
>
> 多步骤复杂任务，先输出简要执行计划，再开始编码。
