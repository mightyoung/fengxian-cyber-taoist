# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

FengxianCyberTaoist is a dual-system AI platform combining:
1. **Swarm Intelligence Engine** - Agent-based social media simulation for predicting real-world outcomes
2. **紫微斗数 (Purple Star Astrology) Divination System** - Multi-agent LLM-powered astrology analysis

## Commands

```bash
# Install dependencies
npm run setup:all          # Install root + frontend + backend (creates venv with uv)

# Development
npm run dev                 # Run both frontend and backend concurrently
npm run backend             # Flask API on http://localhost:5001
npm run frontend            # Next.js app on http://localhost:3000

# Build
npm run build               # Build frontend for production

# Backend tests
cd backend && uv run pytest                          # All tests
cd backend && uv run pytest tests/unit/              # Unit tests only
cd backend && uv run pytest tests/e2e/                # E2E tests only
cd backend && uv run pytest -m "not slow"             # Skip slow tests
cd backend && uv run pytest tests/e2e/test_divination_flows.py  # Single file

# Frontend lint
cd frontend && npm run lint

# Docker
docker compose up -d        # Ports: 3000 (frontend), 5001 (backend)
```

## Architecture

### Two Core Systems

**1. Swarm Intelligence Engine** (Original pipeline):

```
Step1 (Graph Build) → Step2 (Environment Setup) → Step3 (Simulation) → Step4 (Report) → Step5 (Interaction)
```

**2. 紫微斗数 Divination System** (Multi-agent analysis):
- `chart_agent` - Birth chart generation from birth info
- `star_agent` - Star interpretation across 12 palaces
- `palace_agent` - Palace-level analysis
- `transform_agent` - Four transformations (化禄/化权/化科/化忌) analysis
- `pattern_agent` - Pattern/structure recognition
- `causal_chain_predictor` - Causal chain reasoning with multi-agent consensus
- `synthesis_agent` - Final synthesis of all analyses
- `report_generator` / `report_transformer` - Report generation (professional_plain, xiaohongshu formats)

### Backend Services

| Service | Role |
|---------|------|
| `graph_builder.py` | Builds knowledge graph from seed text using Zep Cloud |
| `simulation_manager.py` | Orchestrates dual-platform (Twitter/Reddit) simulation |
| `divination/` | 紫微斗数 multi-agent analysis system |
| `report_service.py` | Unified report generation with PDF/markdown export |

### Backend API Endpoints

**Swarm Intelligence:**
- `POST /api/graph/build` - Build knowledge graph from text
- `GET /api/graph/{graph_id}` - Get graph info
- `POST /api/simulation/create` - Create simulation from graph
- `POST /api/simulation/{id}/start` - Start simulation
- `GET /api/simulation/{id}/status` - Poll simulation status
- `POST /api/report/generate` - Generate prediction report

**Divination System:**
- `POST /api/divination/chart/generate` - Generate birth chart
- `GET /api/divination/chart/<chart_id>` - Get chart data
- `POST /api/divination/agents/analyze` - Run multi-agent analysis
- `POST /api/divination/report/generate` - Generate divination report
- `POST /api/divination/report/transform` - Transform report style

### Frontend Structure (Next.js 16 + React 19)

**Pages** (`frontend/src/app/`):
- Next.js App Router with page-based routing
- `/birth-chart` - 命盘分析
- `/divination/relationship` - 姻缘分析
- `/report/[id]` - 预测报告详情
- `/simulation/[id]` - 模拟运行详情
- `/chat` - 智能体交互
- `/graph` - 知识图谱

**Components** (`frontend/src/components/`):
- `birth-chart/` - 命盘展示组件
- `divination/` - Divination-specific components (FortuneRadarChart, PalaceStarMap, etc.)
- `graph/` - Knowledge graph visualization
- `report/` - Report display components
- `simulation/` - Simulation status and controls
- `ui/` - shadcn/ui components

**Stores** (`frontend/src/stores/`): Zustand for state management

**Hooks** (`frontend/src/hooks/`): Custom React hooks (use-api, use-birth-chart, use-simulation, use-report)

**Contexts** (`frontend/src/contexts/`): React Context providers (AuthContext)

### External Dependencies

- **OASIS** (`camel-oasis`): Agent-based social media simulation
- **Zep Cloud**: Knowledge graph storage and entity memory
- **LLM API**: OpenAI SDK-compatible (tested with Alibaba qwen-plus)

## Environment Variables

```env
LLM_API_KEY=<api_key>
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus
ZEP_API_KEY=<zep_api_key>
```

## Project Structure

```
FengxianCyberTaoist/
├── frontend/               # Next.js 16 (React 19) frontend
│   └── src/
│       ├── app/            # Next.js App Router pages
│       ├── components/     # UI components (birth-chart, divination, graph, report, simulation)
│       ├── contexts/       # React Context (AuthContext)
│       ├── hooks/          # Custom React hooks (use-api, use-auth, use-birth-chart, etc.)
│       ├── stores/         # Zustand state stores
│       └── lib/            # Utilities and config
├── backend/                 # Python Flask backend
│   └── app/
│       ├── api/            # REST endpoints (auth, payments)
│       ├── models/         # Data models (user, divination)
│       ├── services/       # Core business logic
│       │   ├── divination/ # 紫微斗数 multi-agent system
│       │   │   ├── agents/ # Individual agent implementations
│       │   │   └── api/    # Divination API routes
│       │   └── simulation/ # OASIS simulation services
│       └── utils/          # LLM client, file parser, logger, vector_db
├── static/                 # Static assets
└── docker-compose.yml
```
