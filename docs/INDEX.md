# Argus Documentation Index

Welcome to the Argus documentation. This guide will help you understand, use, and modify the Argus stock screening application.

---

## Quick Links

| I want to... | Read this |
|--------------|-----------|
| Set up the project | [README.md](../README.md) |
| Understand the architecture | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Make code changes | [CODE_GUIDE.md](./CODE_GUIDE.md) |
| Contribute to the project | [CONTRIBUTING.md](./CONTRIBUTING.md) |
| Debug an issue | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) |
| Use the API | [API.md](./API.md) |
| Understand backend modules | [BACKEND_REFERENCE.md](./BACKEND_REFERENCE.md) |
| Understand frontend components | [FRONTEND_REFERENCE.md](./FRONTEND_REFERENCE.md) |
| Set up development environment | [DEVELOPMENT.md](./DEVELOPMENT.md) |

---

## Documentation Overview

### For New Developers / AI Agents

Start here to understand the codebase:

1. **[README.md](../README.md)** - Project overview and quick start
2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and data flow
3. **[CODE_GUIDE.md](./CODE_GUIDE.md)** - Code patterns and algorithms

### For Making Changes

Reference these when implementing features:

1. **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Code style, testing, PR checklist
2. **[BACKEND_REFERENCE.md](./BACKEND_REFERENCE.md)** - All backend modules and functions
3. **[FRONTEND_REFERENCE.md](./FRONTEND_REFERENCE.md)** - All frontend components and hooks

### For Troubleshooting

When things go wrong:

1. **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
2. **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Development environment setup

---

## Document Summaries

### README.md
- Project overview
- Tech stack summary
- Quick start commands
- Project structure overview

### ARCHITECTURE.md
- System architecture diagrams
- Backend layer structure (API → Core → Services → Data)
- Frontend component hierarchy
- Data flow for key operations
- State management strategy
- Caching strategy
- Background task configuration
- Design patterns used
- Extensibility points

### CODE_GUIDE.md
- Detailed code explanations with examples
- Indicator calculation algorithms (MA, RSI, MACD)
- Screener logic walkthrough
- Signal detection algorithms
- Caching implementation
- API endpoint patterns
- Frontend component patterns
- State management patterns
- Chart implementation details
- Step-by-step guides for common tasks

### CONTRIBUTING.md
- Development environment setup
- Python and TypeScript style guidelines
- Testing guidelines with examples
- PR checklist
- Git workflow
- End-to-end feature implementation example

### TROUBLESHOOTING.md
- Quick diagnostic commands
- Backend issues (startup, database, market data, Redis, API)
- Frontend issues (build, API connection, charts, state)
- Docker issues
- Performance issues
- Error message reference

### API.md
- All API endpoints with parameters
- Request/response examples
- Error response format

### BACKEND_REFERENCE.md
- Complete API endpoint reference
- Core module classes and methods
- Service classes
- All Pydantic and SQLAlchemy models
- Utility functions
- Cache key and TTL utilities
- Exception classes
- Configuration options

### FRONTEND_REFERENCE.md
- All UI components with usage examples
- Layout components
- Chart components
- Feature components (screener, signals, search)
- Custom hooks
- Zustand stores
- TypeScript type definitions
- Utility functions

### DEVELOPMENT.md
- Prerequisites
- Step-by-step setup for backend and frontend
- Running tests
- Code quality commands
- Environment variables
- Database migrations
- Debugging tips

---

## File Structure

```
docs/
├── INDEX.md              ← You are here
├── ARCHITECTURE.md       ← System design
├── API.md                ← API reference
├── CODE_GUIDE.md         ← Code patterns and algorithms
├── CONTRIBUTING.md       ← Contribution guidelines
├── DEVELOPMENT.md        ← Development setup
├── TROUBLESHOOTING.md    ← Problem solving
├── BACKEND_REFERENCE.md  ← Backend module reference
└── FRONTEND_REFERENCE.md ← Frontend component reference
```

---

## For AI Coding Agents

If you're an AI agent working on this codebase, here's the recommended reading order:

### Understanding the Codebase
1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for the big picture
2. Read [CODE_GUIDE.md](./CODE_GUIDE.md) for implementation details

### Making Changes
1. Check [BACKEND_REFERENCE.md](./BACKEND_REFERENCE.md) or [FRONTEND_REFERENCE.md](./FRONTEND_REFERENCE.md) for the specific module
2. Follow patterns in [CODE_GUIDE.md](./CODE_GUIDE.md)
3. Follow style guidelines in [CONTRIBUTING.md](./CONTRIBUTING.md)

### Key Files to Understand

**Backend:**
- `backend/app/core/indicators.py` - All technical indicator math
- `backend/app/core/screener.py` - Main screening logic
- `backend/app/core/signals.py` - Signal detection
- `backend/app/services/market_data.py` - Data fetching
- `backend/app/api/v1/*.py` - API endpoints

**Frontend:**
- `frontend/src/components/charts/StockChart.tsx` - Main chart
- `frontend/src/hooks/*.ts` - Data fetching hooks
- `frontend/src/stores/*.ts` - State management
- `frontend/src/pages/*.tsx` - Page components

### Common Tasks

| Task | Key Files | Documentation |
|------|-----------|---------------|
| Add new indicator | `core/indicators.py`, `models/indicator.py` | CODE_GUIDE.md → "Adding a New Technical Indicator" |
| Add new signal type | `core/signals.py`, `models/signal.py` | CODE_GUIDE.md → "Adding a New Signal Type" |
| Add new API endpoint | `api/v1/new.py`, `api/v1/router.py` | CODE_GUIDE.md → "Adding a New API Endpoint" |
| Add new component | `components/feature/New.tsx` | FRONTEND_REFERENCE.md |
| Fix API issue | `api/v1/*.py` | TROUBLESHOOTING.md → "API Endpoint Issues" |
| Fix chart issue | `components/charts/StockChart.tsx` | TROUBLESHOOTING.md → "Chart Issues" |
