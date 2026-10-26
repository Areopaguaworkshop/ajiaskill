#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
CLI_SRC="$REPO_DIR/bin/ajia"
BIN_DIR="${HOME}/.local/bin"
DRY_RUN=0
UNINSTALL=0
CHECK=0
CLI_INSTALL=1
PROJECT_DIR=""

usage() {
  cat <<'EOF'
Usage: install.sh [options]

Install the ajiaskill set and the ajia CLI for the current user.

Options:
  --dry-run          Print actions; change nothing.
  --project DIR      Copy skills into DIR/.agents/skills and DIR/.claude/skills.
  --uninstall        Remove symlinks that point into this repository.
  --check            Report whether each skill and the CLI are installed.
  --no-cli           Do not link bin/ajia into ~/.local/bin.
  -h, --help         Show this help.

Default targets:
  ~/.agents/skills   Codex, OpenCode, Pi, Gemini, Cursor, Windsurf, Amp, Factory, Copilot
  ~/.claude/skills   Claude Code
  ~/.local/bin/ajia  CLI and MCP server entry point
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --check) CHECK=1; shift ;;
    --no-cli) CLI_INSTALL=0; shift ;;
    --project)
      [[ $# -ge 2 ]] || { echo "--project needs a directory" >&2; exit 2; }
      PROJECT_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -n "$PROJECT_DIR" ]]; then
  [[ -d "$PROJECT_DIR" ]] || { echo "project directory not found: $PROJECT_DIR" >&2; exit 1; }
  TARGETS=("$PROJECT_DIR/.agents/skills" "$PROJECT_DIR/.claude/skills")
  MODE="copy"
else
  TARGETS=("$HOME/.agents/skills" "$HOME/.claude/skills")
  MODE="link"
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "skills directory not found: $SKILLS_DIR" >&2
  exit 1
fi

skills=()
while IFS= read -r src; do
  skills+=("$src")
done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)

if [[ ${#skills[@]} -eq 0 ]]; then
  echo "no skills found in $SKILLS_DIR" >&2
  exit 1
fi

say() { printf '%s\n' "$*"; }
run() {
  if [[ $DRY_RUN -eq 1 ]]; then
    say "  would: $*"
  else
    "$@"
  fi
}

check_cli() {
  if [[ $CLI_INSTALL -eq 0 ]]; then
    return 0
  fi
  if [[ -L "$BIN_DIR/ajia" ]]; then
    link="$(readlink "$BIN_DIR/ajia")"
    if [[ "$link" == "$CLI_SRC" ]]; then
      say "ok     $BIN_DIR/ajia"
      return 0
    fi
  fi
  say "MISS   $BIN_DIR/ajia"
  return 1
}

install_cli() {
  if [[ $CLI_INSTALL -eq 0 ]]; then
    return 0
  fi
  if [[ -L "$BIN_DIR/ajia" ]]; then
    link="$(readlink "$BIN_DIR/ajia")"
    if [[ "$link" == "$CLI_SRC" ]]; then
      say "ok     $BIN_DIR/ajia"
    else
      say "skip   $BIN_DIR/ajia (symlink to $link)"
    fi
    return 0
  fi
  if [[ -e "$BIN_DIR/ajia" ]]; then
    say "skip   $BIN_DIR/ajia (already exists; not overwriting)"
    return 0
  fi
  run mkdir -p "$BIN_DIR"
  if [[ $DRY_RUN -eq 1 ]]; then
    say "  would: ln -s $CLI_SRC $BIN_DIR/ajia"
  else
    ln -s "$CLI_SRC" "$BIN_DIR/ajia"
    say "add    $BIN_DIR/ajia"
  fi
}

uninstall_cli() {
  if [[ $CLI_INSTALL -eq 0 || ! -L "$BIN_DIR/ajia" ]]; then
    return 0
  fi
  link="$(readlink "$BIN_DIR/ajia")"
  if [[ "$link" == "$CLI_SRC" ]]; then
    run rm "$BIN_DIR/ajia"
    say "remove $BIN_DIR/ajia"
  else
    say "skip   $BIN_DIR/ajia (symlink to $link)"
  fi
}

if [[ $CHECK -eq 1 ]]; then
  missing=0
  for target in "${TARGETS[@]}"; do
    for src in "${skills[@]}"; do
      name="$(basename "$src")"
      if [[ -e "$target/$name" || -L "$target/$name" ]]; then
        say "ok   $target/$name"
      else
        say "MISS $target/$name"
        missing=1
      fi
    done
  done
  check_cli || missing=1
  exit "$missing"
fi

if [[ $UNINSTALL -eq 1 ]]; then
  uninstall_cli
  for target in "${TARGETS[@]}"; do
    for src in "${skills[@]}"; do
      name="$(basename "$src")"
      dest="$target/$name"
      if [[ -L "$dest" ]]; then
        link="$(readlink "$dest")"
        if [[ "$link" == "$src" ]]; then
          run rm "$dest"
          say "remove $dest"
        else
          say "skip   $dest (symlink to $link)"
        fi
      elif [[ -e "$dest" ]]; then
        say "skip   $dest (not a symlink; remove it manually)"
      fi
    done
  done
  exit 0
fi

install_cli

for target in "${TARGETS[@]}"; do
  run mkdir -p "$target"
  for src in "${skills[@]}"; do
    name="$(basename "$src")"
    dest="$target/$name"
    if [[ -L "$dest" ]]; then
      link="$(readlink "$dest")"
      if [[ "$link" == "$src" ]]; then
        say "ok     $dest"
      else
        say "skip   $dest (symlink to $link)"
      fi
    elif [[ -e "$dest" ]]; then
      say "skip   $dest (already exists; not overwriting)"
    else
      if [[ $DRY_RUN -eq 1 ]]; then
        if [[ "$MODE" == "link" ]]; then
          say "  would: ln -s $src $dest"
        else
          say "  would: cp -R $src $dest"
        fi
      elif [[ "$MODE" == "link" ]]; then
        ln -s "$src" "$dest"
        say "add    $dest"
      else
        cp -R "$src" "$dest"
        say "add    $dest"
      fi
    fi
  done
done
