import asyncio
import time
import uuid
from enum import Enum
from typing import Callable, List, Optional
from backend.agents.planner_agent import PlannerAgent
from backend.agents.executor_agent import ExecutorAgent
from backend.agents.final_agent import FinalAgent

class WorkflowState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    FINALIZING = "finalizing"
    DONE = "done"
    ERROR = "error"

class MultiAgentWorkflow:
    def __init__(self, planner_model: str, executor_model: str, final_model: str):
        self.planner = PlannerAgent(planner_model)
        self.executor = ExecutorAgent(executor_model)
        self.finalizer = FinalAgent(final_model)

    async def run(self, goal: str, context: list = None, callback: Optional[Callable] = None):
        run_id = str(uuid.uuid4())
        results = []
        timing = {"start": time.time()}
        print(f"\n[ORCHESTRATOR] 🟢 Starting Run ID: {run_id}")

        try:
            # ── Phase 1: Planning ─────────────────────────────────────────────
            print("[ORCHESTRATOR] 🧠 Phase 1: Planning...")
            if callback: await callback(WorkflowState.PLANNING, {"status": "Analyzing goal..."})
            plan = await self.planner.plan(goal, context)
            timing["planning"] = time.time() - timing["start"]
            print(f"[ORCHESTRATOR] 📋 Plan received with {len(plan['tasks'])} tasks.")
            
            if callback: 
                await callback(WorkflowState.PLANNING, {
                    "tasks": plan["tasks"],
                    "status": "Goal decomposed into actionable tasks."
                })

            # ── Phase 2: Parallel Execution ───────────────────────────────────
            print("[ORCHESTRATOR] ⚡ Phase 2: Parallel Execution...")
            if callback: await callback(WorkflowState.EXECUTING, {"status": f"Spawning {len(plan['tasks'])} agents..."})
            exec_start = time.time()
            
            # Use a semaphore or limited concurrency if needed, but here we go full parallel
            async def run_single_task(task_idx, task_data):
                try:
                    # Stagger start times slightly to avoid immediate rate limit spikes
                    await asyncio.sleep(task_idx * 1.5)
                    print(f"[ORCHESTRATOR] 🤖 Agent {task_idx+1} starting task: {task_data['title']}")
                    
                    if callback:
                        await callback(WorkflowState.EXECUTING, {
                            "task_id": task_data["id"],
                            "status": f"Task '{task_data['title']}' started.",
                            "task_status": "started"
                        })

                    res = await self.executor.execute_task(task_data, plan["goal_understanding"])
                    print(f"[ORCHESTRATOR] ✅ Agent {task_idx+1} finished.")

                    # Report task completion to the frontend
                    if callback:
                        await callback(WorkflowState.EXECUTING, {
                            "task_id": task_data["id"],
                            "completed_task_id": task_data["id"],
                            "status": f"Task '{task_data['title']}' completed.",
                            "task_status": "completed"
                        })
                    return {
                        "task_id": task_data["id"],
                        "task_title": task_data["title"],
                        **res
                    }
                except Exception as e:
                    print(f"[ORCHESTRATOR] ❌ Agent {task_idx+1} FAILED: {e}")
                    if callback:
                        await callback(WorkflowState.EXECUTING, {
                            "task_id": task_data["id"],
                            "completed_task_id": task_data["id"],
                            "status": f"Task '{task_data['title']}' failed.",
                            "task_status": "failed",
                            "error": str(e)
                        })
                    return {
                        "task_id": task_data["id"],
                        "task_title": task_data["title"],
                        "output": f"Execution failed due to error: {str(e)}",
                        "confidence": 0,
                        "status": "error"
                    }

            # Gather all agent executions
            tasks = [run_single_task(i, t) for i, t in enumerate(plan["tasks"])]
            results = await asyncio.gather(*tasks)
            print(f"[ORCHESTRATOR] 📊 All agents reported back.")
            
            timing["execution"] = time.time() - exec_start

            # ── Phase 3: Final Synthesis ──────────────────────────────────────
            print("[ORCHESTRATOR] ✍️ Phase 3: Final Synthesis...")
            if callback: await callback(WorkflowState.FINALIZING, {"status": "Synthesizing agent results..."})
            final_start = time.time()
            final_res = await self.finalizer.finalize(goal, results)
            timing["finalization"] = time.time() - final_start
            timing["total"] = time.time() - timing["start"]
            print("[ORCHESTRATOR] ✨ Synthesis complete.")

            class RunResult:
                def __init__(self, rid, state, plan, agent_results, final_response, timing):
                    self.run_id = rid
                    self.state = state
                    self.plan = plan
                    self.agent_results = agent_results
                    self.final_response = {
                        **final_response, 
                        "agent_results": agent_results, 
                        "task_breakdown": plan["tasks"], 
                        "goal_understanding": plan["goal_understanding"]
                    }
                    self.timing = timing

            return RunResult(run_id, WorkflowState.DONE, plan, results, final_res, timing)

        except Exception as e:
            print(f"[ORCHESTRATOR] 🚨 CRITICAL ERROR: {e}")
            if callback: await callback(WorkflowState.ERROR, {"error": str(e)})
            raise e
