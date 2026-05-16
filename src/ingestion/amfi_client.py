import httpx
import logging
import time

logger = logging.getLogger(__name__)

class AMFIClient:
    BASE_URL = "https://api.mfapi.in/mf"

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def get_fund_data(self, scheme_code: str) -> dict:
        """Fetch fund details and historical NAV from AMFI."""
        url = f"{self.BASE_URL}/{scheme_code}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching AMFI data for {scheme_code} (Attempt {attempt+1}/{self.max_retries})")
                response = httpx.get(url, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if response actually has data
                    if data.get("meta"):
                        return data
                    else:
                        logger.warning(f"No valid data returned for scheme {scheme_code}")
                        return None
                else:
                    logger.warning(f"AMFI API returned status {response.status_code} for {scheme_code}")
                    
            except httpx.RequestError as e:
                logger.warning(f"Network error fetching AMFI data: {e}")
            except ValueError as e:
                logger.warning(f"JSON decode error: {e}")
                
            if attempt < self.max_retries - 1:
                time.sleep(5)
                
        logger.error(f"Failed to fetch AMFI data for {scheme_code} after {self.max_retries} attempts.")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = AMFIClient()
    # HDFC Mid Cap scheme code
    data = client.get_fund_data("119598")
    if data:
        print(f"Successfully fetched AMFI data for {data['meta']['scheme_name']}")
