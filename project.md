# Stock Market Portfolio - Project Overview

## 📋 Project Information

**Project Name:** Personal Portfolio Control Center  
**Root Directory:** `/home/yigitalp/Projects/stock-market-portfolio`  
**Project Type:** Modern portfolio management platform  
**Current Status:** Version 1.0 MVP phase  

## 🎯 Project Vision

This project aims to evolve from a simple portfolio tracker into a comprehensive financial assistant enriched with AI-powered analytics and social collaboration features.

## 🏗️ Technology Stack

### Backend (Application Brain)
- **Framework:** Python & FastAPI
- **Rationale:** Python's unrivaled AI/ML ecosystem (Hugging Face, Pandas, PyPortfolioOpt) and FastAPI's modern performance

### Frontend (Application Face)  
- **Framework:** Flutter & Dart
- **Rationale:** Single codebase for Android/iOS/Web support, native performance

### Database (Application Memory)

#### Primary Database (v1.0)
- **PostgreSQL**
- **Rationale:** Reliability and data integrity for financial data

#### Real-Time Database (v3.0)
- **Firebase (Firestore/Realtime DB)**
- **Rationale:** Optimized for chat and live data streams

#### Vector Database (v3.0)
- **ChromaDB**
- **Rationale:** Text embeddings for RAG and semantic search

### Infrastructure & DevOps

#### Containerization (v1.0)
- **Docker & Docker Compose**
- **Rationale:** Consistent development environments and easy deployment

#### Data Collection Automation (v2.0)
- **n8n**
- **Rationale:** Visual interface for news and data collection automation

#### Hosting
- **DigitalOcean / Hetzner VPS**
- **Rationale:** Cost-effective, easy management for Docker workloads

## 🚀 Version Roadmap

### Version 1.0: "Personal Portfolio Control Center" (MVP)
**Primary Goal:** Rapid time-to-market with essential portfolio tracking

**Features:**
- ✅ Secure user registration and login
- ✅ Smart onboarding wizard
- ✅ Asset management (create, update, delete)
- ✅ Real-time portfolio valuation and profit/loss tracking
- ✅ Asset detail pages with price charts
- ✅ Personalized news feed

### Version 2.0: "Intelligent Analysis and Discovery Layer"
**Primary Goal:** Proactive, AI-driven analytics and insights

**Features:**
- 🤖 NLP-powered sentiment analysis
- 📊 Personalized news curation
- 📅 Financial calendar and event tracking
- 🎮 Simulation mode (virtual portfolio)
- 📈 TEFAS mutual fund support
- 🔄 Automated MLOps workflows

### Version 3.0+: "Holistic Financial Coach & Community"
**Primary Goal:** Social engagement and end-to-end financial management

**Features:**
- 👥 Social chat rooms
- 💰 Personal finance module
- 🎯 Portfolio optimization
- 🏆 Gamification system
- 📚 RAG-enabled financial assistant

## 📋 Development Environment Requirements

### Prerequisites
- **Docker** & **Docker Compose**
- **Python 3.9+**
- **Flutter SDK** (3.0+)
- **PostgreSQL** (via Docker)

### Quick Start Commands

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup  
```bash
cd frontend
flutter doctor
flutter pub get
flutter run -d chrome  # For web
# or
flutter run  # For mobile
```

#### Start Backend with Docker
```bash
cd backend
docker-compose up -d
```

## 📊 Technology Summary Table

| Area | Primary Technology | Rationale | Target Version |
|------|--------------------|-----------|----------------|
| Backend | Python / FastAPI | AI/ML power, performance | v1.0 |
| Frontend | Flutter / Dart | Multi-platform, high performance | v1.0 |
| Core Database | PostgreSQL | Reliability, data integrity | v1.0 |
| Infrastructure | Docker / Docker Compose | Consistency, simplified deployment | v1.0 |
| Automation | n8n | Visual workflows | v2.0 |
| Chat Database | Firebase | Real-time updates | v3.0 |
| AI Database | ChromaDB | Semantic search, RAG support | v3.0 |

## 🎯 Current Focus Areas

1. **MVP Completion:** Stabilization of Version 1.0 features
2. **User Experience:** Flutter interface development  
3. **API Development:** FastAPI backend services expansion
4. **Data Security:** Financial data protection with PostgreSQL

## 🔮 Future Plans

- Preparation for AI/ML integration for Version 2.0
- Planning data collection automation with n8n
- Architecture design for ChromaDB and Firebase integration
- Infrastructure preparation for social features and gamification
