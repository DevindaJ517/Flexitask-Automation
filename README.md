# Flexitask-Automation 🚀

**Social Media Automation Microservice for Job Posting Platform**

This agentic microservice automatically distributes job listings to WhatsApp groups, Facebook groups, and Telegram channels when an admin posts a job on your platform. It runs as an independent service with a REST API.

## 📋 Features

- **Multi-Platform Distribution**: Automatically posts to WhatsApp, Facebook, and Telegram
- **RESTful API**: Simple API endpoint to trigger job posting
- **Async Processing**: Non-blocking job distribution
- **Rich Formatting**: Professionally formatted job posts with emojis and structure
- **Error Handling**: Robust error handling and logging
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Configurable**: Environment-based configuration for different platforms

## 🛠 Tech Stack

- Python 3.11
- FastAPI (Web Framework)
- Twilio (WhatsApp Business API Integration)
- Facebook Graph API (Facebook Groups)
- python-telegram-bot (Telegram Channels)
- Docker & Docker Compose

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, for containerized deployment)
- API credentials for:
  - Twilio (for WhatsApp)
  - Facebook Graph API
  - Telegram Bot

### 1. Clone the Repository

```bash
git clone https://github.com/DevindaJ517/Flexitask-Automation.git
cd Flexitask-Automation
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True

# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_GROUP_NUMBER=whatsapp:+1234567890

# Facebook Configuration
FACEBOOK_ACCESS_TOKEN=your_facebook_page_access_token
FACEBOOK_GROUP_ID=your_facebook_group_id

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=@your_channel_username
# OR use numeric ID: TELEGRAM_CHANNEL_ID=-1001234567890
```

### 3. Option A: Run with Docker (Recommended)

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

The service will be available at `http://localhost:8000`

### 3. Option B: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔐 Getting API Credentials

### WhatsApp (Twilio)

1. Sign up at [Twilio Console](https://www.twilio.com/console)
2. Get your **Account SID** and **Auth Token** from the dashboard
3. Enable WhatsApp in Twilio Console
4. Use the Twilio WhatsApp Sandbox number: `whatsapp:+14155238886`
5. Join your group to the sandbox by sending the join code

### Facebook Graph API

1. Create a Facebook App at [Facebook Developers](https://developers.facebook.com/)
2. Add "Groups API" product
3. Generate a **Page Access Token** with `groups_access_member_info` and `publish_to_groups` permissions
4. Get your Facebook Group ID from the group URL or Graph API Explorer

### Telegram Bot

1. Talk to [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the **Bot Token** provided
4. Add your bot to your channel as an administrator
5. Get channel ID (use `@username` or numeric ID)

---

## 📡 API Documentation

### Health Check

**GET** `/`

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Flexitask Social Media Automation",
  "version": "1.0.0"
}
```

### Post Job to Social Media

**POST** `/api/post-job`

Distributes a job posting to all configured social media platforms.

**Request Body:**

```json
{
  "title": "Senior Software Engineer",
  "companyName": "TechCorp Inc.",
  "workLocationType": "HYBRID",
  "employmentType": "FULL_TIME",
  "category": "IT & Software",
  "country": "United States",
  "city": "San Francisco",
  "experienceYears": "TWO_PLUS",
  "isInternship": false,
  "linkedInApplyURL": "https://www.linkedin.com/jobs/view/123456789",
  "uniqueDescription": "We are looking for a talented Senior Software Engineer...",
  "jobImage": "https://example.com/job-image.jpg"
}
```

**Required Fields:**
- `title` (string): Job title
- `companyName` (string): Company name
- `workLocationType` (string): `ONSITE`, `REMOTE`, or `HYBRID`
- `employmentType` (string): `FULL_TIME`, `PART_TIME`, or `CONTRACT`
- `linkedInApplyURL` (string): LinkedIn job posting URL

**Optional Fields:**
- `category` (string): Job category
- `country` (string): Country name
- `city` (string): City name
- `experienceYears` (string): `ONE_PLUS`, `TWO_PLUS`, `FIVE_PLUS`
- `isInternship` (boolean): Whether it's an internship
- `uniqueDescription` (string): Job description
- `jobImage` (string): URL to job image

**Example cURL:**

```bash
curl -X POST http://localhost:8000/api/post-job \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Software Engineer",
    "companyName": "TechCorp Inc.",
    "workLocationType": "HYBRID",
    "employmentType": "FULL_TIME",
    "linkedInApplyURL": "https://www.linkedin.com/jobs/view/123456789"
  }'
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Job posted successfully to all platforms",
  "results": {
    "whatsapp": {
      "success": true,
      "message_sid": "SM1234567890abcdef"
    },
    "facebook": {
      "success": true,
      "post_id": "123456789_987654321"
    },
    "telegram": {
      "success": true,
      "message_id": 12345
    }
  }
}
```

**Error Response (500):**

```json
{
  "success": false,
  "message": "Failed to post to some platforms",
  "results": {
    "whatsapp": {
      "success": false,
      "error": "Invalid phone number"
    },
    "facebook": {
      "success": true,
      "post_id": "123456789_987654321"
    },
    "telegram": {
      "success": true,
      "message_id": 12345
    }
  }
}
```

---

## 🔗 Frontend Integration

### Integration with Next.js Form

Update your `/api/jobs/create` API route to call the automation service:

```typescript
// app/api/jobs/create/route.ts

