import os
import json
from openai import OpenAI

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
    def __init__(self, model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        self.model = model

    def _get_client(self):
        return OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "http://localhost:3001", "X-Title": "Multi-Agent Platform"}
        )

    async def finalize(self, goal: str, results: list):
        prompt = f"Original Goal: {goal}\nAgent Results: {json.dumps(results)}"
        
        client = self._get_client()
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": FINAL_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
