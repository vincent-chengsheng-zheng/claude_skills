#!/usr/bin/env bash
# Run once after cloning on a new machine:
#   bash setup.sh
# Symlinks every skill in this repo into ~/.claude/skills/ so Claude Code
# picks them up globally in any project folder.

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

mkdir -p "$SKILLS_DIR"

for skill_dir in "$REPO_DIR"/*/; do
    skill_name="$(basename "$skill_dir")"
    # Skip non-skill directories (no SKILL.md)
    [ -f "$skill_dir/SKILL.md" ] || continue
    ln -sfn "$skill_dir" "$SKILLS_DIR/$skill_name"
    echo "linked: $skill_name -> $SKILLS_DIR/$skill_name"
done

echo "Done. Restart Claude Code (or open a new session) to activate skills."
