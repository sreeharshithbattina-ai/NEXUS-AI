# NEXUS AI OS Core - Backend Foundation (Phase 1)

This is the production-ready FastAPI backend service representing **Phase 1: Backend Foundation** of the NEXUS personal AI operating system. It follows SOLID principles and Clean Architectural patterns to power core identity verification, episodic memory exploration, vector context indexing, and virtual automation queues.

---

## 1. Clean Architectural Topology

This service is structured according to the Clean Architecture standard to preserve data boundary encapsulation and decouple third-party frameworks from core entities:

```
[ HTTP REST Layer / API Routers (FastAPI) ]
                │
                ▼
[ Data Transfer Validation / Schemas (Pydantic) ]
                │
                ▼
[ Business Domain Logic / Core Services (SOLID) ]
                │
                ▼
[ Entity & Persistence Layer / ORM (SQLAlchemy) ]
                │
                ▼
[ Relational Datastores / (PostgreSQL / SQLite) ]
```

### Why it is Designed this Way:
* **Separation of Concerns**: Changes to the database architecture (such as migrating from SQLite to PostgreSQL) or HTTP framework will not impact core user, memory, document, or log domain logic.
* **Testability**: Core service handlers and SQLAlchemy queries are decoupled, allowing effortless unit testing using in-memory databases without setting up full Docker infrastructures.
* **SOLID Rigor**: Endpoints rely on dedicated request/response schemas (Single Responsibility), extendable routers (Open/Closed), and standard ORM definitions.

---

## 2. Core Implemented Modules

1. **Authentication Gate**: Crypto-locked identity setup using bcrypt passwords and HS256 JWT access locks.
2. **User Profiles file**: Personal preference logs, clock reminders schedules, and assistant voice packs customization.
3. **Episodic Memory Bank**: Durable CRUD persistence for Semantic, Episodic, and Short-term factual contexts.
4. **Document Indexer & Chunking Engine**: Multi-passage chunk tokenization and simulated 8-element vector coordinate embedding space for standard RAG pipelines.
5. **Automation Gate Security**: Pre-approved routine queues preventing unsafe financial or irreversible browser bookings.
6. **Unified Logging Center**: Real-time diagnostic stream of kernel activities.

---

## 3. Getting Started

### Local Setup (Using pip/uvicorn)

1. Navigate to the backend workspace:
   ```bash
   cd backend
   ```
2. Install standard dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Access the interactive auto-generated OpenAPI documentation schema:
   * **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * **ReDoc Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Container Deployment (Using Docker Compose)

A production-grade multi-container topology is configured:
```bash
docker-compose up --build -d
```
This spins up:
* **FastAPI application container** at port `8000`
* **PostgreSQL relational database** container at port `5432`
* **Redis high-speed caching engine** container at port `6379`

---

## 4. Run Automated Tests

A comprehensive automation testing suit checks all endpoints under SQLite in-memory static pools:
```bash
pytest app/tests/ -v -s
```
All route behaviors, register-logins, setting saves, memories insertions, documents chunking, and task modifications are covered.
