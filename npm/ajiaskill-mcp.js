#!/usr/bin/env node
"use strict";

const { spawn } = require("node:child_process");
const path = require("node:path");

const script = path.join(__dirname, "..", "bin", "ajia");
const python = process.env.AJIA_PYTHON || process.env.PYTHON || "python3";
const child = spawn(python, [script, "mcp", ...process.argv.slice(2)], {
  stdio: "inherit",
});

child.on("error", (error) => {
  console.error(`ajiaskill-mcp: failed to start ${python}: ${error.message}`);
  console.error("Set AJIA_PYTHON to a Python 3.10+ interpreter.");
  process.exit(127);
});

child.on("exit", (code) => process.exit(code ?? 1));
