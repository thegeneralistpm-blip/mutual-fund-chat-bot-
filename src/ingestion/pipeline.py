import asyncio
import logging
import json
import os
from .groww_scraper import scrape_groww_urls
from .amfi_client import AMFIClient
from .parser import GrowwParser
from .normalizer import Normalizer
from .chunker import TextChunker
from .embedder import VectorEmbedder

logger = logging.getLogger(__name__)

# The 5 specific Zerodha URLs
TARGET_FUNDS = {
    "zerodha_large_midcap_250": {
        "url": "https://groww.in/mutual-funds/zerodha-nifty-large-midcap-250-index-fund-direct-growth",
        "scheme_code": None
    },
    "zerodha_silver_etf_fof": {
        "url": "https://groww.in/mutual-funds/zerodha-silver-etf-fof-direct-growth",
        "scheme_code": None
    },
    "zerodha_gold_etf_fof": {
        "url": "https://groww.in/mutual-funds/zerodha-gold-etf-fof-direct-growth",
        "scheme_code": None
    },
    "zerodha_elss_tax_saver": {
        "url": "https://groww.in/mutual-funds/zerodha-elss-tax-saver-nifty-large-midcap-250-index-fund-direct-growth",
        "scheme_code": None
    },
    "zerodha_overnight": {
        "url": "https://groww.in/mutual-funds/zerodha-overnight-fund-direct-growth",
        "scheme_code": None
    }
}

class IngestionPipeline:
    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = raw_dir
        self.amfi_client = AMFIClient()
        self.parser = GrowwParser()
        self.normalizer = Normalizer()
        self.chunker = TextChunker()
        
    async def run(self):
        logger.info("Starting Phase 0 Ingestion Pipeline...")
        os.makedirs(self.raw_dir, exist_ok=True)
        
        # 1. Scrape Groww
        urls_to_scrape = {k: v["url"] for k, v in TARGET_FUNDS.items()}
        logger.info(f"Scraping {len(urls_to_scrape)} URLs from Groww...")
        scraped_results = await scrape_groww_urls(urls_to_scrape)
        
        normalized_data_list = []
        
        # Process each fund
        for fund_key, data in TARGET_FUNDS.items():
            logger.info(f"Processing {fund_key}...")
            
            # 2. Get Scraped HTML
            scrape_data = scraped_results.get(fund_key, {})
            html = scrape_data.get("html")
            
            # 3. Parse HTML
            groww_data = self.parser.parse_fund_page(html, data["url"])
            
            # 4. Fetch AMFI Data
            amfi_data = None
            if data["scheme_code"]:
                amfi_data = self.amfi_client.get_fund_data(data["scheme_code"])
                
            # 5. Normalize and merge
            normalized = self.normalizer.normalize_fund_data(
                groww_data=groww_data, 
                amfi_data=amfi_data, 
                scheme_code=data["scheme_code"]
            )
            
            # Save raw JSON for debugging/fallback
            raw_path = os.path.join(self.raw_dir, f"{fund_key}.json")
            with open(raw_path, 'w', encoding='utf-8') as f:
                json.dump(normalized, f, indent=2)
                
            normalized_data_list.append(normalized)
            
        # 6. Chunking
        logger.info("Chunking text documents...")
        chunks = self.chunker.chunk_documents(normalized_data_list)
        
        # 7. Embedding
        if not os.environ.get("GOOGLE_API_KEY"):
            raise EnvironmentError(
                "GOOGLE_API_KEY environment variable not set. "
                "Add it as a GitHub Actions secret or in your .env file."
            )
            
        logger.info("Generating embeddings and saving to FAISS...")
        try:
            embedder = VectorEmbedder()
            embedder.embed_and_store(chunks)
        except Exception as e:
            logger.error(f"Failed to embed chunks: {e}")
            
        logger.info("✅ Phase 0 Ingestion Complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = IngestionPipeline()
    asyncio.run(pipeline.run())
