# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install (2 minutes)

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure (2 minutes)

```bash
# Create .env file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edit `.env` and add:
```env
STUDENT_SECRET=my-unique-secret-123
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=your-username
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- GitHub: Settings → Developer settings → Personal access tokens → Generate new token (classic)
  - Select scopes: `repo`, `workflow`

## Step 3: Run (1 minute)

```bash
python main.py
```

Server starts at `http://localhost:8000`

## Step 4: Test

### Quick Test
```bash
# In another terminal
python test_client.py
```

### Manual Test
```bash
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "my-unique-secret-123",
    "task": "hello-world-001",
    "round": 1,
    "nonce": "test-123",
    "brief": "Create a simple hello world page with a button",
    "checks": ["Has MIT license", "README exists"],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

## What Happens Next?

1. ✅ API receives request and returns 200
2. 🤖 LLM generates web app
3. 📦 Creates GitHub repo
4. 🌐 Deploys to GitHub Pages
5. 📤 Notifies evaluation URL

Check logs for progress!

## Check Status

```bash
curl http://localhost:8000/status/hello-world-001
```

## Common Issues

### "Configuration errors"
→ Make sure `.env` file exists with all variables

### "Invalid secret"
→ Secret in request must match `STUDENT_SECRET` in `.env`

### "GitHub API error"
→ Check token has `repo` and `workflow` scopes

### "OpenAI API error"
→ Verify API key and account has credits

## Deploy to Production

### Option 1: ngrok (Quick)
```bash
ngrok http 8000
```
Use the ngrok URL as your API endpoint.

### Option 2: Render (Recommended)
1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect your repo
4. Add environment variables
5. Deploy!

## Next Steps

1. ✅ Test locally
2. 🌐 Deploy to cloud
3. 📝 Submit API URL to Google Form
4. 🎯 Wait for evaluation

## Need Help?

- 📖 Read `SETUP.md` for detailed instructions
- 📋 Check `TODO.md` for complete checklist
- 📚 See `PROJECT_README.md` for full documentation

---

**You're ready to go! 🎉**
