# Setup Guide

## Prerequisites

1. **Python 3.9+** installed
2. **GitHub Account** with a Personal Access Token
3. **OpenAI API Key** (or compatible LLM API)

## Step 1: Environment Setup

### 1.1 Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configuration

### 2.1 Create `.env` file

Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 2.2 Configure Environment Variables

Edit `.env` and set the following:

#### Student Secret
```
STUDENT_SECRET=your-unique-secret-here
```
This should match what you submit in the Google Form.

#### OpenAI API Key
```
OPENAI_API_KEY=sk-...
```
Get this from: https://platform.openai.com/api-keys

#### GitHub Personal Access Token
```
GITHUB_TOKEN=ghp_...
```

To create a GitHub token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "TDS Project")
4. Select scopes:
   - `repo` (all)
   - `workflow`
   - `admin:repo_hook`
5. Click "Generate token"
6. Copy the token (you won't see it again!)

#### GitHub Username
```
GITHUB_USERNAME=your-github-username
```

## Step 3: Run the Application

### 3.1 Start the API Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 3.2 Verify It's Running

Open your browser and go to:
```
http://localhost:8000
```

You should see:
```json
{
  "status": "running",
  "service": "LLM Code Deployment API",
  "version": "1.0.0"
}
```

## Step 4: Testing

### 4.1 Test with cURL (Round 1)

Create a test file `test_request.json`:

```json
{
  "email": "student@example.com",
  "secret": "your-secret-here",
  "task": "test-captcha-solver-001",
  "round": 1,
  "nonce": "test-nonce-123",
  "brief": "Create a simple captcha solver that displays an image from ?url=... parameter and shows a text input for the solution.",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page has input field for solution"
  ],
  "evaluation_url": "https://httpbin.org/post",
  "attachments": []
}
```

Send the request:

```bash
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### 4.2 Check Status

```bash
curl http://localhost:8000/status/test-captcha-solver-001
```

### 4.3 Monitor Logs

Watch the console output for:
- ✅ Request received
- ✅ Attachments saved
- ✅ App generated
- ✅ GitHub repo created
- ✅ GitHub Pages enabled
- ✅ Evaluation notification sent

## Step 5: Deploy for Production

### 5.1 Using ngrok (for testing)

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```

This gives you a public URL like `https://abc123.ngrok.io`

Your API endpoint will be: `https://abc123.ngrok.io/request`

### 5.2 Using a Cloud Service

Deploy to:
- **Heroku**: Use `Procfile` with `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Connect GitHub repo, set environment variables
- **Render**: Deploy as Web Service, set environment variables
- **AWS/GCP/Azure**: Use container or serverless deployment

## Troubleshooting

### Error: "Configuration errors: STUDENT_SECRET not set"
- Make sure `.env` file exists and has all required variables
- Restart the server after editing `.env`

### Error: "Invalid secret"
- Check that the `secret` in your request matches `STUDENT_SECRET` in `.env`

### Error: "GitHub API rate limit"
- Wait for rate limit to reset
- Use a different GitHub token
- Check token has correct permissions

### Error: "OpenAI API error"
- Verify API key is correct
- Check you have credits/quota available
- Try a different model (edit `llm_generator.py`)

### Pages not loading (404)
- Wait 1-2 minutes for GitHub Pages to deploy
- Check repo settings → Pages is enabled
- Verify `index.html` exists in repo root

## Next Steps

1. Submit your API endpoint URL to the Google Form
2. Submit your `STUDENT_SECRET` to the Google Form
3. Wait for instructor to send task request
4. Monitor your logs and GitHub repos
5. Check evaluation results after deadline

## Security Notes

- ⚠️ Never commit `.env` file to git
- ⚠️ Never share your API keys publicly
- ⚠️ Keep your `STUDENT_SECRET` confidential
- ⚠️ Use environment variables in production
- ⚠️ Consider using GitHub Secrets for CI/CD
