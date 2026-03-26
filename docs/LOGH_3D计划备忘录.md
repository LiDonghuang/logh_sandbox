# Minimal 2D 阵型规范 v0.1（已修正；仅含2D字段，3D扩展备忘）

## 执行摘要

本报告定义了**更正后的 Minimal 2D Formation Specs v0.1**，明确其为**仅含2D字段**的接口草案，但保留面向未来3D扩展的设计意图。主要特点包括：  
- **ObjectiveLocationSpec**：只包含 `anchor_point`（目标位置）、`forward_hint`（前进方向提示）、`source_owner`（目标所有者）和 `no_enemy_semantics`（无敌情境标记），严格区分“去哪”与“怎么摆”。  
- **FormationFrameSpec/LayoutSpec/SpacingSpec/ReferenceMappingPolicy**：定义舰队局部坐标系、阵型布局和期望间距，均不含 `z` 或 `vertical` 字段。我们在规范中增加了明确的3D扩展说明（如主轴尺度、坐标系构造规则、退化处理策略等），为后续3D支持留下接口。  
- **映射与分层**：保留当前引擎的分离设计——formation spec 仅负责单位对齐到参考槽位，不做最终合法性投影（min-spacing）解算。最终合规由现有 `engine_skeleton.py` 的分离层完成。  
- **运动机制映射**：FR 参数将不再直接放大质心吸引，而仅放大“期望位置修正”力；ODW/PD/stray等原有运动层特征被剥离到高层或诊断层；TL 逻辑不变；FSR 保留为独立的预投影修正层。  
- **限制条件**：不授权任何3D运行时实现；不授权重新定义目标含义；不授权大范围运动重写或基线替换；仅允许在中立过渡场景下设计验证（符合v4b Candidate A 边界）。  
- **推进路径**：按阶段推进——**设计阶段**(纯规格说明，不动代码) → **试验阶段**(仅在 `neutral_transit` fixture 中消费此接口) → **可选推广**(验证无误后再向正式 runtime 尝试小范围集成)。  

下文详细列出了各规格字段、3D注释、与仓库代码的映射对照、数据流示意、测试矩阵与验收标准、推荐交付物等。所有方案建议均基于主线设计文档和现有 repo 约定。  

---

## ObjectiveLocationSpec v0.1

**定义：** ObjectiveLocationSpec 提供最小的目标描述，只回答“舰队向何处前进”，不包含完整阵型姿态语义。  

- `anchor_point` (`vec2`, 必需)：目标位置坐标。  
- `forward_hint` (`vec2`, 必需)：前进方向提示（如从质心到目标点的单位向量）。**仅2D**，不应被解释为完整3D朝向。  
- `source_owner` (enum, 必需)：目标的创建者（如 “fixture” 或 “TL”）。用以区分目标来源，避免运动层自行生成目标。  
- `no_enemy_semantics` (enum, 必需)：无敌情境下敌方项为零的语义标记。用于修正无敌时“敌人吸引”退向自心的BUG。  

**所有权边界：** 由 Fixture 或 TL 在上层产生目标，移动层仅接收并使用，不自行修改。一般中立过渡由 Fixture 提供上述字段，战役层逻辑（TL/PD）在其他机制中处理。

**示例 API（**模块/类名未定**）：**  
```python
def resolve_objective_location_v0_1(battle_state: "BattleState", fleet_id: int,
                                    fixture_cfg: dict=None, tl_context: object=None) -> ObjectiveLocationSpec2D:
    """返回 anchor_point, forward_hint, source_owner, no_enemy_semantics"""
```

**示例 JSON/YAML（2D，省略z）：**  
```json
{
  "objective_location": {
    "anchor_point": [350.0, 350.0],
    "forward_hint": [0.7071, 0.7071],
    "source_owner": "fixture",
    "no_enemy_semantics": "enemy_term_zero"
  }
}
```  
```yaml
objective_location:
  anchor_point: [350.0, 350.0]
  forward_hint: [0.7071, 0.7071]
  source_owner: fixture
  no_enemy_semantics: enemy_term_zero
```

