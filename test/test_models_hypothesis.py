"""
Property-based tests for Pydantic models using Hypothesis
These tests generate random valid/invalid data to find edge cases
"""
import pytest
from hypothesis import given, strategies as st, assume, example
from pydantic import ValidationError
from src.models import Attachment, TaskRequest, EvaluationPayload, APIResponse


# Custom strategies for generating test data
@st.composite
def valid_email(draw):
    """Generate valid email addresses"""
    username = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
        min_size=1,
        max_size=20
    ))
    domain = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll',)),
        min_size=2,
        max_size=15
    ))
    tld = draw(st.sampled_from(['com', 'org', 'edu', 'net', 'io', 'ac.in']))
    return f"{username}@{domain}.{tld}"


@st.composite
def valid_url(draw):
    """Generate valid URLs"""
    protocol = draw(st.sampled_from(['http', 'https']))
    domain = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll',)),
        min_size=3,
        max_size=20
    ))
    tld = draw(st.sampled_from(['com', 'org', 'io', 'net']))
    path = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
        min_size=0,
        max_size=30
    ))
    if path:
        return f"{protocol}://{domain}.{tld}/{path}"
    return f"{protocol}://{domain}.{tld}"


@st.composite
def valid_github_url(draw):
    """Generate valid GitHub URLs"""
    username = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
        min_size=1,
        max_size=39
    ))
    repo = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='-_'),
        min_size=1,
        max_size=100
    ))
    return f"https://github.com/{username}/{repo}"


@st.composite
def valid_data_uri(draw):
    """Generate valid data URIs"""
    mime_type = draw(st.sampled_from(['image/png', 'image/jpeg', 'image/gif', 'text/plain']))
    encoding = 'base64'
    data = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='+/='),
        min_size=10,
        max_size=100
    ))
    return f"data:{mime_type};{encoding},{data}"


class TestAttachmentHypothesis:
    """Property-based tests for Attachment model"""
    
    @given(
        name=st.text(min_size=1, max_size=255),
        url=valid_data_uri()
    )
    def test_attachment_with_random_valid_data(self, name, url):
        """Test that any valid name and data URI creates a valid Attachment"""
        # Filter out names with path separators or null bytes
        assume('/' not in name and '\\' not in name and '\x00' not in name)
        
        attachment = Attachment(name=name, url=url)
        assert attachment.name == name
        assert attachment.url == url
        assert isinstance(attachment.name, str)
        assert isinstance(attachment.url, str)
    
    @given(name=st.text(min_size=1, max_size=255))
    def test_attachment_requires_url(self, name):
        """Test that Attachment requires a URL"""
        with pytest.raises(ValidationError):
            Attachment(name=name)
    
    @given(url=valid_data_uri())
    def test_attachment_requires_name(self, url):
        """Test that Attachment requires a name"""
        with pytest.raises(ValidationError):
            Attachment(url=url)


class TestTaskRequestHypothesis:
    """Property-based tests for TaskRequest model"""
    
    @given(
        email=valid_email(),
        secret=st.text(min_size=1, max_size=100),
        task=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='-_'),
            min_size=1,
            max_size=100
        ),
        round=st.integers(min_value=1, max_value=2),
        nonce=st.text(min_size=1, max_size=100),
        brief=st.text(min_size=10, max_size=1000),
        checks=st.lists(st.text(min_size=1, max_size=200), min_size=1, max_size=20),
        evaluation_url=valid_url()
    )
    def test_task_request_with_random_valid_data(
        self, email, secret, task, round, nonce, brief, checks, evaluation_url
    ):
        """Test that random valid data creates a valid TaskRequest"""
        request = TaskRequest(
            email=email,
            secret=secret,
            task=task,
            round=round,
            nonce=nonce,
            brief=brief,
            checks=checks,
            evaluation_url=evaluation_url,
            attachments=[]
        )
        
        assert request.email == email
        assert request.secret == secret
        assert request.task == task
        assert request.round in [1, 2]
        assert request.nonce == nonce
        assert request.brief == brief
        assert len(request.checks) >= 1
        assert request.evaluation_url == evaluation_url
    
    @given(
        email=valid_email(),
        secret=st.text(min_size=1, max_size=100),
        task=st.text(min_size=1, max_size=100),
        round=st.integers(min_value=3, max_value=100)  # Invalid rounds
    )
    def test_task_request_rejects_invalid_rounds(self, email, secret, task, round):
        """Test that rounds > 2 are rejected"""
        with pytest.raises(ValidationError):
            TaskRequest(
                email=email,
                secret=secret,
                task=task,
                round=round,
                nonce="test",
                brief="test",
                checks=["test"],
                evaluation_url="https://example.com"
            )
    
    @given(
        email=valid_email(),
        secret=st.text(min_size=1, max_size=100),
        task=st.text(min_size=1, max_size=100),
        round=st.integers(max_value=0)  # Invalid rounds (0 or negative)
    )
    def test_task_request_rejects_zero_or_negative_rounds(self, email, secret, task, round):
        """Test that rounds <= 0 are rejected"""
        with pytest.raises(ValidationError):
            TaskRequest(
                email=email,
                secret=secret,
                task=task,
                round=round,
                nonce="test",
                brief="test",
                checks=["test"],
                evaluation_url="https://example.com"
            )
    
    @given(
        email=valid_email(),
        attachments=st.lists(
            st.builds(
                Attachment,
                name=st.text(min_size=1, max_size=50),
                url=valid_data_uri()
            ),
            min_size=0,
            max_size=10
        )
    )
    def test_task_request_with_random_attachments(self, email, attachments):
        """Test TaskRequest with varying numbers of attachments"""
        request = TaskRequest(
            email=email,
            secret="test-secret",
            task="test-task",
            round=1,
            nonce="test-nonce",
            brief="Test brief",
            checks=["Check 1"],
            evaluation_url="https://example.com",
            attachments=attachments
        )
        
        assert len(request.attachments) == len(attachments)
        for i, att in enumerate(request.attachments):
            assert att.name == attachments[i].name
            assert att.url == attachments[i].url


