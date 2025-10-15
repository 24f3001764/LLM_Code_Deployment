# Project Structure

Clean, organized structure for the LLM Code Deployment automation tool.

## 📁 Directory Layout

```
LLM_Code_Deployment/
│
├── 📂 src/                          # Source code
│   ├── __init__.py                  # Package initialization
│   ├── main.py                      # FastAPI server & endpoints
│   ├── models.py                    # Pydantic data models
│   ├── config.py                    # Configuration management
│   ├── llm_generator.py             # OpenAI LLM integration
│   ├── github_manager.py            # GitHub API automation
│   ├── evaluator.py                 # Notification with retry logic
│   ├── security_scanner.py          # Secret detection system
│   └── utils.py                     # Helper functions
│
├── 📂 test/                         # Testing utilities
│   ├── __init__.py                  # Test package init
│   └── test_client.py               # Interactive test client
│
├── 📄 Configuration Files
│   ├── .env.example                 # Environment variables template
│   ├── .gitignore                   # Git ignore rules
│   ├── .gitattributes               # Git attributes
│   ├── .dockerignore                # Docker ignore rules
│   ├── Dockerfile                   # Container configuration
│   └── requirements.txt             # Python dependencies
│
├── 📄 Startup Scripts
│   ├── start.py                     # Python startup script
│   ├── start.bat                    # Windows startup script
│   ├── run_tests.bat                # Windows test runner
│   └── validate_setup.py            # Setup validation script
│
├── 📄 Documentation
│   ├── README.md                    # Main project overview
│   ├── PROJECT_SUMMARY.md           # Complete implementation summary
│   ├── IMPLEMENTATION_COMPLETE.md   # Implementation checklist
│   ├── QUICKSTART.md                # 5-minute quick start
│   ├── SETUP.md                     # Detailed setup guide
│   ├── USAGE_GUIDE.md               # API usage & troubleshooting
│   ├── ARCHITECTURE.md              # System architecture
│   ├── DEPLOYMENT_CHECKLIST.md      # Deployment guide
│   └── PROJECT_STRUCTURE.md         # This file
│
└── 📄 Examples
    └── sample_request.json          # Example API request
```

## 📋 File Descriptions

### Source Code (`src/`)

| File | Purpose | Key Features |
|------|---------|--------------|
| `main.py` | FastAPI application | Endpoints, background tasks, state management |
| `models.py` | Data models | TaskRequest, EvaluationPayload, APIResponse |
| `config.py` | Configuration | Environment variables, validation |
| `llm_generator.py` | LLM integration | OpenAI GPT-4, prompt engineering, fallbacks |
| `github_manager.py` | GitHub automation | Repo creation, Pages deployment, updates |
| `evaluator.py` | Notifications | Exponential backoff, retry logic |
| `security_scanner.py` | Security | Secret detection, 15+ patterns |
| `utils.py` | Utilities | Attachments, sanitization, LICENSE |

### Tests (`test/`)

| File | Purpose |
|------|---------|
| `test_client.py` | Interactive testing for Round 1 & 2 workflows |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Template for environment variables |
| `.gitignore` | Excludes sensitive files from git |
| `.dockerignore` | Excludes files from Docker builds |
| `Dockerfile` | Container configuration for deployment |
| `requirements.txt` | Python package dependencies |

### Startup Scripts

| File | Purpose |
|------|---------|
| `start.py` | Validates setup and starts server |
| `start.bat` | Windows batch file for easy startup |
| `run_tests.bat` | Windows batch file for testing |
| `validate_setup.py` | Checks environment and dependencies |

### Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Project overview | Everyone |
| `PROJECT_SUMMARY.md` | Complete implementation details | Developers/Evaluators |
| `IMPLEMENTATION_COMPLETE.md` | Requirements checklist | Evaluators |
| `QUICKSTART.md` | Fast setup guide | New users |
| `SETUP.md` | Detailed setup instructions | Developers |
| `USAGE_GUIDE.md` | API usage & troubleshooting | Users/Developers |
| `ARCHITECTURE.md` | System design & components | Developers |
| `DEPLOYMENT_CHECKLIST.md` | Production deployment steps | DevOps |

### Examples

| File | Purpose |
|------|---------|
| `sample_request.json` | Example API request payload |

## 🎯 Quick Navigation

### For First-Time Setup:
1. Read `QUICKSTART.md`
2. Run `validate_setup.py`
3. Use `start.py` or `start.bat`

### For Development:
1. Review `ARCHITECTURE.md`
2. Explore `src/` directory
3. Test with `test_client.py`

### For Deployment:
1. Check `DEPLOYMENT_CHECKLIST.md`
2. Configure `Dockerfile`
3. Set environment variables

### For Troubleshooting:
1. Consult `USAGE_GUIDE.md`
2. Check logs in console
3. Run `validate_setup.py`

## 📊 File Statistics

- **Total Files:** 26 (excluding .git)
- **Source Files:** 9 Python files
- **Documentation:** 9 Markdown files
- **Configuration:** 5 files
- **Scripts:** 4 files
- **Examples:** 1 file

## 🧹 Recently Cleaned

The following redundant files were removed:
- ❌ `PROJECT_README.md` (redundant with README.md)
- ❌ `data_storage.py` (unused example code)
- ❌ `environ_variables.py` (functionality in config.py)
- ❌ `temp.py` (functionality in utils.py)

## 🔄 Generated at Runtime

These directories are created automatically:
- `generated_apps/` - Stores generated web applications
- `temp_attachments/` - Temporary storage for attachments
- `__pycache__/` - Python bytecode cache

## 📝 Notes

- All sensitive data goes in `.env` (not committed)
- Generated apps are temporary (can be cleaned)
- Logs are output to console (can be redirected)
- State is in-memory (use database for production)

---

**Last Updated:** 2025-10-11  
**Version:** 1.0.0
