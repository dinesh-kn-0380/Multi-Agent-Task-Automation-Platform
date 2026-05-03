import asyncio
import json
import os
import uuid
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from backend.memory.conversation_memory import memory_store
from backend.workflows.orchestrator import MultiAgentWorkflow, WorkflowState

app = Flask(__name__)
CORS(app)

workflow = MultiAgentWorkflow(
    planner_model=os.getenv("PLANNER_MODEL", "google/gemini-2.5-flash"),
    executor_model=os.getenv("EXECUTOR_MODEL", "google/gemini-2.5-flash"),
    final_model=os.getenv("FINAL_MODEL", "google/gemini-2.5-flash"),
)

def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Multi-Agent Platform"})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())
    use_stream = data.get("stream", False)

    if not message:
        return jsonify({"error": "message is required"}), 400

    memory = memory_store.get_or_create(session_id)
    context = memory.get_context()

    if use_stream:
        return stream_response(message, session_id, memory, context)

    run = run_async(workflow.run(message, context))
    memory.add("user", message)
    memory.add("assistant", run.final_response.get("final_answer", ""))

    return jsonify({
        "run_id": run.run_id,
        "session_id": session_id,
        **run.final_response,
        "timing": run.timing
    })

import queue
import threading

def stream_response(message, session_id, memory, context):
    print(f"\n[SERVER] 🚀 NEW STREAM REQUEST: {message[:50]}...")
    q = queue.Queue()
    # Immediate heartbeat to prove connection is alive
    q.put(json.dumps({"state": "planning", "data": {"status": "Connection established. Waking up agents..."}}))

    def run_in_thread():
        print("[THREAD] 🧵 Background thread started.")
        async def callback(state, data=None):
            print(f"[CALLBACK] 📡 Emitting State: {state.value}")
            q.put(json.dumps({"state": state.value, "data": data}))

        async def run_pipeline():
            try:
                print("[PIPELINE] 🌊 Starting Orchestrator run...")
                run = await workflow.run(message, context, callback)
                print("[PIPELINE] ✅ Workflow run complete.")
                
                memory.add("user", message)
                memory.add("assistant", run.final_response.get("final_answer", ""))
                
                final_data = json.dumps({
                    "state": "done",
                    "data": {
                        "run_id": run.run_id,
                        **run.final_response,
                        "timing": run.timing
                    }
                })
                q.put(final_data)
                q.put("[DONE]")
                print("[PIPELINE] 🏁 Terminal [DONE] token sent to queue.")
            except Exception as e:
                print(f"[PIPELINE] ❌ FATAL ERROR: {str(e)}")
                q.put(json.dumps({"state": "error", "data": str(e)}))
                q.put("[DONE]")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_pipeline())
        finally:
            print("[THREAD] 🛑 Loop closed.")
            loop.close()

    threading.Thread(target=run_in_thread, daemon=True).start()

    def generate():
        print("[STREAM] ⚡ SSE Generator started.")
        while True:
            item = q.get()
            if item == "[DONE]":
                print("[STREAM] 🔌 SSE Stream closed.")
                yield "data: [DONE]\n\n"
                break
            print(f"[STREAM] 📤 Flushing Chunk: {len(item)} bytes")
            yield f"data: {item}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
