# FengxianCyberTaoist (凤仙郡赛博道士) - Project Context

## Project Overview
FengxianCyberTaoist is a dual-system AI platform that combines ancient Eastern wisdom with modern multi-agent simulation. It features two core engines:
1.  **Swarm Intelligence Engine**: An agent-based social media simulation (Twitter/Reddit) using the OASIS framework to predict real-world outcomes and social dynamics.
2.  **紫微斗数 (Purple Star Astrology) Divination System**: A multi-agent LLM-powered system for comprehensive destiny analysis, including chart generation, star interpretation, and causal chain reasoning.

### Core Technologies
-   **Frontend**: Next.js 16 (React 19), Tailwind CSS, shadcn/ui, Zustand (state management).
-   **Backend**: Python 3.11/3.12 (Flask), `uv` (package management), OpenAI SDK (compatible with Qwen, etc.), Zep Cloud (Knowledge Graph), OASIS (Simulation).
-   **Infrastructure**: Redis (caching), PostgreSQL with pgvector (vector storage), S3 (asset storage), Docker.

---

## Building and Running

### Prerequisites
-   **Node.js**: 18+
-   **Python**: 3.11 or 3.12
-   **uv**: Latest version (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Setup and Installation
```bash
# Install all dependencies (Root + Frontend + Backend)
npm run setup:all

# Configure environment variables
cp .env.example .env
# Edit .env with your LLM_API_KEY, ZEP_API_KEY, etc.
```

### Development
```bash
# Run both frontend (port 3000) and backend (port 5001) concurrently
npm run dev

# Run backend only
npm run backend

# Run frontend only
npm run frontend
```

### Testing
```bash
# Run all backend tests
cd backend && uv run pytest

# Run specific test suites
cd backend && uv run pytest tests/unit/
cd backend && uv run pytest tests/e2e/
```

---

## Architecture & Conventions

### Backend Structure (`backend/app/`)
-   **api/**: Flask blueprints for REST endpoints (divination, simulation, graph, etc.).
-   **services/**: Core business logic.
    -   `divination/`: Multi-agent astrology analysis system.
    -   `simulation/`: OASIS-based social simulation orchestrators.
-   **models/**: Data models (SQLAlchemy/Pydantic).
-   **utils/**: Shared utilities (LLM clients, loggers, file parsers).

### Frontend Structure (`frontend/src/`)
-   **app/**: Next.js App Router pages.
-   **components/**: Specialized UI components (birth-chart, divination, graph visualizations).
-   **hooks/**: Custom React hooks for data fetching and state logic.
-   **stores/**: Zustand stores for global application state.

### Multi-Agent Pattern
The divination system uses a specialized multi-agent architecture where individual agents (`star_agent`, `palace_agent`, `transform_agent`, etc.) collaborate to synthesize a final report. Consensus mechanisms are used for causal chain prediction.

### Development Standards
-   **Python**: Use `uv` for all dependency management. Follow PEP 8 styles. Use Flask factory pattern for the application.
-   **Frontend**: Prefer Functional Components with React Hooks. Use `shadcn/ui` for consistent design.
-   **API**: Maintain RESTful principles. Ensure all Chinese responses are properly encoded (UTF-8) without escaping.
-   **Testing**: New features should include unit tests in `backend/tests/unit/` or integration tests in `backend/tests/e2e/`.

---

## Key Files
-   `backend/run.py`: Backend entry point.
-   `frontend/package.json`: Frontend dependencies and scripts.
-   `AGENTS.md` / `CLAUDE.md`: Detailed guidance for AI coding assistants.
-   `docker-compose.yml`: Containerization setup for production/staging.
