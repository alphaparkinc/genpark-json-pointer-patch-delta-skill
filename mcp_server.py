"""MCP Stdio Server for JSON Pointer Patch Delta.
100% Python Standard Library.
"""
import sys
import json
from client import JSONPointerPatchDelta

engine = JSONPointerPatchDelta()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-json-pointer-patch-delta-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "resolve_pointer",
                "description": "Query value at RFC 6901 JSON Pointer path (e.g. /users/0/email)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document": {},
                        "pointer": {"type": "string"}
                    },
                    "required": ["document", "pointer"]
                }
            },
            {
                "name": "compute_patch",
                "description": "Generate RFC 6902 JSON Patch operations delta between original and modified documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "original": {},
                        "modified": {}
                    },
                    "required": ["original", "modified"]
                }
            },
            {
                "name": "apply_patch",
                "description": "Apply RFC 6902 JSON Patch operations to document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document": {},
                        "patch": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["document", "patch"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "resolve_pointer":
            out = {"pointer": args.get("pointer"), "value": engine.resolve_pointer(args.get("document"), args.get("pointer", ""))}
        elif name == "compute_patch":
            out = {"patch": engine.compute_patch(args.get("original"), args.get("modified"))}
        elif name == "apply_patch":
            out = {"result": engine.apply_patch(args.get("document"), args.get("patch", []))}
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
