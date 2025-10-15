---
title: LLM Code Deployment
emoji: 👁
colorFrom: purple
colorTo: green
sdk: docker
pinned: false
---

# LLM Code Deployment API

Automated web application generation and deployment system for TDS 2025 Term 3 Project 1.

## 🎯 Overview

This API receives task requests, generates web applications using LLM, deploys them to GitHub Pages, and notifies evaluation endpoints.

## 📡 API Endpoints

### Health Check
```bash
GET /
```
Returns API status and version.

### Submit Task
```bash
POST /request
```
**Request Body:**
```json
{
  "email": "student@example.com",
  "secret": "your-secret-key",
  "task": "task-id",
  "round": 1,
  "nonce": "unique-nonce",
  "brief": "Task description",
  "checks": ["requirement1", "requirement2"],
  "evaluation_url": "https://evaluation-endpoint.com",
  "attachments": []
}
```

**Response:**
```json
{
  "status": "accepted",
  "message": "Task accepted for processing",
  "task": "task-id",
  "round": 1
}
```

### Check Status
```bash
GET /status/{task_id}
```
Returns processing status for a task.

## 🔧 Configuration

Required environment variables (set in Space Settings → Repository Secrets):

- `STUDENT_SECRET` - Your unique authentication secret
- `OPENAI_API_KEY` - OpenAI API key for LLM generation
- `GITHUB_TOKEN` - GitHub Personal Access Token (repo + workflow scopes)
- `GITHUB_USERNAME` - Your GitHub username

## 🚀 How It Works

1. **Receive Request** - API receives task via POST /request
2. **Immediate Response** - Returns 200 OK immediately
3. **Background Processing**:
   - Decode attachments
   - Generate app using LLM
   - Create GitHub repository
   - Deploy to GitHub Pages
4. **Notify** - Send completion notification to evaluation URL

## 📦 Features

- ✅ Async background task processing
- ✅ Automatic GitHub repo creation
- ✅ GitHub Pages deployment
- ✅ Retry logic with exponential backoff
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ **Automated security scanning** for secrets
- ✅ Multi-round support (Round 1, 2, N)
- ✅ Real-time status tracking
- ✅ Interactive test client
- ✅ One-command startup with validation

## 🔒 Security

- ✅ Secret-based authentication
- ✅ Environment variable configuration
- ✅ No hardcoded credentials
- ✅ **Automated secret scanning** (15+ patterns)
- ✅ Pattern detection for API keys, tokens, passwords
- ✅ Masked logging for sensitive data
- ✅ Pre-deployment security checks

## 📚 Documentation

For detailed setup and usage instructions, see the documentation files in the root directory:

- **`PROJECT_SUMMARY.md`** - Complete project overview and status
- **`QUICKSTART.md`** - Quick start guide (5 minutes)
- **`SETUP.md`** - Detailed local setup instructions
- **`USAGE_GUIDE.md`** - API usage and troubleshooting
- **`ARCHITECTURE.md`** - System design and components
- **`DEPLOYMENT_CHECKLIST.md`** - Deployment guide

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Validate setup
python validate_setup.py

# 4. Start server
python start.py
# Or on Windows: start.bat

# 5. Test API
python test/test_client.py
# Or on Windows: run_tests.bat
```

## 🐛 Troubleshooting

**API not responding?**
- Check Space logs in Hugging Face
- Verify all environment variables are set
- Ensure GitHub token has correct permissions

**GitHub deployment failing?**
- Verify GitHub token is valid
- Check GitHub username is correct
- Ensure repo doesn't already exist

**LLM generation failing?**
- Verify OpenAI API key is valid
- Check API credits/quota
- Review logs for specific errors

## 📞 Support

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-11