---

## FormationSpec v0.1

FormationSpecv0.1 包括舰队局部坐标系定义、阵型布局、期望间距以及单位映射策略，见下表。

### FormationFrameSpec v0.1（舰队坐标系）

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| `anchor_mode` | enum | 是 | 原点定位模式。v0.1保留为 `fleet_centroid`，即以舰队质心为参照点。 |
| `primary_axis_source` | enum | 是 | 主轴来源。对应 Objective 的 `forward_hint`，定义舰队“前方”方向。 |
| `secondary_axis_rule` | enum | 是 | 次轴规则。2D情形下取与主轴垂直方向，避免使用全局上/下轴。 |
| `frame_handedness` | enum | 是 | 帧的手性（如 `right_handed`），确保左右翼定义稳定。 |
| `degeneracy_policy` | enum/struct | 是 | 退化情况处理策略（如目标接近质心时的fallback），**v0.1需明确设置**以避免除0和共线问题。 |
| `frame_smoothing` | struct | 否 | 可选的帧平滑参数（如低通滤波），用于抑制抖动，可暂不启用。 |

**3D扩展说明：** 未来3D坐标系应由前进轴、次参考轴和滚转参考共同定义，并设有手性和退化规则。不应再假设“world up”天然存在。

### FormationLayoutSpec v0.1（阵型布局）

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| `layout_family` | enum | 是 | 阵型类型。v0.1设为 `rect_lattice_2d`（矩形格子）。标识2D时的最简阵型。 |
| `aspect_ratio_target` | float | 是 | 宽深比目标值。**仅适用于2D**，表达阵型在主/副轴上的比例倾向。不作为未来3D参数。 |
| `rotation_policy` | enum | 是 | 阵型旋转规则。通常 `align_primary_axis`，使阵型面向主轴方向。 |
| `centering_policy` | enum | 是 | 阵型中心策略，如 `centered_on_centroid`，保证阵型以舰队质心为中心。 |
| `dim_policy` | enum | 是 | 布局维度策略。根据单位数与长宽比自动确定列/行数。 |
| `slot_identity_policy` | enum | 是 | 槽身份策略。v0.1 为 `fixed_initial_order`，保持单位→槽的初始固定映射（禁止换位）。 |

**3D扩展说明：** 未来3D阵型应由三个主轴长度描述（如 `principal_extents_target=(a,b,c)`）或两个独立比例（`anisotropy_ratios`）来参数化，而非2D宽深比。布局类型将升级为如 `rect_prism_lattice`（体积格子）。

### FormationSpacingSpec v0.1（期望间距）

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| `expected_axis_spacings_xy` | `vec2` | 是 | 沿主轴（x）和次轴（y）的期望单位间距。仅表达阵型意图密度，*不负责实际最小间距碰撞*。 |
| `spacing_mode` | enum | 是 | 间距模式。v0.1 可选 `uniform`（各向同性）以简化。 |
| `slot_fill_order` | enum | 是 | 空位填充顺序。决定槽遍历顺序（如主轴优先），保持确定性。 |

**说明：** “vertical_spacing” 字段被弃用。3D中“vertical”不再作为先验轴，spacing 应只针对主轴坐标系。

### FormationReferenceMappingPolicy v0.1

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| `mapping_mode` | enum | 是 | 单位→槽映射模式。常见做法：按序号顺序映射。 |
| `allow_reflow` | bool | 是 | 是否允许重排单元到不同槽位。v0.1 固定 `false`，禁止自动换位和角色变更。 |
| `debug_emit_expected_positions` | bool | 否 | 调试用：输出每帧计算的期望位置，用于误差分析。 |

**说明：** 本策略只定义槽位参考，**不包括**最终的最小间距调整（后者由分离层负责实现）。

---

## 机制映射与分层（FR/ODW/PD/TL/stray/FSR）

