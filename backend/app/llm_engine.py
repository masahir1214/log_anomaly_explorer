import httpx
import os

async def generate_real_rca(anomalies):
    # API key ko read kar ke uske aage peechay ke spaces/newlines khatam karein
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return {
            "root_cause": "API Key Missing. Add GEMINI_API_KEY to .env file.",
            "confidence": 0.0,
            "recommended_actions": ["Add API key to environment variables and restart server."]
        }
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    
    # Prompt Engineering with Real Evidence
    evidence = str(anomalies[:15]) # Send top 15 anomalies to fit context window
    prompt = f"""
    You are an expert DevOps AI. Analyze these real system anomalies:
    {evidence}
    
    Respond STRICTLY in valid JSON format with NO markdown formatting or codeblocks:
    {{
      "root_cause": "1-2 sentences explaining the likely failure",
      "confidence": 0.95,
      "recommended_actions": ["action 1", "action 2"]
    }}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Clean markdown if model ignores instruction
            text = text.replace('`json', '').replace('`', '').strip()
            import json
            return json.loads(text)
        except Exception as e:
            return {
                "root_cause": f"AI Processing Error: {str(e)}",
                "confidence": 0.0,
                "recommended_actions": ["Check API Key limits", "Review system logs"]
            }