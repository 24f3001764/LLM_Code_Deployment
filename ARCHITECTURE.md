# System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Instructor System                        │
│                  (Sends Task Request via POST)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ POST /request
                             │ {email, secret, task, brief, ...}
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Student API Server (FastAPI)                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  main.py - Request Handler                               │  │
│  │  • Validates secret                                       │  │
│  │  • Returns HTTP 200 immediately                           │  │
│  │  • Spawns background task                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             │ Background Processing               │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  utils.py - Attachment Handler                           │  │
│  │  • Decodes base64 data URIs                              │  │
│  │  • Saves attachments to disk                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  llm_generator.py - App Generator                        │  │
│  │  • Builds prompt from brief + checks                     │  │
│  │  • Calls OpenAI GPT-4 API                                │  │
│  │  • Generates HTML/CSS/JS app                             │  │
│  │  • Generates README.md                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  github_manager.py - GitHub Integration                  │  │
│  │  • Creates public repository                             │  │
│  │  • Adds MIT LICENSE                                      │  │
│  │  • Pushes generated code                                 │  │
│  │  • Enables GitHub Pages                                  │  │
│  │  • Returns repo URL, commit SHA, pages URL               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                     │
│                             ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  evaluator.py - Notification Handler                     │  │
│  │  • POSTs to evaluation_url                               │  │
│  │  • Includes repo details + request metadata              │  │
│  │  • Retries with exponential backoff (1,2,4,8,16s)        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                     │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
                              │ POST to evaluation_url
                              │ {email, task, repo_url, ...}
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Instructor Evaluation API                   │
│                    (Receives Notification)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Server (`main.py`)
**Responsibilities:**
- Accept incoming HTTP POST requests
- Validate student secret
- Return immediate HTTP 200 response
- Spawn background tasks for processing
- Track task state
- Provide status endpoint

**Key Endpoints:**
- `GET /` - Health check
- `POST /request` - Main task endpoint
- `GET /status/{task_id}` - Task status

### 2. Data Models (`models.py`)
**Structures:**
- `TaskRequest` - Incoming request schema
- `EvaluationPayload` - Outgoing notification schema
- `APIResponse` - Immediate response schema
- `Attachment` - Attachment data structure

### 3. Configuration (`config.py`)
**Manages:**
- Environment variables
- API keys (OpenAI, GitHub)
- Student secret
- Timeouts and retry delays
- Directory paths

### 4. Utilities (`utils.py`)
**Functions:**
- `decode_and_save_attachments()` - Handle data URIs
- `sanitize_repo_name()` - Clean task IDs for GitHub
- `get_mit_license()` - Return MIT license text

### 5. LLM Generator (`llm_generator.py`)
**Process:**
1. Build prompt from brief, checks, attachments
2. Call OpenAI GPT-4 API
3. Parse and clean response
4. Generate HTML/CSS/JS application
5. Generate professional README.md
6. Save files to disk

**Fallback:**
- If API fails, uses template HTML
- Ensures app is always generated

### 6. GitHub Manager (`github_manager.py`)
**Round 1 (Create):**
1. Check if repo exists (delete if testing)
2. Create new public repository
3. Add LICENSE file
4. Add README.md
5. Add index.html
6. Enable GitHub Pages
7. Wait for deployment
8. Return URLs and commit SHA

**Round 2 (Update):**
1. Get existing repository
2. Update README.md
3. Update index.html
4. Commit changes
5. Wait for redeployment
6. Return new commit SHA

### 7. Evaluator (`evaluator.py`)
**Notification Process:**
1. Prepare JSON payload
2. POST to evaluation_url
3. Check for HTTP 200 response
4. If failed, retry with delays: 1s, 2s, 4s, 8s, 16s
5. Log all attempts
6. Return success/failure status

## Data Flow

### Round 1: Build and Deploy

```
Request → Validate → Save Attachments → Generate App → Create Repo
                                                            ↓
Notify ← Wait ← Enable Pages ← Push Code ← Add Files ← Create Repo
```

**Timeline:**
- 0s: Request received, 200 returned
- 0-30s: LLM generates app
- 30-40s: GitHub repo created
- 40-50s: Pages enabled, waiting for deployment
- 50-60s: Notification sent
- Total: ~1 minute

