import asyncio
import logging
import httpx
from src.models import EvaluationPayload
from src.config import config

logger = logging.getLogger(__name__)


class EvaluationNotifier:
    """Handle notification to evaluation URL with retry logic"""
    
    async def notify(
        self,
        evaluation_url: str,
        payload: EvaluationPayload
    ) -> bool:
        """
        Send evaluation payload with exponential backoff retry
        Returns True if successful, False otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt, delay in enumerate(config.RETRY_DELAYS, 1):
                try:
                    logger.info(f"Sending evaluation notification (attempt {attempt}/{len(config.RETRY_DELAYS)})")
                    
                    response = await client.post(
                        evaluation_url,
                        json=payload.model_dump(),
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Evaluation notification successful: {response.text}")
                        return True
                    else:
                        logger.warning(f"Evaluation returned {response.status_code}: {response.text}")
                
                except Exception as e:
                    logger.error(f"Evaluation notification failed: {e}")
                
                # If not the last attempt, wait before retrying
                if attempt < len(config.RETRY_DELAYS):
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
            
            logger.error("All evaluation notification attempts failed")
            return False
