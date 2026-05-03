import os
import json
from openai import AsyncOpenAI

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
    def __init__(self, model: str = "google/gemini-2.5-flash"):
        self.model = model

    def _get_client(self):
        base_url = os.environ.get("OPENAI_BASE_URL")
        return AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=base_url if base_url else None,
            default_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "Multi-Agent Platform"} if base_url else None
        )

    async def plan(self, goal: str, context: list = None):
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": f"User Goal: {goal}"}
        ]
        if context:
            messages.insert(1, {"role": "system", "content": f"Conversation Context: {json.dumps(context)}"})

        client = self._get_client()
        try:
            print(f"[PLANNER] 🤖 Requesting plan from {self.model}...")
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            print("[PLANNER] ✅ Response received.")
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[PLANNER] ❌ API ERROR: {str(e)}")
            raise e
