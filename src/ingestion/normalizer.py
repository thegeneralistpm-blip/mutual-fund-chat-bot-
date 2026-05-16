import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Normalizer:
    def __init__(self):
        pass
        
    def normalize_fund_data(self, groww_data: dict, amfi_data: dict, scheme_code: str) -> dict:
        """Merges and normalizes data from Groww and AMFI."""
        normalized = {
            "scheme_code": scheme_code,
            "groww_url": groww_data.get("groww_url"),
            "fund_name": groww_data.get("fund_name"),
            "amc": groww_data.get("amc", "HDFC Mutual Fund"),
            "nav_available": False,
            "returns": groww_data.get("returns", {"1y": None, "3y": None, "5y": None})
        }
        
        # AMFI Data is authoritative for NAV
        if amfi_data and "data" in amfi_data and len(amfi_data["data"]) > 0:
            latest_nav_data = amfi_data["data"][0]
            normalized["nav"] = self._parse_float(latest_nav_data.get("nav"))
            normalized["nav_date"] = latest_nav_data.get("date")
            normalized["nav_available"] = normalized["nav"] is not None
            
            # Use AMFI name if Groww name is missing
            if not normalized["fund_name"] and "meta" in amfi_data:
                normalized["fund_name"] = amfi_data["meta"].get("scheme_name")
        else:
            # Fallback to Groww NAV if AMFI is down
            groww_nav = groww_data.get("nav")
            if groww_nav:
                normalized["nav"] = self._parse_float(groww_nav)
                normalized["nav_date"] = datetime.now().strftime("%Y-%m-%d") # approx
                normalized["nav_available"] = normalized["nav"] is not None
                
        # Copy other fields from Groww
        for field in ['aum_crore', 'expense_ratio', 'category', 'risk_level', 'min_sip_amount', 'fund_manager', 'benchmark', 'exit_load', 'full_text', 'completeness_score']:
            if field in groww_data:
                if field == 'expense_ratio':
                    normalized[field] = self._parse_float(groww_data[field])
                else:
                    normalized[field] = groww_data[field]
                    
        # Construct a rich text document for embedding
        normalized["document_text"] = self._create_document_text(normalized)
        
        return normalized

    def _parse_float(self, val):
        if not val:
            return None
        try:
            # Strip anything that's not a digit or decimal point
            cleaned = ''.join(c for c in str(val) if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else None
        except ValueError:
            return None
            
    def _create_document_text(self, data: dict) -> str:
        """Creates a readable text representation for the LLM to understand."""
        lines = [
            f"Fund Name: {data.get('fund_name', 'Unknown')}",
            f"Scheme Code: {data.get('scheme_code')}",
            f"AMC: {data.get('amc')}",
            f"Category: {data.get('category', 'Unknown')}",
            f"Groww URL: {data.get('groww_url', 'N/A')}",
        ]
        
        if data.get('nav_available'):
            lines.append(f"Current NAV: ₹{data.get('nav')} (as of {data.get('nav_date')})")
            
        if data.get('aum_crore'):
            lines.append(f"Fund Size (AUM): {data.get('aum_crore')}")
            
        if data.get('expense_ratio'):
            lines.append(f"Expense Ratio: {data.get('expense_ratio')}%")
            
        returns = data.get('returns', {})
        if any(returns.values()):
            ret_str = ", ".join([f"{k.upper()}: {v}%" for k, v in returns.items() if v])
            lines.append(f"Historical Returns: {ret_str}")
            
        # Add the full scraped text from Groww for deep context
        if data.get('full_text'):
            lines.append(f"\nDetailed Information:\n{data['full_text']}")
            
        return "\n".join(lines)
