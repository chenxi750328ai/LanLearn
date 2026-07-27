#!/bin/bash
# Install full garrytan/gstack skills into Cursor skills dirs (WSL + Windows).
# Source: /tmp/gstack-src (extracted upstream). Naming: gstack-<skill>
set -euo pipefail

SRC="${GSTACK_SRC:-/tmp/gstack-src}"
WIN_SKILLS="/mnt/c/Users/chenx/.cursor/skills"
WSL_SKILLS="${HOME}/.cursor/skills"
VC_NOTE_FILE="/tmp/gstack-vc-note.md"

if [[ ! -d "$SRC" ]]; then
  echo "FAIL: missing $SRC — fetch gstack first" >&2
  exit 1
fi

mkdir -p "$WIN_SKILLS" "$WSL_SKILLS" \
  "${HOME}/.claude/skills/gstack/bin" \
  "/mnt/c/Users/chenx/.claude/skills/gstack/bin"

cat > "$VC_NOTE_FILE" << 'NOTE'
> **VC 落地注记（陈方思 · 2026-07-27）**：本 skill 来自 `garrytan/gstack`（拷入 `~/.cursor/skills/gstack-*`，未强制跑官方 `./setup`——`~/.claude/skills/gstack/bin/gstack-*` 调用在缺失时会静默降级为默认值，不影响正文流程）。
>
> **强制覆盖**：本文件下方若出现「首次运行自动 `git add CLAUDE.md && git commit`」类步骤，**禁止执行**——vcompany 纪律是「未经用户明确要求禁止提交」，遇到这类步骤直接跳过，不询问、不静默执行。其余 gstack 正文照常可用。
>
> **LanLearn / es 专项**：`/land-and-deploy` **技能可装**，但对无云部署产品 **禁止执行上云**（见计划 H 节）。宣称可用仍须 pytest + Playwright + `/qa` 三证。

NOTE

# Skill dirs = immediate children that contain SKILL.md (exclude repo root SKILL.md usage as meta)
mapfile -t SKILLS < <(find "$SRC" -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/SKILL.md' \; -print | sort)

install_one() {
  local skill_path="$1"
  local name
  name="$(basename "$skill_path")"
  local dest_name="gstack-${name}"
  local tmp="/tmp/install-${dest_name}"
  rm -rf "$tmp"
  mkdir -p "$tmp"
  # copy skill tree (SKILL.md + references/templates/etc.)
  cp -a "$skill_path"/. "$tmp"/
  # prepend VC note once
  if [[ -f "$tmp/SKILL.md" ]] && ! grep -q 'VC 落地注记' "$tmp/SKILL.md"; then
    local body
    body="$(cat "$tmp/SKILL.md")"
    # insert after YAML frontmatter (first --- ... ---)
    python3 - "$tmp/SKILL.md" "$VC_NOTE_FILE" <<'PY'
import sys
path, note_path = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
note = open(note_path, encoding="utf-8").read().rstrip() + "\n\n"
if text.startswith("---"):
    end = text.find("\n---", 3)
    if end != -1:
        end = end + len("\n---")
        text = text[:end] + "\n\n" + note + text[end:].lstrip("\n")
    else:
        text = note + text
else:
    text = note + text
open(path, "w", encoding="utf-8").write(text)
PY
  fi
  for root in "$WSL_SKILLS" "$WIN_SKILLS"; do
    rm -rf "${root}/${dest_name}"
    mkdir -p "${root}/${dest_name}"
    cp -a "$tmp"/. "${root}/${dest_name}/"
  done
  echo "OK $dest_name"
}

echo "Installing ${#SKILLS[@]} skills…"
for s in "${SKILLS[@]}"; do
  install_one "$s"
done

# Helper binaries (best-effort; skills degrade if missing)
if [[ -d "$SRC/bin" ]]; then
  cp -a "$SRC/bin"/. "${HOME}/.claude/skills/gstack/bin/" || true
  cp -a "$SRC/bin"/. "/mnt/c/Users/chenx/.claude/skills/gstack/bin/" || true
  echo "OK bin helpers copied"
fi

# Inventory
echo "==== WSL gstack-* count ===="
ls -1 "$WSL_SKILLS" | grep -c '^gstack-' || true
echo "==== WIN gstack-* count ===="
ls -1 "$WIN_SKILLS" | grep -c '^gstack-' || true
echo "==== names ===="
ls -1 "$WSL_SKILLS" | grep '^gstack-' | sort
