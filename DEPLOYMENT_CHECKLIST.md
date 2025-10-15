# 🚀 Hugging Face Deployment Checklist

## ✅ Pre-Deployment Fixes (COMPLETED)

- [x] **Dockerfile Entry Point** - Fixed to `main:app`
- [x] **Port Configuration** - Updated to 7860 in `config.py`
- [x] **.dockerignore** - Created to exclude unnecessary files
- [x] **README.md** - Updated with comprehensive documentation
- [x] **Timeout Protection** - Added timing checks in background tasks
- [x] **Project Structure** - Moved files from `student/` to root

## 📋 Deployment Steps

### Step 1: Test Docker Build Locally (Optional but Recommended)

```bash
# Build the Docker image
docker build -t llm-deployment .

# Run locally to test
docker run -p 7860:7860 \
  -e STUDENT_SECRET="your-secret" \
  -e OPENAI_API_KEY="your-key" \
  -e GITHUB_TOKEN="your-token" \
  -e GITHUB_USERNAME="your-username" \
  llm-deployment
```

### Step 2: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in details:
   - **Space name**: `llm-code-deployment` (or your choice)
   - **License**: MIT
   - **Select SDK**: Docker
   - **Visibility**: Public or Private (your choice)
4. Click **"Create Space"**

### Step 3: Push Code to Hugging Face

**Option A: Using Git (Recommended)**

```bash
# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Push to Hugging Face
git push hf main
```

**Option B: Using Hugging Face Web Interface**

1. Go to your Space's **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload all files from your project root
4. Commit changes

### Step 4: Configure Secrets

1. Go to your Space's **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Add the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `STUDENT_SECRET` | Your unique authentication secret | `my-secret-key-2025` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_...` |
| `GITHUB_USERNAME` | Your GitHub username | `yourusername` |

**Important**: Make sure your GitHub token has these scopes:
- `repo` (Full control of private repositories)
- `workflow` (Update GitHub Action workflows)

### Step 5: Monitor Build

1. Go to **"Logs"** tab in your Space
2. Watch the build process
3. Wait for "Running on http://0.0.0.0:7860" message
4. Status should show **"Running"** (green)

### Step 6: Test Deployment

**Test Health Endpoint:**
```bash
curl https://YOUR_USERNAME-SPACE_NAME.hf.space/
```

Expected response:
```json
{
  "status": "running",
  "service": "LLM Code Deployment API",
  "version": "1.0.0"
}
```

**Test Task Submission:**
```bash
curl -X POST https://YOUR_USERNAME-SPACE_NAME.hf.space/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your-secret",
    "task": "test-task-001",
    "round": 1,
    "nonce": "test-nonce-123",
    "brief": "Create a simple hello world web page",
    "checks": ["Must display Hello World"],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
  }'
```

Expected response:
```json
{
  "status": "accepted",
  "message": "Task test-task-001 round 1 accepted for processing",
  "task": "test-task-001",
  "round": 1
}
```

### Step 7: Verify Full Workflow

1. **Check Logs**: Monitor Space logs for processing
2. **Check GitHub**: Verify repository was created
3. **Check GitHub Pages**: Verify site is deployed
4. **Check Notification**: Verify callback was sent

## 🔍 Troubleshooting

### Build Fails

**Check:**
- All files are uploaded correctly
- `requirements.txt` is in root
- Dockerfile syntax is correct

**Solution:**
- Review build logs in Space
- Fix errors and push again

### API Not Responding

**Check:**
- Space status is "Running"
- Port 7860 is configured correctly
- No errors in logs

**Solution:**
- Restart Space from Settings
- Check environment variables

### Secret Authentication Fails

**Check:**
- `STUDENT_SECRET` is set in Space secrets
- Secret matches what you're sending in requests

**Solution:**
- Update secret in Space settings
- Test with correct secret

### GitHub Integration Fails

**Check:**
- `GITHUB_TOKEN` is valid and not expired
- Token has `repo` and `workflow` scopes
- `GITHUB_USERNAME` is correct

**Solution:**
- Generate new GitHub token
- Update in Space secrets
- Restart Space

### LLM Generation Fails

**Check:**
- `OPENAI_API_KEY` is valid
- OpenAI account has credits
- API quota not exceeded

**Solution:**
- Verify API key at https://platform.openai.com/api-keys
- Add credits to OpenAI account
- Check usage limits

## 📝 Submission Information

Once deployed and tested, submit these details:

- **API Endpoint URL**: `https://YOUR_USERNAME-SPACE_NAME.hf.space`
- **Student Secret**: Your `STUDENT_SECRET` value
- **GitHub Username**: Your GitHub username

## 🎯 Final Checklist

Before submitting:

- [ ] Space is running (green status)
- [ ] Health endpoint responds correctly
- [ ] Test task completes successfully
- [ ] GitHub repo is created
- [ ] GitHub Pages is deployed
- [ ] Notification callback works
- [ ] All secrets are configured
- [ ] Logs show no errors
- [ ] API endpoint URL is noted
- [ ] Student secret is noted

## 🚨 Important Notes

1. **Keep Space Running**: Don't stop or delete the Space during evaluation period
2. **Monitor Regularly**: Check logs daily for any issues
3. **GitHub Token**: Ensure it doesn't expire during evaluation
4. **OpenAI Credits**: Ensure sufficient credits for all tasks
5. **Backup**: Keep a local copy of your code

## 📞 Support Resources

- **Hugging Face Spaces**: https://huggingface.co/docs/hub/spaces
- **Docker SDK**: https://huggingface.co/docs/hub/spaces-sdks-docker
- **FastAPI**: https://fastapi.tiangolo.com/
- **GitHub API**: https://docs.github.com/en/rest

---

**Status**: Ready for Deployment ✅  
**Last Updated**: 2025-10-10
