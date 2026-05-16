from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

class GrowwParser:
    def __init__(self):
        pass
        
    def parse_fund_page(self, html: str, url: str) -> dict:
        """Parses the HTML of a Groww fund page and extracts metadata."""
        if not html:
            return {}
            
        soup = BeautifulSoup(html, 'lxml')
        data = {"groww_url": url}
        
        try:
            # Title / Fund Name
            h1 = soup.find('h1')
            data['fund_name'] = h1.get_text(strip=True) if h1 else None
            
            # Extract text blocks that might contain NAV, Returns, AUM, Expense Ratio
            # Since Groww's React classes are dynamic (e.g. contentPrimary, text14), 
            # we look for keyword patterns in the text
            full_text = soup.get_text(separator=' | ')
            
            # Very basic regex extractions as fallbacks
            nav_match = re.search(r'NAV(?:.*?|)₹\s*([\d\.]+)', full_text, re.IGNORECASE)
            if nav_match:
                data['nav'] = nav_match.group(1)
                
            aum_match = re.search(r'Fund Size(?:.*?|)₹\s*([\d\.]+\s*[KkCcMmrR]+)', full_text, re.IGNORECASE)
            if aum_match:
                data['aum_crore'] = aum_match.group(1)
                
            expense_match = re.search(r'Expense Ratio(?:.*?|)([\d\.]+)\s*%', full_text, re.IGNORECASE)
            if expense_match:
                data['expense_ratio'] = expense_match.group(1)
                
            # Attempt to find returns (1Y, 3Y, 5Y)
            # Typically looks like "1Y 18.5%" or similar in a table
            returns = {}
            for period in ['1Y', '3Y', '5Y']:
                # look for period followed closely by a percentage
                ret_match = re.search(rf'{period}(?:.*?|)([\d\.\-]+)\s*%', full_text, re.IGNORECASE)
                if ret_match:
                    returns[period.lower()] = ret_match.group(1)
            
            if returns:
                data['returns'] = returns
                
            # Category and AMC can be tricky without exact classes, 
            # but we can grab them from the breadcrumbs or meta tags
            breadcrumbs = soup.find_all('a', class_=re.compile(r'breadcrumb', re.I))
            if breadcrumbs and len(breadcrumbs) > 2:
                data['category'] = breadcrumbs[-2].get_text(strip=True)
                
        except Exception as e:
            logger.error(f"Error parsing HTML for {url}: {e}")
            
        # We also want to store a clean text version of the page for vector embedding
        # Removing scripts and styles
        for script_or_style in soup(['script', 'style', 'noscript', 'header', 'footer']):
            script_or_style.decompose()
            
        clean_text = ' '.join(soup.stripped_strings)
        data['full_text'] = clean_text
        
        # Give it a completeness score based on keys found
        expected_keys = ['fund_name', 'nav', 'aum_crore', 'expense_ratio', 'returns']
        found = sum(1 for k in expected_keys if k in data and data[k])
        data['completeness_score'] = found / len(expected_keys)
        
        return data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = GrowwParser()
    print("Parser initialized.")
