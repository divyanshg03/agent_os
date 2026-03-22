import ollama
import json

MODEL = "qwen2.5:7b"


def agent_1_generate(user_query):
    prompt = f"""
You are a banking assistant helping a borrower.

STRICT RULES:
- Do NOT make false promises
- Do NOT invent numbers
- Be professional and realistic

User Query:
{user_query}

Return ONLY JSON:
{{
  "response": "...",
  "risk_flag": false
}}
"""

    response = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    options={
        "num_predict": 120
        }
    )

    content = response['message']['content']

    try:
        return json.loads(content)
    except:
        return {"response": content, "risk_flag": True}


def agent_2_validate(agent1_output):
    prompt = f"""
You are a strict banking compliance validator, calidating each and every response given 
by the banking assistant.

Check the response against:
1. No false promises
2. No made-up numbers
3. No policy violations

Response:
{agent1_output}

Return ONLY JSON:
{{
  "valid": true/false,
  "issues": "..."
}}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={
            "num_predict": 120 
        }
    )

    content = response['message']['content']

    try:
        return json.loads(content)
    except:
        return {"valid": False, "issues": "Parsing error"}