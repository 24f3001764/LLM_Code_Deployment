"""
Unit tests for FastAPI main application
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app, task_state
from src.models import TaskRequest


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def valid_secret():
    """Get valid secret from config"""
    from src.config import config
    return config.STUDENT_SECRET


@pytest.fixture
def sample_request_data(valid_secret):
    """Create sample request data"""
    return {
        "email": "test@example.com",
        "secret": valid_secret,
        "task": "test-task-001",
        "round": 1,
        "nonce": "test-nonce",
        "brief": "Create a simple web page",
        "checks": ["Has README", "Has LICENSE"],
        "evaluation_url": "https://example.com/evaluate",
        "attachments": []
    }


class TestRootEndpoint:
    """Test root health check endpoint"""
    
    def test_root_endpoint(self, client):
        """Test GET / returns health check"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["service"] == "LLM Code Deployment API"
        assert "version" in data


class TestRequestEndpoint:
    """Test POST /request endpoint"""
    
    def test_request_valid_round1(self, client, sample_request_data):
        """Test valid round 1 request"""
        with patch('src.main.process_build_task', new_callable=AsyncMock):
            response = client.post("/request", json=sample_request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"
            assert data["task"] == "test-task-001"
            assert data["round"] == 1
            assert "message" in data
    
    def test_request_valid_round2(self, client, sample_request_data):
        """Test valid round 2 request"""
        sample_request_data["round"] = 2
        
        with patch('src.main.process_revision_task', new_callable=AsyncMock):
            response = client.post("/request", json=sample_request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"
            assert data["round"] == 2
    
    def test_request_invalid_secret(self, client, sample_request_data):
        """Test request with invalid secret"""
        sample_request_data["secret"] = "wrong-secret"
        
        response = client.post("/request", json=sample_request_data)
        
        assert response.status_code == 401
        assert "Invalid secret" in response.json()["detail"]
    
    def test_request_missing_fields(self, client, valid_secret):
        """Test request with missing required fields"""
        incomplete_data = {
            "email": "test@example.com",
            "secret": valid_secret,
            "task": "test-task-001"
            # Missing: round, nonce, brief, checks, evaluation_url
        }
        
        response = client.post("/request", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_request_invalid_round(self, client, sample_request_data):
        """Test request with invalid round number"""
        sample_request_data["round"] = 3  # Invalid: must be 1 or 2
        
        response = client.post("/request", json=sample_request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_request_duplicate_processing(self, client, sample_request_data):
        """Test duplicate request while already processing"""
        # Clear task state
        task_state.clear()
        
        # Mark task as processing
        task_key = f"{sample_request_data['task']}-{sample_request_data['round']}"
        task_state[task_key] = {"status": "processing"}
        
        with patch('src.main.process_build_task', new_callable=AsyncMock):
            response = client.post("/request", json=sample_request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "already being processed" in data["message"]
        
        # Cleanup
        task_state.clear()
    
    def test_request_with_attachments(self, client, sample_request_data):
        """Test request with attachments"""
        sample_request_data["attachments"] = [
            {
                "name": "test.png",
                "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            }
        ]
        
        with patch('src.main.process_build_task', new_callable=AsyncMock):
            response = client.post("/request", json=sample_request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"


class TestStatusEndpoint:
    """Test GET /status/{task_id} endpoint"""
    
    def test_status_existing_task(self, client):
        """Test getting status of existing task"""
        # Setup task state
        task_state.clear()
        task_state["test-task-001-1"] = {
            "status": "completed",
            "repo_url": "https://github.com/user/repo",
            "pages_url": "https://user.github.io/repo"
        }
        
        response = client.get("/status/test-task-001")
        
        assert response.status_code == 200
        data = response.json()
        assert "test-task-001-1" in data
        assert data["test-task-001-1"]["status"] == "completed"
        
        # Cleanup
        task_state.clear()
    
    def test_status_nonexistent_task(self, client):
        """Test getting status of non-existent task"""
        task_state.clear()
        
        response = client.get("/status/nonexistent-task")
        
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]
    
    def test_status_multiple_rounds(self, client):
        """Test getting status with multiple rounds"""
        task_state.clear()
        task_state["test-task-002-1"] = {"status": "completed"}
        task_state["test-task-002-2"] = {"status": "processing"}
        
        response = client.get("/status/test-task-002")
        
        assert response.status_code == 200
        data = response.json()
        assert "test-task-002-1" in data
        assert "test-task-002-2" in data
        assert data["test-task-002-1"]["status"] == "completed"
        assert data["test-task-002-2"]["status"] == "processing"
        
        # Cleanup
        task_state.clear()


class TestProcessBuildTask:
    """Test process_build_task function"""
    
    @pytest.mark.asyncio
    async def test_process_build_task_success(self, sample_request_data, valid_secret):
        """Test successful build task processing"""
        from src.main import process_build_task
        
        request = TaskRequest(**sample_request_data)
        
        with patch('src.main.decode_and_save_attachments', new_callable=AsyncMock) as mock_decode:
            mock_decode.return_value = []
            
            with patch('src.main.LLMAppGenerator') as mock_generator:
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_app = AsyncMock(return_value="/path/to/app")
                mock_generator.return_value = mock_gen_instance
                
                with patch('src.main.GitHubManager') as mock_github:
                    mock_gh_instance = MagicMock()
                    mock_gh_instance.create_and_deploy = AsyncMock(
                        return_value=("https://github.com/user/repo", "abc123", "https://user.github.io/repo")
                    )
                    mock_github.return_value = mock_gh_instance
                    
                    with patch('src.main.EvaluationNotifier') as mock_notifier:
                        mock_notifier_instance = MagicMock()
                        mock_notifier_instance.notify = AsyncMock(return_value=True)
                        mock_notifier.return_value = mock_notifier_instance
                        
                        await process_build_task(request)
                        
                        # Verify task state was updated
                        task_key = f"{request.task}-{request.round}"
                        assert task_key in task_state
                        assert task_state[task_key]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_process_build_task_failure(self, sample_request_data, valid_secret):
        """Test build task processing with failure"""
        from src.main import process_build_task
        
        request = TaskRequest(**sample_request_data)
        
        with patch('src.main.decode_and_save_attachments', new_callable=AsyncMock) as mock_decode:
            mock_decode.side_effect = Exception("Test error")
            
            await process_build_task(request)
            
            # Verify task state shows failure
            task_key = f"{request.task}-{request.round}"
            assert task_key in task_state
            assert task_state[task_key]["status"] == "failed"
            assert "error" in task_state[task_key]


class TestProcessRevisionTask:
    """Test process_revision_task function"""
    
    @pytest.mark.asyncio
    async def test_process_revision_task_success(self, sample_request_data, valid_secret):
        """Test successful revision task processing"""
        from src.main import process_revision_task
        
        # Setup: Round 1 must be completed first
        task_state.clear()
        task_state["test-task-001-1"] = {"status": "completed"}
        
        sample_request_data["round"] = 2
        request = TaskRequest(**sample_request_data)
        
        with patch('src.main.decode_and_save_attachments', new_callable=AsyncMock) as mock_decode:
            mock_decode.return_value = []
            
            with patch('src.main.LLMAppGenerator') as mock_generator:
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_app = AsyncMock(return_value="/path/to/app")
                mock_generator.return_value = mock_gen_instance
                
                with patch('src.main.GitHubManager') as mock_github:
                    mock_gh_instance = MagicMock()
                    mock_gh_instance.update_repo = AsyncMock(
                        return_value=("abc123", "https://user.github.io/repo")
                    )
                    mock_github.return_value = mock_gh_instance
                    
                    with patch('src.main.EvaluationNotifier') as mock_notifier:
                        mock_notifier_instance = MagicMock()
                        mock_notifier_instance.notify = AsyncMock(return_value=True)
                        mock_notifier.return_value = mock_notifier_instance
                        
                        await process_revision_task(request)
                        
                        # Verify task state was updated
                        task_key = f"{request.task}-{request.round}"
                        assert task_key in task_state
                        assert task_state[task_key]["status"] == "completed"
        
        # Cleanup
        task_state.clear()
    
    @pytest.mark.asyncio
    async def test_process_revision_task_no_round1(self, sample_request_data, valid_secret):
        """Test revision task without completed round 1"""
        from src.main import process_revision_task
        
        task_state.clear()
        
        sample_request_data["round"] = 2
        request = TaskRequest(**sample_request_data)
        
        await process_revision_task(request)
        
        # Verify task state shows failure
        task_key = f"{request.task}-{request.round}"
        assert task_key in task_state
        assert task_state[task_key]["status"] == "failed"
        
        # Cleanup
        task_state.clear()
