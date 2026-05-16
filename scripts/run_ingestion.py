import asyncio
import logging
import sys
import os

# Add the root directory to sys.path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.pipeline import IngestionPipeline
from dotenv import load_dotenv

def main():
    # Load environment variables (e.g., GOOGLE_API_KEY) from .env file if it exists
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("ingestion_runner")
    
    logger.info("Initializing Data Scraping and Ingestion Phase 0...")
    
    pipeline = IngestionPipeline()
    
    try:
        asyncio.run(pipeline.run())
    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user.")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
