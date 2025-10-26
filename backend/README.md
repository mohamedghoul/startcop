# StartCop

The AI Regulatory Navigator for Fintech Startups

---

## Overview

StartCop is a modular, local-first AI backend for regulatory gap analysis and readiness scoring, built for the AIX Hackathon. It leverages FastAPI, ChromaDB (vector DB), MongoDB, and sentence-transformers for real document retrieval and compliance mapping. All services run locally via Docker Compose for zero-budget, cross-platform development.

---

## Features

- **RAG Pipeline**: Real embedding model (MiniLM), chunking, retrieval, and natural language explanation.
- **Regulatory Readiness Scorecard**: Quantifies compliance across key areas.
- **API**: FastAPI endpoints for document upload, RAG queries, and (soon) expert feedback.
- **Testing**: Pytest-based suite, enforced before backend startup.
- **Local-Only**: No cloud dependencies; all data and models run locally.

---

## Prerequisites

- [Docker](https://www.docker.com/get-started) (latest stable)
- [Docker Compose](https://docs.docker.com/compose/) (v2+)
- (Optional) [Python 3.11+](https://www.python.org/) for local dev/testing
- (Optional) [Git](https://git-scm.com/) for version control

> **Works on Windows, macOS, and Linux.**

---

## Quick Start (Recommended)

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd startcop/backend
   ```

2. **Build and start all services:**
   ```sh
   docker compose up --build
   ```
   This will:
   - Build the backend image
   - Start MongoDB, ChromaDB, and the backend API
   - Run all tests before starting the backend

3. **Access the API:**
   - FastAPI docs: [http://localhost:3000/docs](http://localhost:3000/docs)
   - Health check: [http://localhost:3000/api/v0](http://localhost:3000/api/v0)

4. **(Optional) Populate test data:**
   ```sh
   docker compose run --rm data-populator
   ```
   This loads mock regulatory and startup documents into MongoDB and ChromaDB.

---

## Development Workflow

- **Code changes:** Edit files in `src/` and `tests/`.
- **Run tests:**
  - Automatically run in Docker on every backend start.
  - Or manually: `docker compose run --rm backend pytest tests`
- **Hot reload:** FastAPI runs with `--reload` for instant code reloads.
- **Logs:** All logs output to the terminal.

---

## Directory Structure

```
backend/
  ├── src/           # Main backend source code
  │   ├── main.py    # FastAPI entrypoint
  │   └── rag/       # RAG pipeline, scorecard, utils
  ├── tests/         # All pytest tests (unit, integration, advanced)
  ├── Dockerfile     # Backend Docker build
  ├── docker-compose.yml # Multi-service orchestration
  └── requirements.txt   # Python dependencies
```

---

## Environment Variables

Set in `docker-compose.yml` (override as needed):
- `MONGO_URI` (default: `mongodb://mongo:27017`)
- `CHROMA_HOST` (default: `chroma`)
- `CHROMA_PORT` (default: `8000`)

---

## Troubleshooting

- **Port conflicts:** Stop any local services using ports 3000, 8000, or 27017.
- **Windows users:** Use WSL2 for best Docker performance.
- **Model download issues:** The first run will download the MiniLM model; ensure internet access.
- **Test failures:** Check logs for details; all tests must pass before backend starts.