- **FR（Formation Rigidity）**：在现有实现中，FR 参数仍放大质心牵引。新方案中，FR仅用作“向期望位置恢复”的增益因子——即保留参数但与质心脱钩，专门作用于修正位移。  
- **ODW（Optimal Defect Warping）**：当前运动层修改平行项。v0.1中不再在运动代码里硬编码ODW效果，而是考虑作为高层编队输入（脱离运动层）。  
- **PD（Postural Directives）**：对接上层态势接口，当前未深入实施；保留其高层意义，不注入低层。  
- **TL（Tactical Layer）**：TL继续负责战役模式下的目标和策略决策，不在本规范中修改。  
- **Stray（偏航吸引）**：原系统有基于单位间位置偏移的隐含吸引机制。v0.1将其切除，不作为动作指令，仅供分析之用。  
- **FSR（Formation Spread/Rewrite）**：保留为独立的舰队级位置重写步骤，不纳入formation spec，本规范不影响其实现。

**理由：** 以上分层映射严格遵循“解耦低层运动与高层编队”原则。只保留必要的参数并明晰其作用域。

---

## 非授权项（Governance Guardrails）

- **无3D运行时**：v0.1接口仅为2D验证设计，禁止任何z轴或3D计算。  
- **无基线替换**：`v3a`基线保持不变，`v4a`作为实验容器。  
- **无运动重写**：禁止在运动层重新引入MB/ODW/stray等隐藏逻辑。  
- **无隐式槽变换**：禁止单位在运行时自动换位或分配新角色。  
- **禁止新增低层控制**：玩家或TL指令禁止下放到单舰/实时微操，仅限高层决策。  
- **保持分层**：FormationSpec 不得负责法向投影解算，映射和投影必须分离。

以上保证本方案严格在已授权的**测试路径**内进行，不导致现有功能的暗中更改。

---

## 演进路径

1. **设计阶段（纯文档）**：新增ObjectiveLocationSpec2D和FormationSpec2D类型说明，写入分析文档，不修改运行时代码。  
2. **Fixture验证阶段**：在中立过渡测试中使用新接口——计算期望位置（Expected Positions）替代质心目标，使FR驱动恢复；Battle模式保持原状。  
3. **可选集成阶段**：在fixture验证成功后，再行讨论将必要的FormationSpec字段加入正式运行时状态（FleetState），同时确保与TL/PD接口兼容。  

此路线符合之前关于Candidate A的要求，只在无害范围内引入变化。

---

## 规范字段 vs 现有代码映射表

| 规范字段                         | 现有代码对应                         | 说明               |
|----------------------------------|-------------------------------------|--------------------|
| **Objective anchor_point, forward_hint**  | Fixture注入 (test_run_execution.py) | 输入来自测试框架；实际名称 **UNSPECIFIED**。 |
| **Objective source_owner, no_enemy_semantics** | Fixture逻辑设置                     | `source_owner=fixture`、`no_enemy_semantics`由测试框架传递。 |
| **Frame anchor_mode=centroid**        | engine_skeleton 中质心定义 | 用舰队质心（unit 坐标均值）作为框架原点。 |
| **Frame primary_axis=forward_hint**   | engine_skeleton 中的目标方向处理 | 使用目标方向影响运动；新方案将其提炼为坐标系前向轴。 |
| **Frame degeneracy_policy**         | 无现有支持                          | 需新增，用于前向轴退化情况处理。 |
| **Layout family=rect_lattice_2d**   | 初始阵型隐含矩形格局              | v0.1明确表式为2D矩形阵型族。 |
| **Layout aspect_ratio_target**      | 由初始单位排布隐含              | 2D占位字段（UNSPECIFIED默认）。 |
| **Layout rotation_policy, centering**| 隐式按目标和质心对齐            | v0.1强制将其纳入显式设置。 |
| **Slot identity=fixed_initial_order**| 当前按初始顺序排列（隐式）      | Candidate A要求固定，不允许重排。 |
| **Spacing expected_axis_spacings_xy**| 分离层最小间距参数 (engine_skeleton) | 分离出了“预期间距”意图，实际最小间距由Projection层处理。 |
| **Reference mapping_mode**          | 隐式单位顺序映射              | v0.1定义为按序号确定性映射（**UNSPECIFIED**具体方式）。 |
| **Reference allow_reflow=false**    | 当前无换位机制                | 明确禁止运行时重新分配。 |
| **Final Projection (separation)**   | engine_skeleton中同航间距Projection | 保持不变，由原有最小间距求解逻辑完成。 |

