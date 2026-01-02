# FlexiTask Automation - Free Cloud Deployment Guide

## Overview

This guide explains how to deploy the FlexiTask Automation server on **Render** (free tier) with **Upstash Redis** (free tier) for completely free hosting.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Render (Free Tier)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              FastAPI + APScheduler                     │  │
│  │  - Monitors jobs every 60 seconds                      │  │
│  │  - Posts to Telegram automatically                     │  │
│  │  - REST API for manual control                         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌─────────────────────┐              ┌─────────────────────┐
│   Supabase (Free)   │              │   Upstash Redis     │
│   - Job database    │              │   - Job tracking    │
│   - PostgreSQL      │              │   - Last check time │
└─────────────────────┘              └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   Telegram Bot      │
│   - Channel posts   │
└─────────────────────┘
```

---

## Step 1: Set Up Upstash Redis (Free)

1. Go to [Upstash](https://upstash.com/) and create a free account
2. Create a new Redis database:
   - Click "Create Database"
   - Name: `flexitask-automation`
   - Region: Choose closest to your users
   - Type: Regional (free)
3. Copy the **Redis URL** (format: `rediss://default:xxx@xxx.upstash.io:6379`)

**Free tier includes:**
- 10,000 commands/day
- 256MB storage
- TLS encryption

---

## Step 2: Create Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Save your **Bot Token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Create a Telegram channel for job posts
5. Add your bot as an administrator to the channel
6. Get your **Channel ID**:
   - For public channels: Use `@channelname` format
   - For private channels: Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)

---

## Step 3: Get Supabase Credentials

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your FlexiTask project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL**: `https://qdtmbfuwonsdmfhtasqp.supabase.co`
   - **anon/public key**: (your API key)

---

## Step 4: Deploy to Render

### Option A: One-Click Deploy (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect `render.yaml` and configure everything

### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `flexitask-automation`
   - **Region**: Oregon (or nearest)
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### Add Environment Variables

In Render dashboard, go to your service → "Environment" and add:

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | `https://qdtmbfuwonsdmfhtasqp.supabase.co` |
| `SUPABASE_KEY` | Your Supabase anon key |
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHANNEL_ID` | Your channel ID (e.g., `@mychannelname`) |
| `REDIS_URL` | Your Upstash Redis URL |
| `JOB_SITE_URL` | `https://flexi-task-zeta.vercel.app` |
| `POLLING_INTERVAL_SECONDS` | `60` |

---

## Step 5: Verify Deployment

Once deployed, your service will be available at:
`https://flexitask-automation.onrender.com`

### Test the endpoints:

```bash
# Health check
curl https://flexitask-automation.onrender.com/health

# Check scheduler status
curl https://flexitask-automation.onrender.com/api/scheduler/status

# Manually trigger a job check
curl -X POST https://flexitask-automation.onrender.com/api/scheduler/trigger
```

---

## Free Tier Limitations

### Render Free Tier:
- ✅ 750 hours/month (enough for 1 service 24/7)
- ✅ Auto-deploy from GitHub
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ Cold starts take ~30 seconds

### Keeping the Service Active

To prevent spin-down, set up a free cron job pinger:

1. Go to [cron-job.org](https://cron-job.org/) (free)
2. Create a new cron job:
   - URL: `https://flexitask-automation.onrender.com/health`
   - Schedule: Every 10 minutes
   - Method: GET

This will keep your service active 24/7.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/api/scheduler/status` | GET | Scheduler status |
| `/api/scheduler/trigger` | POST | Manual job check |
| `/api/jobs/new` | GET | List new jobs |
| `/api/jobs/{id}` | GET | Get job details |
| `/api/share/{id}` | POST | Share specific job |
| `/api/stats` | GET | Statistics |

---

## Monitoring

### View Logs
In Render dashboard → Your service → "Logs"

### Check Stats
```bash
curl https://flexitask-automation.onrender.com/api/stats
```

---

## Troubleshooting

### Service not starting?
- Check environment variables are set correctly
- View logs in Render dashboard

### Jobs not posting to Telegram?
- Verify bot token is correct
- Ensure bot is admin in the channel
- Check channel ID format

### Redis connection failed?
- Verify Upstash URL is correct
- Ensure URL starts with `rediss://` (with SSL)

### Supabase connection failed?
- Use the REST API URL, not the direct database URL
- Verify the anon key is correct

---

## Cost Summary

| Service | Plan | Cost |
|---------|------|------|
| Render | Free | $0 |
| Upstash Redis | Free | $0 |
| Supabase | Free | $0 |
| Telegram Bot | Free | $0 |
| **Total** | | **$0/month** |

---

## Upgrading (Optional)

If you need more reliability later:

- **Render Starter ($7/mo)**: No spin-down, faster response
- **Upstash Pay-as-you-go**: More commands if needed
- **Supabase Pro ($25/mo)**: More database resources
