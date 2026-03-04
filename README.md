# Humain DecisionOps Console

A production-style Insurance Claims Decision Console: a SaaS dashboard + agentic decision pipeline that ingests claim documents, performs extraction + policy RAG, computes risk/fraud, outputs an auditable decision, and persists full audit evidence.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Overview │ │  Claims  │ │ Fast Lane│ │Knowledge │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   LangGraph Pipeline                      │   │
│  │  ingest → extract → retrieve → risk → fraud → decide     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Postgres │   │  MongoDB │   │  Ollama  │
        │ pgvector │   │(optional)│   │ /OpenAI  │
        └──────────┘   └──────────┘   └──────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Ollama running locally for LLM inference
- (Optional) OpenAI API key for cloud LLM

### 1. Clone and Setup

```bash
cd humain-decisionops
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Start Services

```bash
docker compose up --build
```

### 3. Access Applications

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| pgAdmin | http://localhost:5050 | admin@humain.local / admin123 |
| Mongo Express | http://localhost:8081 | - |

## Demo Script (90 seconds)

1. **Open Dashboard** (0:00-0:10)
   - Navigate to http://localhost:3000
   - Show Overview page with KPIs and live claims stream

2. **Claims Inbox** (0:10-0:25)
   - Click "Claims Inbox" in sidebar
   - Show 10+ seeded claims with different triage labels
   - Filter by STP, REVIEW, HIGH_RISK

3. **Claim Detail** (0:25-0:45)
   - Click on a claim to open detail workspace
   - Walk through tabs: Document, Extraction, Policy Matches, Risk/Fraud, Decision
   - Show audit timeline

4. **Run Pipeline** (0:45-1:00)
   - Click "Run Pipeline" button
   - Watch status update in real-time
   - Show decision result with rationale

5. **Fast Lane** (1:00-1:15)
   - Navigate to Fast Lane queue
   - Show auto-approve eligible claims
   - Demonstrate override functionality

6. **Fraud Scenarios** (1:15-1:30)
   - Show fraud scenario library
   - Adjust threshold slider
   - View recent hits

## 20-Minute Talk Track

### Introduction (2 min)
- Problem: Insurance claims processing is slow, error-prone, and lacks transparency
- Solution: AI-powered decision infrastructure with full auditability

### Architecture Deep Dive (5 min)
- Monorepo structure: frontend, backend, infra
- LangGraph pipeline: 8 nodes for complete claim processing
- Database design: PostgreSQL with pgvector for semantic search
- Optional MongoDB for raw document storage

### Feature Walkthrough (10 min)
1. **Smart Triage** - Automatic classification into STP/REVIEW/HIGH_RISK
2. **Document Forensics** - PDF metadata analysis, template detection
3. **Policy RAG** - Semantic search over policy documents
4. **Fraud Detection** - 12 configurable fraud scenarios
5. **Fast Lane Automation** - Auto-approve with human oversight
6. **Conversation Intake** - Chat-based FNOL collection
7. **Full Audit Trail** - Every action logged with payload

### Technical Highlights (3 min)
- Pydantic validation with repair attempts
- LangSmith tracing integration
- Flexible LLM provider (Ollama/OpenAI)
- Docker-first deployment

## Environment Variables

### Backend
| Variable | Description | Default |
|----------|-------------|--------|
| DATABASE_URL | PostgreSQL connection string | postgresql://humain:humain_secret@postgres:5432/humain_decisionops |
| MONGO_URL | MongoDB connection string | mongodb://humain:humain_secret@mongo:27017/ |
| OPENAI_API_KEY | OpenAI API key (optional) | - |
| LANGSMITH_API_KEY | LangSmith API key (optional) | - |
| OLLAMA_BASE_URL | Ollama server URL | http://host.docker.internal:11434 |
| API_KEY | API authentication key | - |
| AUTH_ENABLED | Enable API key auth | false |
| **CORS_ALLOW_ORIGINS** | Comma-separated allowed origins | * |
| **HEURISTIC_MODE** | Force heuristic mode (no LLM) | false |
| **SEED_ON_STARTUP** | Run DB seed on startup | false |

### Frontend
| Variable | Description | Default |
|----------|-------------|--------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 |

## Acceptance Checklist

- [ ] `docker compose up --build` starts all services without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] Overview page shows KPI cards with data
- [ ] Claims Inbox shows 10+ seeded claims
- [ ] Claim Detail page shows all tabs with data
- [ ] Run Pipeline creates a decision and audit events
- [ ] Fast Lane shows eligible claims
- [ ] Override button works and creates audit event
- [ ] Fraud Scenarios page shows 12 scenarios
- [ ] Knowledge Base allows upload and test retrieval
- [ ] Governance/Audit shows filterable events
- [ ] pgAdmin accessible and shows database tables

## Troubleshooting

### Docker Issues

**Problem**: `docker compose up` fails with port conflicts
```bash
# Check what's using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Kill the process or change ports in docker-compose.yml
```

**Problem**: Backend can't connect to Postgres
```bash
# Check if postgres is healthy
docker compose ps
docker compose logs postgres

