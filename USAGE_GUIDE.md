# LLM Code Deployment - Usage Guide

## Quick Start (Windows)

### 1. First Time Setup

1. **Install Python 3.10+**
   - Download from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     ```
     STUDENT_SECRET=your-secret-from-google-form
     OPENAI_API_KEY=sk-your-openai-key
     GITHUB_TOKEN=ghp_your-github-token
     GITHUB_USERNAME=your-github-username
     ```

4. **Validate Setup**
   ```bash
   python validate_setup.py
   ```

### 2. Running the Server

**Option A: Using the startup script (Recommended)**
```bash
python start.py
```
Or simply double-click `start.bat`

**Option B: Manual start**
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 7860 --reload
```

### 3. Testing the API

**Option A: Using the test client**
```bash
python test\test_client.py
```
Or double-click `run_tests.bat`

**Option B: Using curl**
```bash
curl -X POST http://localhost:7860/request \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

**Option C: Using the API docs**
- Open http://localhost:7860/docs in your browser
- Use the interactive Swagger UI

## API Endpoints

### Health Check
```http
GET /
```
Returns API status and version.

**Response:**
```json
{
  "status": "running",
  "service": "LLM Code Deployment API",
  "version": "1.0.0"
}
```

### Submit Task (Round 1)
```http
POST /request
```

**Request Body:**
```json
{
  "email": "student@example.com",
  "secret": "your-secret-key",
  "task": "task-001",
  "round": 1,
  "nonce": "unique-nonce-123",
  "brief": "Create a web page that displays weather information...",
  "checks": [
    "Page displays weather data",
    "Has search functionality",
    "Responsive design"
  ],
  "evaluation_url": "https://evaluation-endpoint.com/notify",
  "attachments": []
}
```

**Response:**
```json
{
  "status": "accepted",
  "message": "Task task-001 round 1 accepted for processing",
  "task": "task-001",
  "round": 1
}
```

### Submit Revision (Round 2)
Same as Round 1, but with `"round": 2` and updated brief.

### Check Task Status
```http
GET /status/{task_id}
```

**Response:**
```json
{
  "task-001-1": {
    "status": "completed",
    "completed_at": "2025-10-11T09:30:00",
    "repo_url": "https://github.com/username/task-001",
    "pages_url": "https://username.github.io/task-001/",
    "notification_sent": true
  }
}
```

## Workflow

### Round 1: Build and Deploy

1. **API receives request** → Returns 200 OK immediately
2. **Background processing starts:**
   - Decodes attachments (if any)
   - Generates app using OpenAI GPT-4
   - Scans code for secrets
   - Creates GitHub repository
   - Adds LICENSE and README
   - Pushes code
   - Enables GitHub Pages
   - Waits for deployment
3. **Sends notification** to evaluation_url with:
   - repo_url
   - commit_sha
   - pages_url

**Timeline:** ~60-90 seconds

### Round 2: Revision

1. **API receives revision request** → Returns 200 OK immediately
2. **Background processing:**
   - Generates updated app
   - Scans for secrets
   - Updates existing repository
   - Waits for redeployment
3. **Sends notification** with updated details

**Timeline:** ~60-90 seconds

## Troubleshooting

### Server won't start

**Problem:** `Configuration error: OPENAI_API_KEY not set`
- **Solution:** Create `.env` file with your API keys (copy from `.env.example`)

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
- **Solution:** Install dependencies: `pip install -r requirements.txt`

**Problem:** `Port 7860 already in use`
- **Solution:** Change port in `.env`: `PORT=8000`

### GitHub deployment fails

**Problem:** `Bad credentials`
- **Solution:** Check your `GITHUB_TOKEN` in `.env`
- Make sure token has `repo` and `workflow` scopes

**Problem:** `Repository already exists`
- **Solution:** The system auto-deletes existing repos. If it fails, manually delete the repo on GitHub.

**Problem:** `GitHub Pages not deploying`
- **Solution:** 
  - Check repository settings → Pages
  - Ensure source is set to `main` branch, `/` root
  - Wait 2-3 minutes for initial deployment

