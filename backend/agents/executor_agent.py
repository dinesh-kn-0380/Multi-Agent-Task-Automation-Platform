import os
import json
from openai import OpenAI

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
    def __init__(self, model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        self.model = model

    def _get_client(self):
        return OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "http://localhost:3001", "X-Title": "Multi-Agent Platform"}
        )

    async def execute_task(self, task: dict, goal_context: str):
        prompt = f"Goal Context: {goal_context}\nTask to execute: {task['title']}\nDescription: {task['description']}"
        
        client = self._get_client()
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": EXECUTOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
