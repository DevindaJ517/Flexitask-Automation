# FlexiTask Automation - Project Summary

## 📋 Overview

**FlexiTask Automation** is an automated job posting service that monitors the FlexiTask job database (Supabase) and automatically shares new job postings to a Telegram channel. It's designed for free cloud deployment and provides real-time job monitoring with scheduled polling.

---

## 🛠 Tech Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core runtime language |
| **FastAPI** | ≥0.104.0 | Web framework for REST API |
| **Uvicorn** | ≥0.24.0 | ASGI server for running FastAPI |
| **Pydantic** | ≥2.5.0 | Data validation and settings management |

### Database & Storage

| Technology | Purpose |
|------------|---------|
| **Supabase** | PostgreSQL database connection (FlexiTask job data) |
| **Redis** | Job tracking to prevent duplicate posts (Upstash for production) |

### Messaging & Scheduling

| Technology | Version | Purpose |
|------------|---------|---------|
| **python-telegram-bot** | ≥21.0 | Telegram Bot API integration |
| **APScheduler** | ≥3.10.0 | Background task scheduling (replaces Celery for free tier) |

### HTTP & Utilities

| Technology | Version | Purpose |
|------------|---------|---------|
| **httpx** | ≥0.26.0 | Async HTTP client |
| **python-dotenv** | ≥1.0.0 | Environment variable management |

### Deployment

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Local development orchestration |
| **Render** | Free cloud hosting |
| **Upstash Redis** | Free Redis hosting |

---

## ✨ Features

### 🔍 Database Monitoring
- Automatically detects new published jobs from Supabase
- Queries job posts with related data (categories, countries, cities)
- Filters jobs by creation date with configurable lookback period
- Real-time tracking of published job status

### 📱 Telegram Integration
- Formatted job listings with rich formatting (MarkdownV2)
- Support for both text messages and image-based posts
- Automatic hashtag generation based on job category
- Direct apply links to job postings
- Channel posting with admin bot support
- Escaped special characters for Telegram compatibility

### ⚡ Background Scheduling
- APScheduler handles periodic job checks (free tier compatible)
- Configurable polling interval (default: 60 seconds)
- Asyncio-based scheduler for non-blocking operations
- Manual trigger endpoints for immediate checks

### 📊 Job Tracking
- Redis-based tracking to prevent duplicate posts
- Stores job share timestamps
- Tracks Telegram message IDs for posted jobs
- Last check timestamp persistence

### 🌐 REST API Endpoints

#### Health & Status
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with service info |
| `/health` | GET | Detailed health check for all services |

#### Job Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jobs/new` | GET | Get new jobs not yet shared (with hour filter) |
| `/api/jobs/{job_id}` | GET | Get details of a specific job |
| `/api/jobs/shared/recent` | GET | Get recently shared jobs list |

#### Sharing Controls
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/share/{job_id}` | POST | Manually share a specific job to Telegram |
| `/api/share/trigger-check` | POST | Trigger background job check |

#### Scheduler Controls
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scheduler/status` | GET | Get current scheduler status |
| `/api/scheduler/trigger` | POST | Manually trigger immediate job check |

#### Preview & Statistics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/preview/telegram` | POST | Preview formatted Telegram message |
| `/api/stats` | GET | Get sharing statistics |

### 🔄 Job Message Formatting
- Title and company name with proper formatting
- Location display (City, Country)
- Work type indicators (On-site, Remote, Hybrid)
- Employment type (Full Time, Part Time, Contract)
- Category tags
- Experience requirements
- Internship badge for internship positions
- Description preview (200 characters)
- Apply Now link
- Dynamic hashtags (#Jobs, #Hiring, #FlexiTask, #RemoteJobs)

---

## 🏗 Project Architecture

```
Flexitask-Automation/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── config.py            # Settings and environment config
│   ├── models.py            # Pydantic data models
│   ├── scheduler.py         # APScheduler configuration
│   └── services/
│       ├── __init__.py
│       ├── supabase_service.py   # Supabase database operations
│       └── telegram_service.py   # Telegram bot integration
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
├── Procfile                 # Heroku/Render process file
├── render.yaml              # Render deployment config
├── start.sh                 # Startup script
├── run_check.py             # Manual check script
├── test_api.py              # API tests
└── docs/
    ├── DEPLOYMENT.md        # Deployment instructions
    ├── INTEGRATION_GUIDE.md # Integration documentation
    └── MESSAGE_FORMAT.md    # Message formatting guide
```

---

## 📦 Data Models

### JobPosting
- `id`, `title`, `slug`, `companyName`
- `employmentType`: FULL_TIME, PART_TIME, CONTRACT
- `workLocationType`: ONSITE, REMOTE, HYBRID
- `experienceYears`: ONE_PLUS, TWO_PLUS, FIVE_PLUS
- `isInternship`, `isPublished`
- `category`, `country`, `city` (related data)
- `uniqueDescription`, `linkedInApplyURL`, `jobImageUrl`
- `createdAt`, `updatedAt`

### SharedJob
- `job_id`, `shared_at`
- `telegram_shared`, `telegram_message_id`
- `error_message`

---

## ⚙️ Configuration

### Environment Variables
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHANNEL_ID=@your-channel

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Polling interval (seconds)
POLLING_INTERVAL_SECONDS=60
```

---

## 🚀 Deployment Options

### Local Development
```bash
pip install -r requirements.txt
redis-server &
python -m app.main
```

### Docker
```bash
docker-compose up -d
```

### Cloud (Free Tier)
- **Render** - Free web service
- **Upstash Redis** - Free tier Redis

---

## 📈 Version

**Current Version:** 2.0.0

---

## 📝 Key Highlights

1. **Zero-Cost Deployment** - Designed for free cloud platforms (Render + Upstash)
2. **Async-First** - Built with asyncio for non-blocking operations
3. **Duplicate Prevention** - Redis-based tracking prevents double posting
4. **CORS Enabled** - Ready for frontend integration
5. **Comprehensive API** - Full REST API for manual control and monitoring
6. **Graceful Lifecycle** - Proper startup/shutdown handling with FastAPI lifespan
7. **Structured Logging** - Detailed logging for debugging and monitoring
8. **Type-Safe** - Pydantic models for data validation
