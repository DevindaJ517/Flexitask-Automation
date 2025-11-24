# Frontend Integration Guide

This guide shows you how to integrate the Flexitask-Automation microservice with your Next.js job posting application.

## Overview

When an admin posts a job through your frontend form, your backend API will:
1. Create the job in your database
2. Upload the job image (if provided)
3. Call the Flexitask-Automation service to distribute the job to social media
4. Return success to the frontend

## Step 1: Add Environment Variable

In your Next.js project root, add to `.env.local`:

```env
# Flexitask Automation Service
AUTOMATION_SERVICE_URL=http://localhost:8000
```

For production:
```env
AUTOMATION_SERVICE_URL=https://your-automation-service-domain.com
```

## Step 2: Update Your Job Creation API Route

Here's how to integrate with your existing `/api/jobs/create/route.ts`:

```typescript
// app/api/jobs/create/route.ts
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const formData = await request.formData()
    
    // Extract form data
    const title = formData.get('title') as string
    const companyName = formData.get('companyName') as string
    const workLocationType = formData.get('workLocationType') as string
    const employmentType = formData.get('employmentType') as string
    const linkedInApplyURL = formData.get('linkedInApplyURL') as string
    const uniqueDescription = formData.get('uniqueDescription') as string
    const isPublished = formData.get('isPublished') === 'on'
    
    // Optional fields
    const category = formData.get('categoryText') as string || formData.get('categoryId') as string
    const country = formData.get('countryText') as string || formData.get('countryId') as string
    const city = formData.get('cityText') as string || formData.get('cityId') as string
    const experienceYears = formData.get('experienceYears') as string
    const isInternship = formData.get('isInternship') === 'on'
    
    // Handle image upload
    const jobImageFile = formData.get('jobImage') as File
    let jobImageUrl = null
    
    if (jobImageFile && jobImageFile.size > 0) {
      // Upload to your storage (S3, Cloudinary, etc.)
      // jobImageUrl = await uploadImageToStorage(jobImageFile)
      // For now, this is a placeholder
      jobImageUrl = 'https://example.com/job-images/placeholder.jpg'
    }
    
    // 1. Create job in your database
    const newJob = await createJobInDatabase({
      title,
      companyName,
      workLocationType,
      employmentType,
      category,
      country,
      city,
      experienceYears,
      isInternship,
      linkedInApplyURL,
      uniqueDescription,
      jobImageUrl,
      isPublished
    })
    
    // 2. If published, call automation service to post to social media
    if (isPublished) {
      const AUTOMATION_SERVICE_URL = process.env.AUTOMATION_SERVICE_URL || 'http://localhost:8000'
      
      const automationPayload = {
        title,
        companyName,
        workLocationType,
        employmentType,
        category: category || 'General',
        country: country || 'Remote',
        city: city || '',
        experienceYears: experienceYears || null,
        isInternship,
        linkedInApplyURL,
        uniqueDescription,
        jobImage: jobImageUrl
      }
      
      try {
        console.log('📤 Sending job to automation service...')
        
        const response = await fetch(`${AUTOMATION_SERVICE_URL}/api/post-job`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(automationPayload)
        })

        if (response.ok) {
          const result = await response.json()
          console.log('✅ Job posted to social media successfully:', result)
          
          // Optionally update job record with social media post IDs
          // await updateJobWithSocialMediaIds(newJob.id, result.results)
        } else {
          const errorText = await response.text()
          console.error('⚠️ Failed to post to social media:', errorText)
          // Continue anyway - don't fail job creation if social media fails
        }
      } catch (error) {
        // Network error or service unavailable
        console.error('⚠️ Social media automation error:', error)
        // Continue anyway - job is created, social media is a bonus feature
      }
    }
    
    return NextResponse.json({ 
      success: true, 
      jobId: newJob.id,
      message: 'Job created successfully'
    })
    
  } catch (error: any) {
    console.error('❌ Error creating job:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to create job' }, 
      { status: 500 }
    )
  }
}

// Helper function placeholder - implement based on your database
async function createJobInDatabase(jobData: any) {
  // Your Prisma/database logic here
  // const job = await prisma.job.create({ data: jobData })
  // return job
  
  return { 
    id: 'job-123', 
    ...jobData 
  }
}
```

## Step 3: Handle Non-Blocking Requests