---

## 数据流示意图

```mermaid
flowchart LR
  OL[目标位置<br>(Objective Location)] --> FF[阵型坐标系<br>(Formation Frame)]
  FF --> LS[阵型布局/间距<br>(Layout/Spacing)]
  LS --> EP[期望位置<br>(Expected Positions)]
  EP --> MV[移动过程<br>(Movement)]
  MV --> SE[分离层<br>(Separation)]
  SE --> PR[最终投影<br>(Projection)]
```
*注：上图展示数据从Objective→Frame→Layout/Spacing→Expected Positions→Movement→Separation→Projection 的流程。*

---

## 测试矩阵与验收标准

**测试指标**：到达时间、最终半径RMS、平均校正比率、投影对数/最大位移、前沿伸展比等。推荐新指标：**预期位置RMS误差**。  

**优先场景**：  
- **P0. 极远距离中立过渡**（arena=400，[50,50]→[350,350]）：`v3a(post-fix)` vs `v4a` vs `v4a+EP`。验证期望位置修正能显著减少舰队前沿伸展，比值显著下降（参考现 ~5.49）。同时检查投影负担无回弹。  
- **P1. 长对角阵型**（现有fixture案例）：`v3a` vs `v4a` vs `v4a+EP`。保持 `v4a` 先前优化成果（平均校正比率降低，投影配对负担持续减小）。  
- **P2. 短距离/近战情形**：类似参数改变场景，确保近距离追击无过度投影位移。  
- **P3. 阵型比例变化**：不同舰队宽深比场景测试，验证方案适应性。  

**验收条件**：  
1. 与`v4a`后基线相比，P0-P1 的前沿伸展和单位半径指标明显改善；  
2. 投影相关指标（平均校正比、对数/位移）不回退到`v3a`水平；  
3. 无舰队压缩崩溃（RMS半径保持稳定）；  
4. 系统分层无变动：未引入新低层控制或插入逻辑，参考映射与投影求解依旧分离。

---

## 推荐交付物与概要

- `analysis/specs/objective_location_spec_v0_1_2d.md` — ObjectiveLocationSpec 文档  
- `analysis/specs/formation/formation_spec_v0_1_2d_extension_aware.md` — FormationSpec（Frame/Layout/Spacing/ReferenceMapping）文档  
- `analysis/specs/formation/reference_mapping_vs_projection.md` — 参照映射与合法性投影说明  
- `analysis/test_plans/v4b_candidateA_expected_position_matrix.md` — 测试矩阵与指标（v4b候选A）  
- `analysis/engineering_reports/developments/20260322/v4b_fixture_design.md` — 实现边界和设计说明

**15行结构化概要示例**：  
```
引擎版本: v4a + v4b_candidateA_fixture_only（特征）。  
修改层: 仅限 neutral-transit fixture 路径（movement上游）。  
影响参数: FR 用于恢复EP（期望位置），ODW/MB/stray脱耦；TL/PD策略不变。  
新增变量: ObjectiveLocationSpec2D, FormationSpec2D, expected_position_map, expected_position_rms_error。  
跨层耦合: 减少MB/ODW干扰；新增稳定的2D阵型坐标系。  
映射影响: 中立场景用EP替代质心恢复；战役场景不变。  
治理影响: 严格限定v4b候选A；无基线替换；含3D扩展注释。  
向后兼容: 是（默认行为与v4a一致）。  
总结: 实施ObjectiveLocationSpec2D和FormationSpec2D；基于初始舰队构型计算预期位置；使用FR恢复至预期位置；保留分离层投影；通过长距离与长对角场景验证。  
```

---

## 借鉴游戏与视觉风格

