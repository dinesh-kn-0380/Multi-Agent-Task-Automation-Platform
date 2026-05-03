import os
import json
from openai import OpenAI

PLANNER_SYSTEM_PROMPT = """
You are the specialized PLANNER AGENT of the Multi-Agent Task Automation Platform.
Your responsibility is to analyze the user goal and break it into ordered, non-overlapping steps.

CONSTRAINTS:
- Ensure steps are actionable and logically connected.
- You do NOT execute tasks.
- You provide the roadmap for the EXECUTOR agents.

OUTPUT FORMAT:
Return a JSON object with:
- goal_understanding: A clear, deep interpretation of the user's intent.
- tasks: Numbered list of steps {id, title, description}.
"""

class PlannerAgent:
    def __init__(self, model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        self.model = model

    def _get_client(self):
        return OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "http://localhost:3001", "X-Title": "Multi-Agent Platform"}
        )

    async def plan(self, goal: str, context: list = None):
        import requests
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": f"User Goal: {goal}"}
        ]
        
        print(f"[PLANNER] 🤖 Requesting plan from {self.model}...")
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                    "HTTP-Referer": "http://localhost:3001",
                    "X-Title": "Multi-Agent Platform",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": "openai/gpt-3.5-turbo",
                    "messages": messages,
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                })
            )
            
            if response.status_code != 200:
                print(f"[PLANNER] ❌ API ERROR: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter Error {response.status_code}: {response.text}")

            print("[PLANNER] ✅ Response received.")
            raw_content = response.json()["choices"][0]["message"]["content"]
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                # Fallback: extract json from markdown blocks
                import re
                match = re.search(r'\{.*\}', raw_content.replace('\n', ''), re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                return {"goal_understanding": "Fallback logic applied.", "tasks": []}
        except Exception as e:
            print(f"[PLANNER] ❌ FATAL ERROR: {str(e)}")
            raise e