# Restart just postgres
docker compose restart postgres
```

### LLM Issues

**Problem**: Pipeline fails with LLM errors
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Or set OpenAI key in .env
OPENAI_API_KEY=sk-...
```

**Problem**: Slow LLM responses
- Ollama on CPU can be slow; consider using OpenAI for demos
- Or run Ollama with GPU support

### Database Issues

**Problem**: No data showing in UI
```bash
# Check if seed ran
docker compose logs postgres | grep seed

# Manually run seed
docker compose exec postgres psql -U humain -d humain_decisionops -f /docker-entrypoint-initdb.d/02-seed.sql
```

### Frontend Issues

**Problem**: API calls failing
- Check NEXT_PUBLIC_API_URL is set correctly
- Check backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors

## Project Structure

```
humain-decisionops/
├── frontend/                 # Next.js frontend
│   ├── app/                  # App router pages
│   ├── components/           # React components
│   ├── lib/                  # Utilities and types
│   └── Dockerfile
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # Pydantic & SQLAlchemy models
│   │   ├── services/         # Business logic
│   │   └── pipeline/         # LangGraph pipeline
│   ├── tests/                # Pytest tests
│   └── Dockerfile
├── infra/
│   └── postgres/             # SQL migrations and seed
├── data/
│   ├── uploads/              # Claim document uploads
│   └── policies/             # Policy documents
├── docker-compose.yml
├── render.yaml               # Render deployment config
├── vercel.json               # Vercel deployment config
├── .env.example
└── README.md
```

---

## Free-Tier Cloud Deployment

Deploy the application for free using:
- **Frontend**: Vercel (free tier)
- **Backend**: Render (free tier)
- **Database**: Neon PostgreSQL (free tier)

### Step 1: Set Up Neon PostgreSQL

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project named `humain-decisionops`
3. Copy the connection string (looks like `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`)
4. Run the schema and seed SQL:
   - Go to the Neon SQL Editor
   - Copy contents of `infra/postgres/01-init.sql` and run it
   - Copy contents of `infra/postgres/02-seed.sql` and run it

### Step 2: Deploy Backend to Render

1. Go to [render.com](https://render.com) and create a free account
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `humain-decisionops-api`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   ```
   DATABASE_URL=<your-neon-connection-string>
   CORS_ALLOW_ORIGINS=https://humain-decisionops.vercel.app,http://localhost:3000
   HEURISTIC_MODE=true
   SEED_ON_STARTUP=false
   LOG_LEVEL=INFO
   ```
6. (Optional) Add `OPENAI_API_KEY` if you want LLM features
7. Click "Create Web Service"
8. Note the URL (e.g., `https://humain-decisionops-api.onrender.com`)

### Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and create a free account
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://humain-decisionops-api.onrender.com
   ```
6. Click "Deploy"

### Step 4: Update CORS (if needed)

After Vercel deployment, update the Render backend's `CORS_ALLOW_ORIGINS` to include your actual Vercel URL:
```
CORS_ALLOW_ORIGINS=https://your-project.vercel.app,http://localhost:3000
```

### Deployment Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   Vercel (Free)     │     │   Render (Free)     │
│   Next.js Frontend  │────▶│   FastAPI Backend   │
│                     │     │   (Heuristic Mode)  │
└─────────────────────┘     └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │   Neon (Free)       │
                            │   PostgreSQL        │
                            └─────────────────────┘
```

### Operating Modes

The backend supports three operating modes:

| Mode | Description | When Used |
|------|-------------|-----------|
| **OpenAI** | Full LLM features with GPT-4o-mini | `OPENAI_API_KEY` is set |
| **Ollama** | Local LLM with Llama2 | Ollama server is reachable |
| **Heuristic** | Rule-based, no LLM calls | Default fallback or `HEURISTIC_MODE=true` |

In **Heuristic Mode**, the pipeline still:
- ✅ Creates DecisionBundle with decision status
- ✅ Generates audit events
- ✅ Computes fraud hits and risk scores
- ✅ Produces forensics signals
- ✅ Returns policy matches (simple keyword matching)
- ❌ Does NOT use LLM for extraction (uses templates)
- ❌ Does NOT use LLM for rationale (uses templates)

Check the current mode in the **Settings** page of the UI.

### Free Tier Limitations

| Service | Limitation |
|---------|------------|
| Render | Spins down after 15 min inactivity (cold start ~30s) |
| Neon | 0.5 GB storage, auto-suspend after 5 min |
| Vercel | 100 GB bandwidth/month |

### Troubleshooting Deployment

**Backend not starting on Render:**
- Check build logs for missing dependencies
- Ensure `requirements.txt` is in the `backend/` directory
- Verify DATABASE_URL is correctly set

**Frontend can't reach backend:**
- Check CORS_ALLOW_ORIGINS includes your Vercel domain
- Verify NEXT_PUBLIC_API_URL is set correctly (no trailing slash)
- Check Render service is running (not suspended)

**Database connection errors:**
- Verify Neon connection string includes `?sslmode=require`
- Check Neon project is not suspended
- Run schema/seed SQL if tables are missing

---

## License

Proprietary - Humain AI Inc.
