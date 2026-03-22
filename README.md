
# 凤仙郡赛博道士|fengxian-cyber-taoist
## 天人合一 · 洞悉未来

> *"道生一，一生二，二生三，三生万物。万象皆有数，命运自有定。"*
>
> ——《道德经》

**FengxianCyberTaoist** 是一款融合古老东方智慧与现代人工智能的预测引擎。它以玄学为体、科技为用，将千年命理智慧与多智能体模拟技术完美结合。

### 双系统架构

| 系统 | 描述 |
|------|------|
| **群体智能引擎** | 基于 OASIS 的 agent 社会模拟，从海量信息中推演未来走向 |
| **紫微斗数分析** | 多智能体协同的命理分析，涵盖命盘、四化、因果链、趋避之道 |

> 你只需：上传种子材料或提供出生信息<br/>
> FengxianCyberTaoist 将为你：推演因果，预知吉凶

---

## 紫微斗数 · 命理真言

> 紫微斗数，源于天上星宿，应于人间祸福

除群体智能预测外，系统提供**完整的紫微斗数命理分析**：

- **命盘排布**：星辰定位，宫位流转，揭示先天命格
- **四化飞星**：禄权科忌，推演命势流转
- **因果链推理**：多智能体共识验证，追根溯源
- **多维预测**：事业、财运、感情、健康、人际五大维度
- **趋吉避凶**：基于因果链的风险提示与化解指导
- **双版报告**：专业通俗版、小红书版，随心切换

### 因果链验证机制

```
多智能体共识 → 因果链追溯 → 因忌数计算 → 趋避建议
     ↓              ↓            ↓           ↓
 星辰解读 ← 命盘分析 ← 四化飞星 ← 先天命格
```

---

## 数字沙盘 · 万象推演

**宏观**：政策舆情、金融市场、社会事件——决策者的预演实验室

**微观**：小说结局、人生剧本、创意探索——每个人都是命运的编剧

### 工作流程

```
图谱构建 → 环境搭建 → 模拟推演 → 报告生成 → 深度互动
    ↓           ↓           ↓           ↓           ↓
GraphRAG   Agent人设   OASIS并行   多Agent共识   命运对话
```

---

## 🚀 玄门启动

### 一、源码部署（推荐）

#### 前置要求

| 工具 | 版本 | 说明 | 验证命令 |
|------|------|------|----------|
| **Node.js** | 18+ | 前端运行环境 | `node -v` |
| **Python** | ≥3.11, ≤3.12 | 后端运行环境 | `python --version` |
| **uv** | 最新版 | Python 包管理器 | `uv --version` |

#### 1. 配置玄机

```bash
# 复制灵符（配置文件）
cp .env.example .env

# 编辑 .env，注入你的 API 密钥
```

**必需环境变量：**

```env
# LLM API（支持 OpenAI SDK 格式的任意模型）
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# Zep Cloud（知识图谱）
ZEP_API_KEY=your_zep_api_key
```

#### 2. 灵力灌注

```bash
# 一键安装天地灵气（所有依赖）
npm run setup:all
```

#### 3. 启动法阵

```bash
# 启动前后端服务
npm run dev
```

**服务地址：**
- 前端：`http://localhost:3000`
- 后端 API：`http://localhost:5001`

### 二、Docker 部署

```bash
# 配置环境变量后
docker compose up -d
```

---

## 🔮 紫微斗数 API

### 命盘推演

```bash
# 生成命盘
POST /api/divination/chart/generate
Content-Type: application/json

{
  "birth_info": {
    "name": "张三",
    "gender": "男",
    "birth_date": "1990-08-20",
    "birth_time": "12:00",
    "birth_location": "北京"
  }
}

# 获取命盘
GET /api/divination/chart/<chart_id>
```

### 星辰分析

```bash
# 多维分析
POST /api/divination/agents/analyze
Content-Type: application/json

{
  "chart_id": "uuid",
  "analysis_types": ["stars", "palaces", "transforms", "patterns", "timing"]
}
```

### 报告生成

```bash
# 生成命盘报告
POST /api/divination/report/generate
Content-Type: application/json

{
  "chart": {...},
  "user_name": "张三",
  "year": 2026,
  "report_type": "professional_plain"  # or "xiaohongshu"
}

# 格式转换
POST /api/divination/report/transform
{
  "report_content": "# 命盘分析...",
  "style": "xiaohongshu"
}
```

### 报告类型

| 类型 | 适用场景 |
|------|----------|
| `professional_plain` | 专业通俗版，含完整命盘分析、四化详解、因果链推理、月度运势 |
| `xiaohongshu` | 小红书版，emoji 丰富、标签话题、适合社交媒体传播 |

---

## 🐟 项目起源

**FengxianCyberTaoist** 基于 [MiroFish](https://github.com/666ghj/MiroFish) 改造而来，保留其群体智能模拟核心能力，并新增紫微斗数命理分析系统。

本项目继承 **AGPL-3.0** 开源协议，所有源代码开放共享。

---

## 致谢

本项目的仿真引擎由 **[OASIS](https://github.com/camel-ai/oasis)** 驱动，衷心感谢 CAMEL-AI 团队的开源贡献！