### Round 2: Revise

```
Request → Validate → Save Attachments → Generate Updated App
                                              ↓
Notify ← Wait ← Redeploy Pages ← Update Files ← Get Repo
```

**Timeline:**
- 0s: Request received, 200 returned
- 0-30s: LLM generates updated app
- 30-40s: Files updated in repo
- 40-50s: Pages redeployed
- 50-60s: Notification sent
- Total: ~1 minute

## External Dependencies

### OpenAI API
- **Model:** GPT-4 Turbo Preview
- **Usage:** Generate HTML/CSS/JS and README
- **Rate Limits:** Depends on account tier
- **Cost:** ~$0.01-0.03 per request

### GitHub API
- **Library:** PyGithub
- **Operations:** Create repo, add files, enable Pages
- **Rate Limits:** 5000/hour (authenticated)
- **Requirements:** Personal Access Token with `repo` scope

### Evaluation API
- **Protocol:** HTTP POST with JSON
- **Expected Response:** HTTP 200
- **Retry Logic:** Exponential backoff
- **Timeout:** 30 seconds per attempt

## State Management

### In-Memory State (Development)
```python
task_state = {
    "task-id-1": {
        "status": "completed",
        "started_at": "2025-10-10T12:00:00",
        "completed_at": "2025-10-10T12:01:00",
        "repo_url": "https://github.com/user/task-id",
        "pages_url": "https://user.github.io/task-id/",
        "notification_sent": True
    }
}
```

### Production Considerations
- Use database (PostgreSQL, MongoDB)
- Add task queue (Celery, RQ)
- Implement webhooks for async updates
- Add monitoring and alerting

## Security Measures

### Secret Management
- Student secret stored in environment variable
- Validated on every request
- Never logged or exposed

### API Keys
- Stored in `.env` file (gitignored)
- Loaded via python-dotenv
- Never committed to git

### GitHub Token
- Minimal required scopes (`repo`, `workflow`)
- Stored securely
- Can be rotated if compromised

### Input Validation
- Pydantic models validate all inputs
- Sanitize repo names
- Validate data URIs
- Check file sizes (future enhancement)

## Error Handling

### Request Level
- Invalid secret → HTTP 401
- Missing fields → HTTP 422 (Pydantic validation)
- Server error → HTTP 500

### Background Processing
- LLM API failure → Use fallback template
- GitHub API failure → Log error, mark task failed
- Notification failure → Retry with backoff

### Logging
- INFO: Normal operations
- WARNING: Retries, non-critical issues
- ERROR: Failures, exceptions
- All logs include task ID for tracing

## Scalability Considerations

### Current Limitations
- In-memory state (lost on restart)
- Synchronous background tasks
- No request queuing
- Single server instance

### Scaling Solutions
1. **Database:** PostgreSQL for persistent state
2. **Queue:** Redis + Celery for task processing
3. **Load Balancer:** Multiple API instances
4. **Caching:** Redis for frequently accessed data
5. **Monitoring:** Prometheus + Grafana
6. **Logging:** ELK stack or CloudWatch

## Deployment Architecture

### Development
```
Local Machine → FastAPI (localhost:8000)
```

### Production (Cloud)
```
Internet → Load Balancer → API Servers (multiple)
                              ↓
                         Task Queue (Redis/Celery)
                              ↓
                         Database (PostgreSQL)
```

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock external APIs
- Validate data models

### Integration Tests
- Test API endpoints
- Test GitHub integration
- Test LLM generation

### End-to-End Tests
- Full workflow from request to notification
- Test both Round 1 and Round 2
- Verify GitHub Pages deployment

### Manual Testing
- Use `test_client.py`
- Test with various briefs
- Test error scenarios
- Verify logs and state

## Monitoring

### Key Metrics
- Request count
- Success/failure rate
- Average processing time
- API error rates (OpenAI, GitHub)
- Notification success rate

### Health Checks
- API server status
- Database connectivity (if used)
- External API availability
- Disk space for generated apps

### Alerts
- High error rate
- API quota exceeded
- Deployment failures
- Long processing times (>10 min)

---

**This architecture supports the complete TDS Project 1 workflow while remaining simple enough for students to understand and extend.**