export async function POST(request: Request) {
  try {
    const formData = await request.formData()
    
    // ... your existing job creation logic ...
    
    // After successfully creating the job, call the automation service
    const jobData = {
      title: formData.get('title'),
      companyName: formData.get('companyName'),
      workLocationType: formData.get('workLocationType'),
      employmentType: formData.get('employmentType'),
      category: formData.get('categoryText') || 'General',
      country: formData.get('countryText') || 'Remote',
      city: formData.get('cityText') || '',
      experienceYears: formData.get('experienceYears') || null,
      isInternship: formData.get('isInternship') === 'on',
      linkedInApplyURL: formData.get('linkedInApplyURL'),
      uniqueDescription: formData.get('uniqueDescription'),
      jobImage: jobImageUrl || null // URL to the uploaded image
    }

    // Call the automation microservice
    const AUTOMATION_SERVICE_URL = process.env.AUTOMATION_SERVICE_URL || 'http://localhost:8000'
    
    try {
      const response = await fetch(`${AUTOMATION_SERVICE_URL}/api/post-job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData)
      })

      if (response.ok) {
        console.log('✅ Job posted to social media successfully')
      } else {
        console.error('⚠️ Failed to post to social media:', await response.text())
      }
    } catch (error) {
      // Don't fail the job creation if social media posting fails
      console.error('⚠️ Social media automation error:', error)
    }

    return NextResponse.json({ success: true, jobId: newJob.id })
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
```

### Environment Variable

Add to your Next.js `.env.local`:

```env
AUTOMATION_SERVICE_URL=http://localhost:8000
# In production: https://your-automation-service.com
```

### Testing with Your Form

1. Start the automation service:
   ```bash
   docker-compose up -d
   ```

2. Submit a job through your form at `/post-job`

3. Check the service logs:
   ```bash
   docker-compose logs -f
   ```

4. Verify posts appear on WhatsApp, Facebook, and Telegram

---

## 🧪 Testing the API

Use the included test script:

```bash
python test_api.py
```

Or test manually with cURL:

```bash
# Health check
curl http://localhost:8000/

# Post a job
curl -X POST http://localhost:8000/api/post-job \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Full Stack Developer",
    "companyName": "StartupXYZ",
    "workLocationType": "REMOTE",
    "employmentType": "FULL_TIME",
    "category": "Software Development",
    "country": "United States",
    "linkedInApplyURL": "https://www.linkedin.com/jobs/view/123456789",
    "uniqueDescription": "Join our amazing team!"
  }'
```

---

## 📁 Project Structure

```
Flexitask-Automation/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic models
│   ├── config.py               # Configuration loader
│   └── services/
│       ├── __init__.py
│       ├── whatsapp_service.py # WhatsApp integration
│       ├── facebook_service.py # Facebook integration
│       └── telegram_service.py # Telegram integration
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── test_api.py                # API testing script
└── README.md                  # This file
```

---

## 🚀 Deployment

### Deploy with Docker

```bash
# Build the image
docker build -t flexitask-automation .

# Run the container
docker run -d \
  --name flexitask-automation \
  -p 8000:8000 \
  --env-file .env \
  flexitask-automation
```

### Deploy to Cloud Platforms

#### **Railway / Render / Fly.io**
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy automatically from main branch

#### **AWS ECS / Google Cloud Run**
1. Push Docker image to registry (ECR/GCR)
2. Create service with environment variables
3. Configure health check endpoint: `/`

#### **Heroku**
```bash
heroku create flexitask-automation
heroku config:set TWILIO_ACCOUNT_SID=xxx ...
git push heroku main
```

---

## 📝 Message Format Example

**Important:** The service shares only a **brief summary with key details and the apply link** - NOT the full job description. This keeps posts concise and encourages click-throughs to LinkedIn.

When a job is posted, the following formatted message is sent:

```
🎯 **New Job Opportunity!**

**Senior Software Engineer**
🏢 TechCorp Inc.

📍 San Francisco, United States
💼 Full Time | Hybrid
🏷️ IT & Software
📊 Experience: 2+ years

🔗 **Apply now:** https://www.linkedin.com/jobs/view/123456789
```

**What's included:** Job title, company, location, employment type, category, experience level  
**What's NOT included:** Full description, requirements, benefits

See [MESSAGE_FORMAT.md](MESSAGE_FORMAT.md) for more examples and details.

---

## 🛠 Troubleshooting

### WhatsApp not working
- Verify Twilio credentials
- Check if WhatsApp number is verified
- Ensure recipient has joined Twilio sandbox

### Facebook posts failing
- Verify Page Access Token permissions
- Check if bot is admin of the group
- Ensure token hasn't expired

### Telegram messages not sending
- Verify bot token is correct
- Check if bot is admin in the channel
- Use correct channel ID format (`@username` or `-1001234567890`)

### Service won't start
- Check `.env` file exists and is properly formatted
- Verify all required environment variables are set
- Check port 8000 is not already in use

---

## 📄 License

MIT License - feel free to use this project for your job posting platform!

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues and questions, please open an issue on GitHub or contact the maintainer.

---

**Built with ❤️ for automated job distribution**