# 📝 Message Format Example

## What Gets Shared to Social Media

The automation service now shares **only a brief summary with key job details and the apply link**, not the full job description. This keeps social media posts concise and encourages users to click through to LinkedIn.

## Example Message Format

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

## What's Included in the Message

✅ **Job Title** - Bold and prominent  
✅ **Company Name** - With building emoji  
✅ **Location** - City and country (if provided)  
✅ **Employment Type** - Full Time, Part Time, or Contract  
✅ **Work Location Type** - Onsite, Remote, or Hybrid  
✅ **Category** - Job category (if provided)  
✅ **Experience Requirement** - Years of experience (if specified)  
✅ **Internship Badge** - If it's an internship position  
✅ **Apply Link** - Direct link to LinkedIn job posting  

## What's NOT Included

❌ Full job description  
❌ Detailed requirements list  
❌ Benefits information  
❌ Salary information  

The full details are on LinkedIn - the social media post is just a teaser to drive traffic!

## Message Variations

### With All Optional Fields:
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

### Minimal (Required Fields Only):
```
🎯 **New Job Opportunity!**

**Full Stack Developer**
🏢 StartupXYZ

💼 Full Time | Remote

🔗 **Apply now:** https://www.linkedin.com/jobs/view/987654321
```

### With Internship Badge:
```
🎯 **New Job Opportunity!**

**Marketing Intern**
🏢 Creative Agency Ltd.

📍 New York, United States
💼 Full Time | Onsite
🏷️ Marketing
🎓 Internship Position

🔗 **Apply now:** https://www.linkedin.com/jobs/view/555555555
```

## Testing the Message Format

You can preview what the message will look like without actually posting it:

```bash
curl -X POST http://localhost:8000/api/preview-message \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Your Job Title",
    "companyName": "Your Company",
    "workLocationType": "REMOTE",
    "employmentType": "FULL_TIME",
    "linkedInApplyURL": "https://www.linkedin.com/jobs/view/123456789"
  }'
```

## Benefits of This Approach

1. **Clean & Concise** - Easy to read on mobile devices
2. **Drives Traffic** - Users click through to LinkedIn for full details
3. **Professional** - Uses emojis tastefully for visual appeal
4. **Fast to Read** - Key info at a glance
5. **No Spam** - Doesn't clutter feeds with long text
6. **Click-Through** - Encourages engagement with the actual job posting

---

**The LinkedIn URL contains all the full details - the social media post is just to announce the opportunity! 🚀**
