# FlexiTask Automation 🚀

**Automated Telegram Job Posting Service for FlexiTask**

This automation server monitors the FlexiTask job database (Supabase) and automatically shares new job postings to a Telegram channel.

## 📋 Features

- **🔍 Database Monitoring**: Automatically detects new published jobs from Supabase
- **📱 Telegram Integration**: Posts formatted job listings to your Telegram channel
- **⚡ Background Scheduling**: APScheduler handles periodic job checks
- **📊 Job Tracking**: Redis-based tracking to prevent duplicate posts
- **🔄 Scheduled Polling**: Configurable polling interval (default: 60 seconds)
- **🌐 REST API**: Manual control and monitoring endpoints
- **☁️ Free Cloud Deployment**: Designed for Render free tier

## 🛠 Tech Stack

- **Python 3.11** - Core runtime
- **FastAPI** - Web framework for REST API
- **APScheduler** - Background task scheduling
- **Redis** - Job tracking (Upstash for production)
- **Supabase** - Database connection (FlexiTask PostgreSQL)
- **python-telegram-bot** - Telegram integration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (local or Upstash)
- Supabase project credentials
- Telegram Bot Token

### 1. Clone the Repository

```bash
git clone https://github.com/DevindaJ517/Flexitask-Automation.git
cd Flexitask-Automation
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://qdtmbfuwonsdmfhtasqp.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHANNEL_ID=@your-channel

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Polling interval (seconds)
POLLING_INTERVAL_SECONDS=60
```

### 3. Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (if not running)
redis-server &

# Run the server
python -m app.main
```

### 4. Run with Docker

```bash
docker-compose up -d
```

---

## ☁️ Free Cloud Deployment

Deploy for **$0/month** using:
- **Render** (free web service)
- **Upstash Redis** (free tier)

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/api/scheduler/status` | GET | Scheduler status |
| `/api/scheduler/trigger` | POST | Manual job check |
| `/api/jobs/new` | GET | List unshared jobs |
| `/api/jobs/{id}` | GET | Get job details |
| `/api/share/{id}` | POST | Share specific job |
| `/api/stats` | GET | Statistics |

---

## �� How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                   FlexiTask Automation                      │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ APScheduler │───▶│ Supabase     │───▶│ Telegram     │  │
│  │ (every 60s) │    │ Query Jobs   │    │ Post Message │  │
│  └─────────────┘    └──────────────┘    └──────────────┘  │
│                            │                               │
│                            ▼                               │
│                     ┌──────────────┐                       │
│                     │ Redis        │                       │
│                     │ Track Shared │                       │
│                     └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

1. **Scheduler** runs every 60 seconds (configurable)
2. **Queries Supabase** for new published jobs
3. **Checks Redis** to skip already-shared jobs
4. **Posts to Telegram** with formatted job details
5. **Records** in Redis to prevent duplicates

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_KEY` | Supabase anon/public key | Required |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Required |
| `TELEGRAM_CHANNEL_ID` | Channel ID or @username | Required |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `POLLING_INTERVAL_SECONDS` | Check interval | `60` |
| `JOB_SITE_URL` | FlexiTask website URL | `https://flexi-task-zeta.vercel.app` |

---

## 📱 Telegram Message Format

Jobs are posted with this format:

```
💼 **Job Title**
🏢 Company Name

📍 City, Country
⏰ Full Time | Remote

📝 Job description here...

🔗 [Apply Now](https://flexi-task-zeta.vercel.app/jobs/job-slug)
```

---

## 📄 License

MIT License
