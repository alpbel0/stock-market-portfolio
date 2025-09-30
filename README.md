# Personal Portfolio Control Center

Modern, intelligent, and user-friendly portfolio management platform. Track, analyze, and optimize every asset across markets from a single dashboard.

## 🎯 Project Vision

This initiative aims to evolve from a simple portfolio tracker into a comprehensive financial assistant enriched with AI-powered analytics and social collaboration features.

## 🚀 Version Roadmap

### Version 1.0: "Personal Portfolio Control Center" (MVP)
**Primary Goal:** Rapid time-to-market with essential portfolio tracking.

**Features:**
- ✅ Secure user registration and login
- ✅ Smart onboarding wizard
- ✅ Asset management (create, update, delete)
- ✅ Real-time portfolio valuation and profit/loss tracking
- ✅ Asset detail pages with price charts
- ✅ Personalized news feed

### Version 2.0: "Intelligent Analysis and Discovery Layer"
**Primary Goal:** Proactive, AI-driven analytics and insights.

**Features:**
- 🤖 NLP-powered sentiment analysis
- 📊 Personalized news curation
- 📅 Financial calendar and event tracking
- 🎮 Simulation mode (virtual portfolio)
- 📈 TEFAS mutual fund support
- 🔄 Automated MLOps workflows

### Version 3.0+: "Holistic Financial Coach & Community"
**Primary Goal:** Social engagement and end-to-end financial management.

**Features:**
- 👥 Social chat rooms
- 💰 Personal finance module
- 🎯 Portfolio optimization
- 🏆 Gamification system
- 📚 RAG-enabled financial assistant

## 🛠️ Tech Stack

### Backend — The Application Brain
- **Framework:** Python & FastAPI
  - *Why:* Python's AI/ML ecosystem (Hugging Face, Pandas, PyPortfolioOpt) is unrivaled, and FastAPI delivers modern performance with automatic documentation.

### Frontend — The Application Face
- **Framework:** Flutter & Dart
  - *Why:* Single codebase for Android/iOS/Web, native performance, and rapid hot-reload development cycle.

### Database — The Application Memory

#### Primary Database (v1.0)
- **PostgreSQL**
  - *Why:* Industry-standard reliability, consistency, and integrity for financial data.

#### Real-Time Database (v3.0)
- **Firebase (Firestore/Realtime DB)**
  - *Why:* Optimized for chat and live data streams with seamless mobile integration.

#### Vector Database (v3.0)
- **ChromaDB**
  - *Why:* Efficiently stores text embeddings for RAG and semantic search; open source and Python-friendly.

### Infrastructure & DevOps — The Skeleton and Automation

#### Containerization (v1.0)
- **Docker & Docker Compose**
  - *Why:* Consistent development environments, straightforward deployment, and eliminates "works on my machine" issues.

#### Data Collection Automation (v2.0)
- **n8n**
  - *Why:* Visual interface for automating news and data ingestion keeps backend codebase clean.

#### Hosting
- **DigitalOcean / Hetzner VPS**
  - *Why:* Cost-effective, easy-to-manage hosting for Dockerized workloads.

## 📋 Technology Summary Table

| Area | Primary Technology | Rationale | Target Version |
|------|--------------------|-----------|----------------|
| Backend | Python / FastAPI | AI/ML power, performance, developer experience | v1.0 |
| Frontend | Flutter / Dart | Multi-platform, high performance | v1.0 |
| Core Database | PostgreSQL | Reliability, data integrity | v1.0 |
| Infrastructure | Docker / Docker Compose | Consistency, simplified deployment | v1.0 |
| Automation | n8n | Visual workflows, reduces backend load | v2.0 |
| Chat Database | Firebase | Real-time updates, mobile-first | v3.0 |
| AI Database | ChromaDB | Semantic search, RAG support | v3.0 |

## 🚀 Getting Started

### Prerequisites
- **Docker** & **Docker Compose**
- **Python 3.9+**
- **Flutter SDK** (3.0+)
- **PostgreSQL** (via Docker)

### Quick Start

```bash
# Clone the repository
git clone [repo-url]
cd portfolio-control-center

# Start the backend with Docker
cd backend
docker-compose up -d

# Launch the frontend
cd ../frontend
flutter pub get
flutter run
```

### Development Environment Details

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
flutter doctor  # System check
flutter pub get
flutter run -d chrome  # For web
# or
flutter run  # For mobile
```
