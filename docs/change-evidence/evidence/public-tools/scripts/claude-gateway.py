# An OpenAI-compatible /v1/chat/completions endpoint backed by `claude -p`.
#
# The machine has no readable API key, only a logged-in Claude Code CLI, so
# tools that speak the OpenAI protocol (PR-Agent via LiteLLM, semantic_diff's
# openai provider) are pointed here. Each call forwards the tool's own system
# and user messages unchanged: --system-prompt replaces Claude Code's prompt,
# --tools "" removes its tools, --setting-sources "" drops settings, CLAUDE.md
# and hooks. What the CLI still adds is measured, not hidden: a bare
# "Say ok." costs 445 input tokens.
#
# Not forwarded: temperature, max_tokens, seed, response_format. Requests with
# `tools` are refused (400) rather than answered without them.
#
#   python3 claude-gateway.py <port> <log-dir>
import http.server, itertools, json, os, subprocess, sys, threading, time

port, log = int(sys.argv[1]), sys.argv[2]
os.makedirs(log, exist_ok=True)
seq, lock = itertools.count(), threading.Lock()

def text(content):
    if isinstance(content, str):
        return content
    return "".join(p.get("text", "") for p in content if isinstance(p, dict))

class H(http.server.BaseHTTPRequestHandler):
    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        with lock:
            n = next(seq)
        req = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))))
        stem = f"{log}/{n:03d}"
        json.dump(req, open(f"{stem}.request.json", "w"), indent=1)
        model = req.get("model", "")
        if req.get("tools") or not model.startswith("claude-"):
            why = "tools are not supported" if req.get("tools") else f"unsupported model {model!r}"
            json.dump({"refused": why}, open(f"{stem}.refused.json", "w"))
            return self.reply(400, {"error": {"message": f"claude-gateway: {why}"}})
        msgs = req["messages"]
        system = "\n\n".join(text(m["content"]) for m in msgs if m["role"] == "system")
        turns = [m for m in msgs if m["role"] != "system"]
        if len(turns) == 1 and turns[0]["role"] == "user":
            prompt = text(turns[0]["content"])
        else:
            prompt = "\n\n".join(f"[{m['role']}]\n{text(m['content'])}" for m in turns)
        cmd = ["claude", "-p", "--model", model, "--output-format", "json",
               "--tools", "", "--no-session-persistence", "--strict-mcp-config",
               "--setting-sources", "", "--disable-slash-commands",
               "--exclude-dynamic-system-prompt-sections",
               "--system-prompt", system or "You are a helpful assistant."]
        started = time.time()
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd="/tmp", timeout=900)
        open(f"{stem}.claude.json", "w").write(p.stdout)
        if p.stderr:
            open(f"{stem}.claude.stderr", "w").write(p.stderr)
        try:
            out = json.loads(p.stdout)
        except ValueError:
            return self.reply(502, {"error": {"message": "claude-gateway: unparseable CLI output"}})
        if out.get("is_error"):
            return self.reply(502, {"error": {"message": f"claude-gateway: {out.get('result')}"}})
        u = out["usage"]
        prompt_tokens = u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]
        resp = {"id": out["session_id"], "object": "chat.completion", "created": int(started),
                "model": next(iter(out["modelUsage"]), model),
                "choices": [{"index": 0, "finish_reason": "length" if out.get("stop_reason") == "max_tokens" else "stop",
                             "message": {"role": "assistant", "content": out["result"]}}],
                "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": u["output_tokens"],
                          "total_tokens": prompt_tokens + u["output_tokens"]}}
        json.dump(resp, open(f"{stem}.response.json", "w"), indent=1)
        self.reply(200, resp)

    def log_message(self, *a):
        pass

http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
