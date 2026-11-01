#!/usr/bin/env python3
"""Live MCP-only six-host test: search, use, and native-first refusal."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "bin" / "ajia"


class Client:
    def __init__(self, host: str) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, str(BIN), "mcp", "--host", host],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=dict(os.environ, AJIA_AUTO_UPDATE="0"),
        )
        self.next_id = 1
        init = self.request("initialize", {})
        self.server = init.get("result", {}).get("serverInfo", {}).get("name")

    def request(self, method: str, params: dict) -> dict:
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None
        request_id = self.next_id
        self.next_id += 1
        self.proc.stdin.write(
            json.dumps(
                {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
            )
            + "\n"
        )
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def tool(self, name: str, arguments: dict) -> dict:
        reply = self.request(
            "tools/call", {"name": name, "arguments": arguments}
        )
        return reply.get("result", {})

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        if self.proc.stdout:
            self.proc.stdout.close()
        if self.proc.stderr:
            self.proc.stderr.close()
        self.proc.terminate()
        self.proc.wait(timeout=5)


def main() -> int:
    for host in ("opencode", "pi", "hermes", "codex", "omp", "claude"):
        client = Client(host)
        assert client.server == "ajiaskill", (host, client.server)
        print(host, "server:", client.server)
        try:
            search = client.tool(
                "ajia_search",
                {"query": "draw the architecture", "limit": 3, "host": host},
            )
            results = json.loads(search["content"][0]["text"])
            archify = next(
                (item for item in results if item["name"] == "archify"), None
            )
            print(
                host,
                "search:",
                archify["id"] if archify else None,
                "native=" + str(archify.get("native") if archify else None),
            )
            if archify:
                used = client.tool(
                    "ajia_use", {"id": archify["id"], "host": host}
                )
                print(
                    host,
                    "use archify:",
                    "native refusal" if used.get("isError") else "body",
                    (used.get("content") or [{}])[0].get("text", "")[:80],
                )

            skill_search = client.tool(
                "ajia_search",
                {"query": "grill me on a vague idea", "limit": 3, "host": host},
            )
            skill_results = json.loads(skill_search["content"][0]["text"])
            skill = next(
                (item for item in skill_results if item["name"] == "grill-me"), None
            )
            if skill:
                skill_use = client.tool(
                    "ajia_use", {"id": skill["id"], "host": host}
                )
                body = (skill_use.get("content") or [{}])[0].get("text", "")
                parsed = json.loads(body) if not skill_use.get("isError") else {}
                print(
                    host,
                    "use grill-me:",
                    "error" if skill_use.get("isError") else f"body {len(parsed.get('body', ''))} chars",
                )

            foundry_search = client.tool(
                "ajia_search",
                {"query": "mcp health", "limit": 3, "host": host},
            )
            foundry_results = json.loads(foundry_search["content"][0]["text"])
            foundry = next(
                (item for item in foundry_results if item["name"] == "mcp-health-check"),
                None,
            )
            if foundry:
                foundry_use = client.tool(
                    "ajia_use", {"id": foundry["id"], "host": host}
                )
                body = (foundry_use.get("content") or [{}])[0].get("text", "")
                parsed = json.loads(body) if not foundry_use.get("isError") else {}
                print(
                    host,
                    "use foundry:",
                    "error" if foundry_use.get("isError") else f"body {len(parsed.get('body', ''))} chars",
                )
        finally:
            client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
