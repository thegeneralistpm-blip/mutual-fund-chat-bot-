MOCK_USERS = {
    "user_1": {
        "name": "Alice",
        "risk_profile": "High",
        "portfolio": [
            {"fund": "Zerodha Nifty Large Midcap 250 Index Fund", "amount": 50000, "returns": "12%"},
            {"fund": "Zerodha ELSS Tax Saver Nifty Large Midcap 250 Index Fund", "amount": 20000, "returns": "18%"}
        ],
        "sips": [
            {"fund": "Zerodha Nifty Large Midcap 250 Index Fund", "monthly_amount": 5000, "status": "Active"}
        ]
    },
    "user_2": {
        "name": "Bob",
        "risk_profile": "Low",
        "portfolio": [
            {"fund": "Zerodha Gold ETF FoF", "amount": 100000, "returns": "6%"}
        ],
        "sips": []
    }
}

def get_user_context(user_id: str) -> dict:
    return MOCK_USERS.get(user_id, None)

def format_user_context_for_prompt(user_data: dict) -> str:
    if not user_data:
        return "No user portfolio context available."
    
    ctx = f"User Name: {user_data['name']}\n"
    ctx += f"Risk Profile: {user_data['risk_profile']}\n"
    ctx += "Current Portfolio Holdings:\n"
    if user_data['portfolio']:
        for item in user_data['portfolio']:
            ctx += f"- {item['fund']}: Rs. {item['amount']} (Returns: {item['returns']})\n"
    else:
        ctx += "- None\n"
        
    ctx += "Active SIPs:\n"
    if user_data['sips']:
        for sip in user_data['sips']:
            ctx += f"- {sip['fund']}: Rs. {sip['monthly_amount']}/month ({sip['status']})\n"
    else:
        ctx += "- None\n"
        
    return ctx