For better user experience, consider making the social media posting non-blocking:

### Option A: Fire and Forget (Simple)

```typescript
// Don't await the automation service call
fetch(`${AUTOMATION_SERVICE_URL}/api/post-job`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(automationPayload)
}).catch(err => console.error('Social media automation error:', err))

// Return immediately
return NextResponse.json({ success: true, jobId: newJob.id })
```

### Option B: Background Job Queue (Recommended for Production)

Use a job queue like BullMQ, Inngest, or Trigger.dev:

```typescript
import { inngest } from '@/lib/inngest'

// Create job in database
const newJob = await createJobInDatabase(jobData)

// Queue background job for social media posting
await inngest.send({
  name: 'job/post-to-social-media',
  data: {
    jobId: newJob.id,
    ...automationPayload
  }
})

// Return immediately
return NextResponse.json({ success: true, jobId: newJob.id })
```

## Step 4: Error Handling

Add proper error handling and retry logic:

```typescript
async function postJobToSocialMedia(payload: any, retries = 3) {
  const AUTOMATION_SERVICE_URL = process.env.AUTOMATION_SERVICE_URL
  
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await fetch(`${AUTOMATION_SERVICE_URL}/api/post-job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      })

      if (response.ok) {
        return await response.json()
      }
      
      if (response.status >= 500 && attempt < retries) {
        // Retry on server errors
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt))
        continue
      }
      
      throw new Error(`HTTP ${response.status}: ${await response.text()}`)
      
    } catch (error) {
      if (attempt === retries) {
        throw error
      }
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt))
    }
  }
}
```

## Step 5: Frontend User Feedback

Update your frontend to show social media posting status:

```typescript
// In your PostJobForm component
const [socialMediaStatus, setSocialMediaStatus] = useState<{
  posting: boolean
  success?: boolean
  message?: string
}>({ posting: false })

const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault()
  setIsSubmitting(true)
  setSocialMediaStatus({ posting: true })
  
  const formData = new FormData(e.currentTarget)
  // ... prepare formData ...
  
  try {
    const response = await fetch('/api/jobs/create', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Failed to create job')
    }
    
    const result = await response.json()
    
    setSocialMediaStatus({
      posting: false,
      success: true,
      message: 'Job posted to social media!'
    })
    
    // Redirect after short delay to show success message
    setTimeout(() => {
      router.push('/')
      router.refresh()
    }, 1500)
    
  } catch (err: any) {
    setError(err.message)
    setSocialMediaStatus({ posting: false, success: false })
    setIsSubmitting(false)
  }
}
```

## Step 6: Testing the Integration

### 1. Start the Automation Service

```bash
cd /path/to/Flexitask-Automation
docker-compose up -d
```

### 2. Verify Service is Running

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Flexitask Social Media Automation",
  "version": "1.0.0"
}
```

### 3. Test from Your Frontend

1. Navigate to your job posting form
2. Fill in all required fields
3. Check "Publish immediately"
4. Submit the form
5. Check automation service logs:

```bash
docker-compose logs -f
```

### 4. Verify Posts on Social Media

- Check your WhatsApp group
- Check your Facebook group
- Check your Telegram channel

## Production Deployment Checklist

- [ ] Set up automation service on production server
- [ ] Update `AUTOMATION_SERVICE_URL` in production environment
- [ ] Configure all API credentials in production `.env`
- [ ] Set up monitoring and alerting for service health
- [ ] Implement retry logic for failed posts
- [ ] Add logging for social media post IDs
- [ ] Test with staging environment first
- [ ] Set up rate limiting if needed
- [ ] Configure CORS if service is on different domain
- [ ] Add authentication/API key if exposing publicly

## Troubleshooting

### "Connection refused" error
- Ensure automation service is running: `docker-compose ps`
- Check service URL is correct in `.env.local`
- Verify port 8000 is accessible

### "Job created but not posted to social media"
- Check automation service logs: `docker-compose logs`
- Verify API credentials are configured
- Check service health: `curl http://localhost:8000/`

### "Timeout" errors
- Increase timeout in fetch call
- Check service performance: `docker stats`
- Consider making the call non-blocking

## Support

For issues with the automation service:
- Check service logs: `docker-compose logs -f`
- Test the API directly: `python test_api.py`
- Open an issue on GitHub

---

**Ready to automate your job postings! 🚀**
