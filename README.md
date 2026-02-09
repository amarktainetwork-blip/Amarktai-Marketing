# Amarktai Marketing

**Autonomous AI Social Media Marketing Platform | Part of Amarktai Network**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-View%20Site-blue)](https://ojlhabefx73cy.ok.kimi.link)

Amarktai Marketing is a fully autonomous AI-powered social media marketing SaaS platform that promotes users' web apps across the top 6 social media platforms daily with **zero manual effort** beyond a single daily approval step.

## 🚀 Live Demo

**Frontend:** https://ojlhabefx73cy.ok.kimi.link

## ✨ Features

### Core Functionality
- **🤖 AI-Powered Content Generation** - Research, creative, and media agents work together to generate platform-optimized content
- **📅 Daily Automation** - Content is generated every night at 2:00 AM, ready for approval each morning
- **✅ One-Click Approval** - Review, edit, approve, or reject all content from a single dashboard
- **📊 Performance Analytics** - Track views, engagement, and CTR across all platforms
- **🔄 Self-Optimizing** - AI learns from performance data to improve future content

### Platform Coverage
- **YouTube Shorts** - Short-form video content
- **TikTok** - Viral short videos
- **Instagram** - Reels and posts
- **Facebook** - Reels and posts
- **X (Twitter)** - Short posts and threads
- **LinkedIn** - Professional content

### Tech Stack

#### Frontend
- **React + TypeScript** - Modern UI development
- **Vite** - Fast build tooling
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Beautiful UI components
- **Clerk** - Authentication and user management
- **Recharts** - Data visualization

#### Backend
- **FastAPI** - High-performance Python API framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Caching and job queues
- **Celery** - Background task processing

#### AI/ML
- **CrewAI** - Multi-agent orchestration
- **LangGraph** - Workflow orchestration
- **OpenAI/Anthropic/Groq** - LLM providers

## 📁 Project Structure

```
amarktai-marketing/
├── app/                          # Frontend (React + Vite)
│   ├── src/
│   │   ├── app/                 # Page components
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── login/           # Login page
│   │   │   ├── register/        # Register page
│   │   │   └── dashboard/       # Dashboard pages
│   │   ├── components/          # Reusable components
│   │   ├── lib/                 # Utilities and API
│   │   └── types/               # TypeScript types
│   └── dist/                    # Production build
├── backend/                      # Backend (FastAPI)
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   ├── core/                # Configuration
│   │   ├── db/                  # Database models
│   │   ├── models/              # SQLAlchemy models
│   │   └── schemas/             # Pydantic schemas
│   └── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Frontend Setup

```bash
cd app
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Database Setup

```bash
# Create PostgreSQL database
createdb amarktai

# Run migrations (using Alembic)
cd backend
alembic upgrade head
```

## 📋 Features Implemented

### MVP (Phase 1) ✅
- [x] Landing page with pricing
- [x] User authentication (Clerk)
- [x] Dashboard with stats
- [x] Web Apps CRUD
- [x] Platform connections UI
- [x] Content library
- [x] Approval queue
- [x] Analytics dashboard
- [x] Settings page

### Phase 2 (AI Content Generation) 🚧
- [ ] Research Agent
- [ ] Creative Agent
- [ ] Media Generation Agent
- [ ] Nightly workflow orchestrator
- [ ] Background workers

### Phase 3 (Full Autonomy) 🚧
- [ ] Autonomous posting
- [ ] Performance optimization
- [ ] A/B testing
- [ ] Community management

## 💰 Pricing Tiers

| Feature | Free | Pro ($29/mo) | Business ($99/mo) |
|---------|------|--------------|-------------------|
| Web Apps | 1 | 5 | Unlimited |
| Platforms | 3 | 6 | 6 |
| Posts/Day | 3 | 12 | 36 |
| AI Model | Groq | Grok/Claude | GPT-4o |
| Images/Month | 30 | 150 | 500 |
| Videos/Month | 5 | 30 | 100 |
| Support | Community | Priority | Dedicated |

## 🔐 Environment Variables

### Frontend (.env)
```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/amarktai
REDIS_URL=redis://localhost:6379
CLERK_SECRET_KEY=sk_test_...
GROK_API_KEY=xai-...
LEONARDO_API_KEY=...
# ... see .env.example for full list
```

## 🛣️ API Endpoints

### Web Apps
- `GET /api/v1/webapps` - List all web apps
- `POST /api/v1/webapps` - Create new web app
- `GET /api/v1/webapps/{id}` - Get web app details
- `PUT /api/v1/webapps/{id}` - Update web app
- `DELETE /api/v1/webapps/{id}` - Delete web app

### Content
- `GET /api/v1/content` - List all content
- `GET /api/v1/content/pending` - Get pending content
- `POST /api/v1/content/{id}/approve` - Approve content
- `POST /api/v1/content/{id}/reject` - Reject content
- `PUT /api/v1/content/{id}` - Update content

### Platforms
- `GET /api/v1/platforms` - List connected platforms
- `POST /api/v1/platforms/{platform}/connect` - Connect platform
- `POST /api/v1/platforms/{platform}/disconnect` - Disconnect platform

### Analytics
- `GET /api/v1/analytics/summary` - Get analytics summary
- `GET /api/v1/analytics/platform/{platform}` - Get platform analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software owned by Amarktai Network.

## 🙏 Acknowledgments

- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components
- [Clerk](https://clerk.com/) for authentication
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [CrewAI](https://github.com/joaomdmoura/crewAI) for AI agent orchestration

---

**Part of Amarktai Network** - Building the future of autonomous marketing
