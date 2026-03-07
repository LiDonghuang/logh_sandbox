# Sandbox Governance Canonical v1.0

**Status: Frozen / Authoritative**\
**Scope: 银河战场 Sandbox 全部后续演化**

------------------------------------------------------------------------

# I. 唯一锚点原则（Single Anchor Principle）

Archetype 的**最新版**是唯一理论锚点。

1.  Archetype 十维参数定义不可修改。
2.  Archetype 语义不可重解释。
3.  Sandbox 不得新增人格维度。
4.  Sandbox 不得重命名十维参数。
5.  任何版本演化均以"最新版 Archetype"为唯一理论源。

依赖关系必须保持：

Archetype → Sandbox（单向依赖）

严禁：

Sandbox → 修改 Archetype

------------------------------------------------------------------------

# II. 参数映射强制原则（Mandatory Mapping Principle）

任何新增机制必须回答：

> 该机制由哪一个 Archetype 参数控制？

若无法明确映射到十维之一：

→ 不允许加入。

映射必须是：

-   单向
-   可解释
-   可追溯

允许：

-   一个参数影响多个机制

禁止：

-   一个机制无参数来源

------------------------------------------------------------------------

# III. 派生变量规则（Derived Variable Rule）

Sandbox 内部变量必须分为两类：

## A. 原始参数（仅十维）

-   只读
-   不可扩展

## B. 派生变量

必须满足：

DerivedVariable = f(ArchetypeParameters, BattleState)

例如：

-   Cohesion
-   Breakthrough Window
-   Threat Level
-   Guard Behavior

不得存在：

未由十维驱动的独立人格变量。

------------------------------------------------------------------------

# IV. 结构闭合点冻结机制（Structural Freeze Trigger）

当出现以下任一情况时：

1.  新变量加入
2.  新触发逻辑加入
3.  新公式加入
4.  参数语义改变
5.  层级结构改变

必须暂停并生成：

-   Canonical Snapshot
-   版本号
-   变更说明
-   冻结声明

未经 Snapshot，不得继续扩展。

------------------------------------------------------------------------

# V. 层级隔离原则（Layer Isolation）

正式定义三层：

## Layer A --- Canonical Theory

最新版 Archetype\
不可修改。

## Layer B --- Parameter Mapping Layer

定义：

十维参数 → Sandbox 行为函数

此层允许修改，但必须生成版本号。

## Layer C --- Engine Layer

-   火力
-   Cohesion
-   Supply
-   Breakthrough
-   Seed
-   报告

Engine 只读 Mapping 层。

------------------------------------------------------------------------

# VI. 反向修正禁止原则（No Reverse Adjustment）

战斗结果：

-   不得用于修改 Archetype
-   不得用于修改十维定义

若发现结果异常：

只能：

-   调整 Mapping 层
-   或修正 Engine 实现错误

------------------------------------------------------------------------

# VII. LLM 行为约束（Prompt Governance Clause）

今后所有 Sandbox 相关线程应加入：

This thread operates under Archetype-Aligned Governance Mode.\
Latest Archetype version is the only anchor.\
All new mechanics must map to one of the ten parameters.\
Assistant must warn at structural closure points.\
No reverse adjustment allowed.

若违反，助手必须主动警告。

------------------------------------------------------------------------

# VIII. 冻结声明

Sandbox Governance Canonical v1.0\
Frozen / Authoritative\
Archetype-Aligned Development Required