为指导设计，本项目参考了多款大规模舰队策略游戏：  
- **《家园》(Homeworld)**：早期3D宇宙舰队视角典范。启示我们舰队不是平面而是具有纵深和体积的编队结构。视角一般采用斜俯视，强调舰队整体形状。  
- **《群星》(Stellaris)**：大规模舰队抽象，展示了高层指挥和慢节奏策略的可能。角色、舰队行为更偏战略与编组，而非微观操控。  
- **《银河英雄传说4/7》**（90年代PC策略游戏）：尽管画面简陋，其体现的“高层指挥”思路与本项目高度契合。强调阵型、站位与执行意图，不追求花哨特效。  

**推荐视觉/交互风格**：采用严肃克制的军事模拟器基调，场景主体为舰队形状和位置关系。界面元素（HUD、选择框等）应简洁实用，避免花里胡哨的赛博风UI或过度即时操作。重点显示：舰队的3D阵型形状、队形深度和指向。色彩上保持冷静（例如蓝/红对比），舰船用光点或简化模型表示。整体风格需有“真实三维战场回放”的感觉，而不是2D棋盘或飞行射击。

---

## Panda3D 集成与开发指南

**引擎选择**：Panda3D 是一款面向 Python 的3D渲染引擎，支持 `pip install panda3d` 直接使用。可用于实时3D可视化和游戏开发。它完全兼容 VS Code 和现有 Python 工作流。  

**文件组织示例**：在项目根目录下新增 `viz3d_panda/` 模块，结构示例如：  
```
viz3d_panda/
  viewer.py          # 继承 ShowBase 的主程序
  assets/            # 3D模型/材质等资源（简化舰船光点或帧模型）
  camera_controller.py  # 摄像机控制逻辑
  controller.py      # 回放时序控制（播放/暂停/快进）
  utils.py           # 场景管理辅助函数
```

**运行时数据映射**：在可视化中，每个 `UnitState`（代表约100艘舰船）映射为舰队的一个可视化实体（可用光点或简易模型表示）。读取 `test_run` 输出的 `position_frames` 逐帧更新各舰队坐标、航迹和目标线。例如：“position_frames[frame][unit_id].pos” 转换为 Panda3D 中的节点位置。舰队阵型（expected positions）可提前计算并存储，用于驱动修正引擎运动。

**可视化规则**：  
- **单位缩放**：由于现实规模巨大，一个单位可视化为百艘舰队符号；可通过颜色/大小区分舰种。  
- **地图比例**：例如 `arena=400` 映射到3D世界的400×400单位；静态深色空间背景，下方界面有控件条。  
- **摄像机视野**：默认斜俯视，支持旋转/缩放。可固定跟随主要舰队或自由移动。  
- **路径绘制**：显示前缀舰队航迹线和当前目标锚点，增强战术可读性。  
- **渲染优化**：简化模型、绘制光点或2D billboards，避免过度渲染细节。

**开发时间预估**：按现有节奏，在VS Code环境中仅做回放功能：约2周实现工作雏形（基本场景+单位显示+摄像机）；4–6周完成稳定版本（航迹、标签、导出等）；约8–10周构建完善的3D回放框架。

**VS Code + Codex 支持**：可直接在 VS Code 中编写Panda3D脚本，无需专用IDE。使用Codex扩展可以辅助生成Panda3D代码。典型流程为：`pip install panda3d` → 在 VS Code 里新建Python文件 → 导入 Panda3D API（如 `from direct.showbase.ShowBase import ShowBase`）→ 运行脚本弹出3D视窗。

**示例启动代码**：  
```python
from direct.showbase.ShowBase import ShowBase
class FleetViewer(ShowBase):
    def __init__(self):
        super().__init__()
        # 在此初始化场景（加载单位标记，设置相机）
app = FleetViewer()
app.run()
```
此脚本即可启动基本3D视图窗口。在VS Code中运行该Python文件，可直接查看3D回放效果。

---

以上建议旨在**在现有架构内**安全实现3D舰队回放验证。它们保留了Current 2D Viewer作为规范观察器的地位，而将3D作为可选侧车（sidecar）实现。该报告和附带文档将有助于Engineering团队在设计、测试和文档方面的下一步工作。