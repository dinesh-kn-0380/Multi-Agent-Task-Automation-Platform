import os
import json
from openai import AsyncOpenAI

FINAL_AGENT_SYSTEM_PROMPT = """
You are the specialized FINAL SYNTHESIS AGENT.
Your responsibility is to aggregate outputs from all agents and produce the definitive response.

CONSTRAINTS:
- Ensure the response is clean, structured, and user-friendly.
- Maintain logical flow and remove any redundancy from intermediate steps.
- The output should be a complete, actionable result.

OUTPUT FORMAT:
Return a JSON object with:
- final_answer: Markdown formatted string containing the final synthesized results.
"""

class FinalAgent:
    def __init__(self, model: str = "google/gemini-2.5-flash"):
        self.model = model

    def _get_client(self):
        base_url = os.environ.get("OPENAI_BASE_URL")
        return AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=base_url if base_url else None,
            default_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "Multi-Agent Platform"} if base_url else None
        )

    async def finalize(self, goal: str, results: list):
        prompt = f"Original Goal: {goal}\nAgent Results: {json.dumps(results)}"
        
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": FINAL_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
