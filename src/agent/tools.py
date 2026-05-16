import os
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from src.ingestion.amfi_client import AMFIClient
from src.retrieval.retriever import Retriever
from src.personalization.mock_store import get_user_context, format_user_context_for_prompt
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults

# Initialize clients once
amfi_client = AMFIClient()
try:
    retriever = Retriever(index_dir="data/vector_store")
except Exception:
    retriever = None


@tool
def get_live_nav(scheme_code: str) -> str:
    """Fetch latest NAV using AMFI scheme code."""
    scheme_code = str(scheme_code)
    data = amfi_client.get_fund_data(scheme_code)

    if not data or not data.get("data"):
        return f"Could not fetch NAV for scheme code {scheme_code}."
    
    latest_nav = data["data"][0]
    meta = data["meta"]
    return (
        f"Fund: {meta['scheme_name']}\n"
        f"Latest NAV: Rs. {latest_nav['nav']} (as of {latest_nav['date']})"
    )


@tool
def compare_funds(scheme_code_a: str, scheme_code_b: str) -> str:
    """Compare two mutual funds using AMFI codes."""
    scheme_code_a = str(scheme_code_a)
    scheme_code_b = str(scheme_code_b)
    data_a = amfi_client.get_fund_data(scheme_code_a)
    data_b = amfi_client.get_fund_data(scheme_code_b)


    res = []
    if data_a and data_a.get("data"):
        res.append(f"{data_a['meta']['scheme_name']}: NAV Rs. {data_a['data'][0]['nav']} ({data_a['data'][0]['date']})")
    else:
        res.append(f"Could not fetch data for scheme code {scheme_code_a}.")

    if data_b and data_b.get("data"):
        res.append(f"{data_b['meta']['scheme_name']}: NAV Rs. {data_b['data'][0]['nav']} ({data_b['data'][0]['date']})")
    else:
        res.append(f"Could not fetch data for scheme code {scheme_code_b}.")

    return "\n".join(res)


@tool
def calculate_sip_returns(amount: float, years: int, expected_return_rate_percent: float) -> str:
    """Calculate projected SIP corpus."""
    n = years * 12
    i = (expected_return_rate_percent / 100) / 12
    
    if i == 0:
        corpus = amount * n
    else:
        corpus = amount * (((1 + i)**n - 1) / i) * (1 + i)
        
    invested = amount * n
    wealth_gained = corpus - invested
    
    return (
        f"SIP Calculation Summary:\n"
        f"- Monthly Investment: Rs. {amount:,.2f}\n"
        f"- Duration: {years} years\n"
        f"- Expected Return: {expected_return_rate_percent}%\n"
        f"- Total Invested: Rs. {invested:,.2f}\n"
        f"- Wealth Gained: Rs. {wealth_gained:,.2f}\n"
        f"- Projected Corpus: Rs. {corpus:,.2f}"
    )


@tool
def estimate_tax_savings(investment_amount: float) -> str:
    """Estimate 80C tax savings for ELSS."""
    eligible_amount = min(investment_amount, 150000.0)
    # Assume 30% tax bracket + 4% cess = 31.2%
    max_savings = eligible_amount * 0.312
    
    return (
        f"ELSS Tax Savings Estimate (under Section 80C):\n"
        f"- Invested Amount: Rs. {investment_amount:,.2f}\n"
        f"- Eligible Amount for 80C: Rs. {eligible_amount:,.2f}\n"
        f"- Estimated Tax Saved (assuming 30% slab + 4% cess): Rs. {max_savings:,.2f}"
    )


@tool
def get_portfolio_summary(user_id: str) -> str:
    """Fetch user portfolio and risk profile by ID."""
    user_id = str(user_id)
    data = get_user_context(user_id)

    if not data:
        return f"No portfolio found for user_id: {user_id}. Available users: user_1, user_2."
    
    return format_user_context_for_prompt(data)


@tool
def search_knowledge_base(query: str) -> str:
    """Search vector DB for HDFC fund details (expense, exit load)."""
    query = str(query)
    if not retriever:

        return "Internal knowledge base is currently unavailable."
        
    return retriever.retrieve_formatted(query, top_k=3)


@tool
def recommend_funds(risk_profile: str, investment_goal: str, horizon_years: int) -> str:
    """Recommend Zerodha funds by risk/goal/horizon."""
    # Logic based on risk profile for Zerodha
    recommendations = {
        "High": [
            ("Zerodha Nifty Large Midcap 250 Index Fund", "https://groww.in/mutual-funds/zerodha-nifty-large-midcap-250-index-fund-direct-growth"),
            ("Zerodha ELSS Tax Saver Nifty Large Midcap 250 Index Fund", "https://groww.in/mutual-funds/zerodha-elss-tax-saver-nifty-large-midcap-250-index-fund-direct-growth")
        ],
        "Medium": [
            ("Zerodha Nifty Large Midcap 250 Index Fund", "https://groww.in/mutual-funds/zerodha-nifty-large-midcap-250-index-fund-direct-growth"),
            ("Zerodha Gold ETF FoF", "https://groww.in/mutual-funds/zerodha-gold-etf-fof-direct-growth")
        ],
        "Low": [
            ("Zerodha Gold ETF FoF", "https://groww.in/mutual-funds/zerodha-gold-etf-fof-direct-growth"),
            ("Zerodha Silver ETF FoF", "https://groww.in/mutual-funds/zerodha-silver-etf-fof-direct-growth"),
            ("Zerodha Overnight Fund", "https://groww.in/mutual-funds/zerodha-overnight-fund-direct-growth")
        ]
    }
    
    funds = recommendations.get(risk_profile, [("Zerodha Nifty Large Midcap 250 Index Fund", "https://groww.in/mutual-funds/zerodha-nifty-large-midcap-250-index-fund-direct-growth")])
    res = f"Based on your {risk_profile} risk profile and {investment_goal} goal for {horizon_years} years, we recommend:\n"
    for name, url in funds:
        res += f"- {name} (Link: {url})\n"
    res += "\nPlease use `search_knowledge_base` to get more details about these specific funds."
    return res


@tool
def initiate_sip(fund_name: str, amount: float, day_of_month: int) -> str:
    """Simulate SIP initiation. Requires confirmation."""
    return (
        f"SIP Initiation REQUESTED (SIMULATED):\n"
        f"- Fund: {fund_name}\n"
        f"- Amount: Rs. {amount}\n"
        f"- SIP Date: {day_of_month}th of every month\n"
        f"Status: Waiting for final user verification in the Groww App."
    )


@tool
def web_search(query: str) -> str:
    """Search web for news/trends if DB is insufficient."""
    query = str(query)
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)

    except Exception as e:
        return f"Web search failed: {e}"


@tool
def escalate_to_human(issue_summary: str, user_id: str) -> str:
    """Escalate to human support agent."""
    # In production, this would call Freshdesk/Zendesk API
    ticket_id = f"GRW-{os.urandom(4).hex().upper()}"
    return (
        f"Support Ticket Created: {ticket_id}\n"
        f"Status: A human agent from Groww will contact you shortly regarding: '{issue_summary}'.\n"
        f"Reference ID: {user_id}"
    )


