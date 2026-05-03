import os
import json
from openai import AsyncOpenAI

EXECUTOR_SYSTEM_PROMPT = """
You are a specialized EXECUTOR AGENT. 
Your responsibility is to handle a specific subtask assigned by the Orchestrator.

CONSTRAINTS:
- Execute with precision using deep reasoning.
- Return concise and relevant outputs.
- Focus strictly on your assigned subtask.

OUTPUT FORMAT:
Return a JSON object with:
- output: Detailed but concise result of your execution.
- reasoning: Short explanation of how you solved it.
- confidence: Float (0-1).
- status: "completed" | "failed"
"""

class ExecutorAgent:
    def __init__(self, model: str = "google/gemini-2.5-flash"):
        self.model = model

    def _get_client(self):
        base_url = os.environ.get("OPENAI_BASE_URL")
        return AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=base_url if base_url else None,
            default_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "Multi-Agent Platform"} if base_url else None
        )

    async def execute_task(self, task: dict, goal_context: str):
        prompt = f"Goal Context: {goal_context}\nTask to execute: {task['title']}\nDescription: {task['description']}"
        
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": EXECUTOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
