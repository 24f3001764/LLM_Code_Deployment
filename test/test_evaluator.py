"""
Unit tests for evaluation notifier
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from src.evaluator import EvaluationNotifier
from src.models import EvaluationPayload


class TestEvaluationNotifier:
    """Test EvaluationNotifier class"""
    
    @pytest.fixture
    def notifier(self):
        """Create an EvaluationNotifier instance"""
        return EvaluationNotifier()
    
    @pytest.fixture
    def sample_payload(self):
        """Create a sample evaluation payload"""
        return EvaluationPayload(
            email="test@example.com",
            task="test-task-001",
            round=1,
            nonce="test-nonce",
            repo_url="https://github.com/user/repo",
            commit_sha="abc123def456",
            pages_url="https://user.github.io/repo"
        )
    
    @pytest.mark.asyncio
    async def test_notify_success_first_attempt(self, notifier, sample_payload):
        """Test successful notification on first attempt"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await notifier.notify("https://example.com/evaluate", sample_payload)
            
            assert result is True
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_notify_success_after_retry(self, notifier, sample_payload):
        """Test successful notification after one retry"""
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Server Error"
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.text = "Success"
        
        with patch('httpx.AsyncClient') as mock_client:
            # First call fails, second succeeds
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=[mock_response_fail, mock_response_success]
            )
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await notifier.notify("https://example.com/evaluate", sample_payload)
            
            assert result is True
            assert mock_client.return_value.__aenter__.return_value.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_notify_all_attempts_fail(self, notifier, sample_payload):
        """Test notification fails after all retry attempts"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await notifier.notify("https://example.com/evaluate", sample_payload)
            
            assert result is False
            # Should try 5 times (based on RETRY_DELAYS in config)
            assert mock_client.return_value.__aenter__.return_value.post.call_count == 5
    
    @pytest.mark.asyncio
    async def test_notify_network_exception(self, notifier, sample_payload):
        """Test notification with network exception"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await notifier.notify("https://example.com/evaluate", sample_payload)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_notify_timeout_exception(self, notifier, sample_payload):
        """Test notification with timeout exception"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await notifier.notify("https://example.com/evaluate", sample_payload)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_notify_correct_headers(self, notifier, sample_payload):
        """Test that notification sends correct headers"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await notifier.notify("https://example.com/evaluate", sample_payload)
            
            # Check that headers include Content-Type
            call_kwargs = mock_post.call_args[1]
            assert 'headers' in call_kwargs
            assert call_kwargs['headers']['Content-Type'] == 'application/json'
    
    @pytest.mark.asyncio
    async def test_notify_correct_payload(self, notifier, sample_payload):
        """Test that notification sends correct payload"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await notifier.notify("https://example.com/evaluate", sample_payload)
            
            # Check that payload is sent as JSON
            call_kwargs = mock_post.call_args[1]
            assert 'json' in call_kwargs
            payload_dict = call_kwargs['json']
            assert payload_dict['email'] == "test@example.com"
            assert payload_dict['task'] == "test-task-001"
            assert payload_dict['commit_sha'] == "abc123def456"
    
    @pytest.mark.asyncio
    async def test_notify_non_200_status(self, notifier, sample_payload):
        """Test notification with non-200 status codes"""
        for status_code in [400, 401, 403, 404, 500, 502, 503]:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = f"Error {status_code}"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
                
                with patch('asyncio.sleep', new_callable=AsyncMock):
                    result = await notifier.notify("https://example.com/evaluate", sample_payload)
                
                assert result is False
    
    @pytest.mark.asyncio
    async def test_notify_retry_delays(self, notifier, sample_payload):
        """Test that retry delays are applied correctly"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                await notifier.notify("https://example.com/evaluate", sample_payload)
                
                # Should sleep 4 times (between 5 attempts)
                assert mock_sleep.call_count == 4
                # Check that delays are from RETRY_DELAYS
                from src.config import config
                expected_delays = config.RETRY_DELAYS[:4]
                actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
                assert actual_delays == expected_delays