class TestEvaluationPayloadHypothesis:
    """Property-based tests for EvaluationPayload model"""
    
    @given(
        email=valid_email(),
        task=st.text(min_size=1, max_size=100),
        round=st.integers(min_value=1, max_value=2),
        nonce=st.text(min_size=1, max_size=100),
        repo_url=valid_github_url(),
        commit_sha=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
            min_size=7,
            max_size=40
        ),
        pages_url=valid_url()
    )
    def test_evaluation_payload_with_random_valid_data(
        self, email, task, round, nonce, repo_url, commit_sha, pages_url
    ):
        """Test that random valid data creates a valid EvaluationPayload"""
        payload = EvaluationPayload(
            email=email,
            task=task,
            round=round,
            nonce=nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        assert payload.email == email
        assert payload.task == task
        assert payload.round == round
        assert payload.nonce == nonce
        assert payload.repo_url == repo_url
        assert payload.commit_sha == commit_sha
        assert payload.pages_url == pages_url
    
    @given(
        email=valid_email(),
        task=st.text(min_size=1, max_size=100),
        round=st.integers(min_value=1, max_value=2),
        nonce=st.text(min_size=1, max_size=100),
        repo_url=valid_github_url(),
        commit_sha=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
            min_size=7,
            max_size=40
        ),
        pages_url=valid_url()
    )
    def test_evaluation_payload_model_dump_preserves_data(
        self, email, task, round, nonce, repo_url, commit_sha, pages_url
    ):
        """Test that model_dump() preserves all data correctly"""
        payload = EvaluationPayload(
            email=email,
            task=task,
            round=round,
            nonce=nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        data = payload.model_dump()
        
        assert data["email"] == email
        assert data["task"] == task
        assert data["round"] == round
        assert data["nonce"] == nonce
        assert data["repo_url"] == repo_url
        assert data["commit_sha"] == commit_sha
        assert data["pages_url"] == pages_url


class TestAPIResponseHypothesis:
    """Property-based tests for APIResponse model"""
    
    @given(
        status=st.text(min_size=1, max_size=50),
        message=st.text(min_size=1, max_size=500),
        task=st.text(min_size=1, max_size=100),
        round=st.integers(min_value=1, max_value=2)
    )
    def test_api_response_with_random_valid_data(self, status, message, task, round):
        """Test that random valid data creates a valid APIResponse"""
        response = APIResponse(
            status=status,
            message=message,
            task=task,
            round=round
        )
        
        assert response.status == status
        assert response.message == message
        assert response.task == task
        assert response.round == round
    
    @given(
        status=st.sampled_from(['accepted', 'processing', 'completed', 'failed', 'error']),
        task=st.text(min_size=1, max_size=100),
        round=st.integers(min_value=1, max_value=2)
    )
    @example(status='accepted', task='test-task', round=1)
    @example(status='failed', task='error-task', round=2)
    def test_api_response_common_statuses(self, status, task, round):
        """Test APIResponse with common status values"""
        response = APIResponse(
            status=status,
            message=f"Task is {status}",
            task=task,
            round=round
        )
        
        assert response.status in ['accepted', 'processing', 'completed', 'failed', 'error']
        assert task in response.message or response.message == f"Task is {status}"


# Run with: pytest test/test_models_hypothesis.py -v
# Run with more examples: pytest test/test_models_hypothesis.py -v --hypothesis-show-statistics
# Run with specific seed: pytest test/test_models_hypothesis.py -v --hypothesis-seed=12345
