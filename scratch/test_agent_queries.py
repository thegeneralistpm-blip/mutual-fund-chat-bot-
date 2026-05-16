import logging
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("."))

from src.agent.orchestrator import FundAgent

def test_agent():
    logging.basicConfig(level=logging.INFO)
    agent = FundAgent()
    
    queries = [
        "Hi",
        "How can you help me?",
        "What is the exit load of HDFC Small Cap?",
        "Compare HDFC Mid Cap and HDFC Multi Cap",
        "What is the best mutual fund for 5 years?",
        "Should I invest in HDFC Mid Cap?",
        "Who is the CEO of Groww?",
        "Tell me about the HDFC Gold ETF Fund of Fund."
    ]
    
    for q in queries:
        print(f"\n--- Query: {q} ---")
        try:
            response = agent.chat(q)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_agent()