### LLM generation fails

**Problem:** `Invalid API key`
- **Solution:** Verify your OpenAI API key starts with `sk-`

**Problem:** `Rate limit exceeded`
- **Solution:** Wait a few minutes or upgrade your OpenAI plan

**Problem:** `Generated app is too simple`
- **Solution:** The system uses a fallback template if LLM fails. Check logs for errors.

### Notification fails

**Problem:** `Connection timeout to evaluation_url`
- **Solution:** System retries with exponential backoff (1, 2, 4, 8, 16 seconds)
- Check if evaluation_url is accessible

## Security Features

### Secret Scanning
The system automatically scans generated code for:
- API keys
- Tokens
- Passwords
- Private keys
- Database URLs

**Patterns detected:**
- OpenAI API keys (`sk-...`)
- GitHub tokens (`ghp_...`, `gho_...`, `ghs_...`)
- AWS credentials
- Bearer tokens
- Generic API keys and secrets

**Action taken:**
- Logs warnings if secrets detected
- Continues deployment (with warning)
- In production, consider auto-sanitizing or blocking

### Best Practices
1. Never hardcode secrets in generated apps
2. Use environment variables for configuration
3. Review generated code before deployment
4. Rotate tokens if accidentally exposed

## Monitoring

### Logs
All operations are logged with timestamps:
```
2025-10-11 09:30:00 - INFO - Received request for task: task-001
2025-10-11 09:30:05 - INFO - Generated app at: generated_apps/task-001
2025-10-11 09:30:30 - INFO - Created repo: https://github.com/user/task-001
2025-10-11 09:30:45 - INFO - GitHub Pages enabled
2025-10-11 09:31:00 - INFO - Evaluation notification successful
```

### Status Tracking
Check task status anytime:
```bash
curl http://localhost:7860/status/task-001
```

## Advanced Usage

### Custom LLM Model
Edit `src/llm_generator.py`:
```python
model="gpt-4-turbo-preview"  # Change to gpt-4, gpt-3.5-turbo, etc.
```

### Custom Timeout
Edit `src/config.py`:
```python
EVALUATION_TIMEOUT = 600  # 10 minutes (default)
```

### Custom Retry Logic
Edit `src/config.py`:
```python
RETRY_DELAYS = [1, 2, 4, 8, 16]  # Exponential backoff delays
```

### Adding Attachments
Attachments should be in data URI format:
```json
{
  "attachments": [
    {
      "name": "logo.png",
      "url": "data:image/png;base64,iVBORw0KGgoAAAANS..."
    }
  ]
}
```

## Production Deployment

### Hugging Face Spaces

1. **Create a new Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose "Docker" SDK

2. **Configure Secrets**
   - Go to Space Settings → Repository Secrets
   - Add:
     - `STUDENT_SECRET`
     - `OPENAI_API_KEY`
     - `GITHUB_TOKEN`
     - `GITHUB_USERNAME`

3. **Push Code**
   ```bash
   git remote add hf https://huggingface.co/spaces/username/space-name
   git push hf main
   ```

4. **Access API**
   - Your API will be at: `https://username-space-name.hf.space`

### Other Platforms

**Railway / Render / Fly.io:**
- Set environment variables in platform settings
- Deploy using Dockerfile
- Ensure port 7860 is exposed

**AWS / GCP / Azure:**
- Use container services (ECS, Cloud Run, Container Apps)
- Set up environment variables
- Configure load balancer if needed

## Performance Tips

1. **Use faster LLM models** for quicker generation (e.g., gpt-3.5-turbo)
2. **Increase timeout** for complex tasks
3. **Cache common templates** to reduce LLM calls
4. **Use database** for persistent state in production
5. **Add task queue** (Celery/RQ) for better scalability

## Support

- **Documentation:** See README.md, SETUP.md, ARCHITECTURE.md
- **Issues:** Check logs in console output
- **Testing:** Use test_client.py for debugging
- **Validation:** Run validate_setup.py before starting

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-11
