"""
Abstract base scraper with retry logic and error handling
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
import time
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import APICallLog, get_db_context
from app.config import settings
from app.exceptions import APIConnectionError

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers with production features"""

    def __init__(self, api_name: str, base_url: str):
        self.api_name = api_name
        self.base_url = base_url
        self.timeout = settings.API_TIMEOUT
        self.retry_attempts = settings.API_RETRY_ATTEMPTS

    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict]:
        """
        Scrape data from the source
        Must be implemented by subclasses
        Returns list of standardized dictionaries
        """
        pass

    def make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        method: str = "GET"
    ) -> requests.Response:
        """
        Make HTTP request with retry logic and logging
        Raises APIConnectionError on failure
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        last_error = None

        for attempt in range(self.retry_attempts):
            try:
                logger.debug(
                    f"Making {method} request to {self.api_name} "
                    f"(attempt {attempt + 1}/{self.retry_attempts})"
                )

                if method.upper() == "GET":
                    response = requests.get(
                        url,
                        params=params,
                        timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = requests.post(
                        url,
                        json=params,
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Calculate response time
                response_time_ms = int((time.time() - start_time) * 1000)

                # Log the API call
                self._log_api_call(
                    endpoint=endpoint,
                    status_code=response.status_code,
                    success=response.status_code < 400,
                    response_time_ms=response_time_ms
                )

                # Raise for HTTP errors
                response.raise_for_status()

                logger.debug(
                    f"Request successful: {response.status_code} "
                    f"({response_time_ms}ms)"
                )
                return response

            except requests.exceptions.Timeout as e:
                last_error = f"Timeout after {self.timeout}s"
                logger.warning(f"Request timeout (attempt {attempt + 1}): {e}")

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                logger.warning(f"Connection error (attempt {attempt + 1}): {e}")

            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    last_error = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                    logger.error(f"HTTP client error: {last_error}")
                    self._log_api_call(
                        endpoint=endpoint,
                        status_code=e.response.status_code,
                        success=False,
                        error_message=last_error,
                        response_time_ms=int((time.time() - start_time) * 1000)
                    )
                    raise APIConnectionError(self.api_name, last_error, attempt)

                # Retry on 5xx errors (server errors)
                last_error = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                logger.warning(f"Server error (attempt {attempt + 1}): {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")

            # Exponential backoff
            if attempt < self.retry_attempts - 1:
                sleep_time = 2 ** attempt  # 1s, 2s, 4s
                logger.debug(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)

        # All retries failed
        response_time_ms = int((time.time() - start_time) * 1000)
        self._log_api_call(
            endpoint=endpoint,
            status_code=None,
            success=False,
            error_message=last_error,
            response_time_ms=response_time_ms
        )

        raise APIConnectionError(
            self.api_name,
            last_error or "Unknown error",
            self.retry_attempts
        )

    def _log_api_call(
        self,
        endpoint: str,
        status_code: Optional[int],
        success: bool,
        error_message: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ):
        """Log API call to database for monitoring"""
        try:
            with get_db_context() as db:
                log_entry = APICallLog(
                    api_name=self.api_name,
                    endpoint=endpoint,
                    status_code=status_code,
                    success=success,
                    error_message=error_message,
                    response_time_ms=response_time_ms,
                    called_at=datetime.utcnow()
                )
                db.add(log_entry)
                db.commit()
        except Exception as e:
            # Don't let logging errors crash the application
            logger.error(f"Failed to log API call: {e}")

    def categorize_error(self, error: Exception) -> str:
        """Categorize error type for better handling"""
        if isinstance(error, requests.exceptions.Timeout):
            return "timeout"
        elif isinstance(error, requests.exceptions.ConnectionError):
            return "connection"
        elif isinstance(error, requests.exceptions.HTTPError):
            return "http_error"
        elif isinstance(error, APIConnectionError):
            return "api_connection"
        else:
            return "unknown"
