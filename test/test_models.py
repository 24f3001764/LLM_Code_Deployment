"""
Unit tests for Pydantic models
"""
import pytest
from pydantic import ValidationError
from src.models import Attachment, TaskRequest, EvaluationPayload, APIResponse


class TestAttachment:
    """Test Attachment model"""
    
    def test_valid_attachment(self):
        """Test creating a valid attachment"""
        attachment = Attachment(
            name="test.png",
            url="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        assert attachment.name == "test.png"
        assert attachment.url.startswith("data:image/png;base64,")
    
    def test_attachment_missing_fields(self):
        """Test attachment with missing required fields"""
        with pytest.raises(ValidationError):
            Attachment(name="test.png")
        
        with pytest.raises(ValidationError):
            Attachment(url="data:image/png;base64,abc123")


class TestTaskRequest:
    """Test TaskRequest model"""
    
    def test_valid_task_request_round1(self):
        """Test creating a valid round 1 task request"""
        request = TaskRequest(
            email="test@example.com",
            secret="test-secret",
            task="test-task-001",
            round=1,
            nonce="test-nonce",
            brief="Create a simple web page",
            checks=["Has README", "Has LICENSE"],
            evaluation_url="https://example.com/evaluate",
            attachments=[]
        )
        assert request.email == "test@example.com"
        assert request.round == 1
        assert len(request.checks) == 2
    
    def test_valid_task_request_round2(self):
        """Test creating a valid round 2 task request"""
        request = TaskRequest(
            email="test@example.com",
            secret="test-secret",
            task="test-task-001",
            round=2,
            nonce="test-nonce",
            brief="Update the web page",
            checks=["Updated README"],
            evaluation_url="https://example.com/evaluate"
        )
        assert request.round == 2
    
    def test_invalid_round_number(self):
        """Test invalid round numbers"""
        with pytest.raises(ValidationError):
            TaskRequest(
                email="test@example.com",
                secret="test-secret",
                task="test-task-001",
                round=0,  # Invalid: must be >= 1
                nonce="test-nonce",
                brief="Test",
                checks=["Check 1"],
                evaluation_url="https://example.com/evaluate"
            )
        
        with pytest.raises(ValidationError):
            TaskRequest(
                email="test@example.com",
                secret="test-secret",
                task="test-task-001",
                round=3,  # Invalid: must be <= 2
                nonce="test-nonce",
                brief="Test",
                checks=["Check 1"],
                evaluation_url="https://example.com/evaluate"
            )
    
    def test_missing_required_fields(self):
        """Test task request with missing required fields"""
        with pytest.raises(ValidationError):
            TaskRequest(
                email="test@example.com",
                secret="test-secret",
                task="test-task-001",
                round=1
                # Missing: nonce, brief, checks, evaluation_url
            )
    
    def test_task_request_with_attachments(self):
        """Test task request with attachments"""
        attachments = [
            Attachment(name="file1.png", url="data:image/png;base64,abc123"),
            Attachment(name="file2.jpg", url="data:image/jpeg;base64,def456")
        ]
        request = TaskRequest(
            email="test@example.com",
            secret="test-secret",
            task="test-task-001",
            round=1,
            nonce="test-nonce",
            brief="Test with attachments",
            checks=["Check 1"],
            evaluation_url="https://example.com/evaluate",
            attachments=attachments
        )
        assert len(request.attachments) == 2
        assert request.attachments[0].name == "file1.png"


class TestEvaluationPayload:
    """Test EvaluationPayload model"""
    
    def test_valid_evaluation_payload(self):
        """Test creating a valid evaluation payload"""
        payload = EvaluationPayload(
            email="test@example.com",
            task="test-task-001",
            round=1,
            nonce="test-nonce",
            repo_url="https://github.com/user/repo",
            commit_sha="abc123def456",
            pages_url="https://user.github.io/repo"
        )
        assert payload.email == "test@example.com"
        assert payload.repo_url == "https://github.com/user/repo"
        assert payload.commit_sha == "abc123def456"
    
    def test_evaluation_payload_missing_fields(self):
        """Test evaluation payload with missing fields"""
        with pytest.raises(ValidationError):
            EvaluationPayload(
                email="test@example.com",
                task="test-task-001",
                round=1
                # Missing: nonce, repo_url, commit_sha, pages_url
            )
    
    def test_evaluation_payload_model_dump(self):
        """Test converting payload to dict"""
        payload = EvaluationPayload(
            email="test@example.com",
            task="test-task-001",
            round=1,
            nonce="test-nonce",
            repo_url="https://github.com/user/repo",
            commit_sha="abc123def456",
            pages_url="https://user.github.io/repo"
        )
        data = payload.model_dump()
        assert isinstance(data, dict)
        assert data["email"] == "test@example.com"
        assert data["commit_sha"] == "abc123def456"


class TestAPIResponse:
    """Test APIResponse model"""
    
    def test_valid_api_response(self):
        """Test creating a valid API response"""
        response = APIResponse(
            status="accepted",
            message="Task accepted for processing",
            task="test-task-001",
            round=1
        )
        assert response.status == "accepted"
        assert response.task == "test-task-001"
        assert response.round == 1
    
    def test_api_response_different_statuses(self):
        """Test API response with different status values"""
        statuses = ["accepted", "processing", "completed", "failed"]
        for status in statuses:
            response = APIResponse(
                status=status,
                message=f"Task is {status}",
                task="test-task-001",
                round=1
            )
            assert response.status == status
    
    def test_api_response_missing_fields(self):
        """Test API response with missing fields"""
        with pytest.raises(ValidationError):
            APIResponse(
                status="accepted",
                message="Task accepted"
                # Missing: task, round
            )
