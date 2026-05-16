import os
import logging
import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.agent.tools import (
    get_live_nav,
    compare_funds,
    calculate_sip_returns,
    estimate_tax_savings,
    get_portfolio_summary,
    search_knowledge_base,
    recommend_funds,
    initiate_sip,
    web_search,
    escalate_to_human
)
from src.llm.prompt_templates import SEBI_DISCLAIMER
from src.safety.guardrails import Guardrails
from src.utils.pii import PIIRedactor

load_dotenv()
logger = logging.getLogger(__name__)

# List of tools available to the agent
TOOLS = [
    get_live_nav,
    compare_funds,
    calculate_sip_returns,
    estimate_tax_savings,
    get_portfolio_summary,
    search_knowledge_base,
    recommend_funds,
    initiate_sip,
    web_search,
    escalate_to_human
]

AGENT_SYSTEM_PROMPT = """You are a Zerodha Mutual Fund assistant. 
Your goal is to provide accurate, helpful, and transparent financial information specifically for Zerodha AMC's index-focused funds.

TONE & STYLE:
- Professional yet accessible (avoid overly complex jargon).
- Focus on the benefits of low-cost index investing and passive strategies.
- Use clear bullet points for comparisons.
- Always be objective; do not "push" products, but explain their suitability.
- Maintain a helpful, reassuring tone for transactional or frustrated queries.

CATEGORIES & BEHAVIOR:
1. Goal-Matching: Suggest funds based on risk profile (e.g., Zerodha Large Midcap 250 for diversified equity).
2. SIP Management: Explain app steps or pausing logic clearly.
3. Portfolio Intelligence: Use `get_portfolio_summary` to diagnose overexposure or rebalancing needs.
4. Tax & Compliance: Explain ELSS lock-ins (3 years) and Zerodha's specific ELSS Index fund.
5. Educational: Explain concepts like NAV (price per unit) and Index tracking.
6. Real-time Data: Use `get_live_nav` for current prices.
7. Escalation: Use `escalate_to_human` for payment failures or high frustration.

RULES:
- Use `search_knowledge_base` for fund details (NAV, expense ratio, exit load).
- Use `get_portfolio_summary` for user-specific data.
- Redact PII (PAN/Aadhaar). No hallucinating numbers.
- DO NOT provide individual stock tips or speculative advice.
- NOTE: The UI appends a standard disclaimer, but you should mention risk awareness in recommendations.
"""

class FundAgent:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found. Agent will fail.")
            self.agent_executor = None
            return
            
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            google_api_key=api_key
        )

        
        prompt = ChatPromptTemplate.from_messages([
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(llm, TOOLS, prompt)
        
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=TOOLS, 
            verbose=True,
            handle_parsing_errors=True
        )
        
    def _needs_disclaimer(self, query: str, response: str) -> bool:
        trigger_keywords = [
            "recommend", "suggest", "invest", "buy", "sell", "return", 
            "performance", "growth", "yield", "nav", "historical", "portfolio"
        ]
        combined_text = (query + " " + response).lower()
        for kw in trigger_keywords:
            if kw in combined_text:
                return True
        return False

    def chat(self, user_input: str, user_id: Optional[str] = None) -> str:
        if not self.agent_executor:
            return "Configuration Error: Google API key is missing."
            
        # 1. PII Redaction on input
        user_input = PIIRedactor.redact(user_input)

        # 2. Input Guardrails
        is_safe, error_msg = Guardrails.validate_input(user_input)
        if not is_safe:
            return error_msg

        try:
            # 3. Inject dynamic context (Current Date/Time)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            agent_input = f"[System: Today is {current_time}] " + user_input
            
            if user_id:
                agent_input += f" [System note: The current user's user_id is '{user_id}'.]"
                
            # 4. Agent Execution
            response = self.agent_executor.invoke({"input": agent_input})
            raw_output = response.get("output", "")
            
            # Handle case where output is a list of dicts (multimodal/modern Gemini format)
            if isinstance(raw_output, list):
                text_parts = []
                for part in raw_output:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                    else:
                        text_parts.append(str(part))
                answer = "\n".join(text_parts)
            else:
                answer = str(raw_output)
            
            # 4. Output Guardrails
            answer = Guardrails.validate_output(answer, user_input)

            # 5. Disclaimer Injection
            if self._needs_disclaimer(str(user_input), str(answer)):
                if "Past performance is not an indicator" not in answer:
                    answer += "\n\n" + SEBI_DISCLAIMER

            
            # 6. PII Redaction on output
            return PIIRedactor.redact(answer)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Agent execution error: {error_msg}")
            
            if "429" in error_msg or "rate_limit_exceeded" in error_msg.lower() or "quota" in error_msg.lower():
                return "Gemini Quota Exceeded: You are sending requests too fast for the free tier. Please wait a minute and try again."
            
            return f"An error occurred: {error_msg}"



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = FundAgent()
    print("Testing Agent...")
    print(agent.chat("Compare HDFC Mid Cap and HDFC Small Cap funds.", user_id="user_1"))
