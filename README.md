# Research Skills

A personal collection of Claude Code skills for academic / research workflows. Each subdirectory is a self-contained skill with `SKILL.md` + optional `scripts/` + `references/`.

## Skills

| Skill | Triggers when... |
|---|---|
| [`literature-scan/`](./literature-scan/) | Doing a lit review, finding related papers, checking novelty, verifying citations resolve, auditing an existing scan. |

(Add more skills here as they accumulate.)

## How to install on a new machine

A Claude Code skill lives at a path that Claude knows to look in. There are three ways to wire this repo up:

### Option A — Symlink each skill into `~/.claude/skills/` (simplest, personal use)

```bash
# Clone the repo somewhere durable
cd ~/Code
git clone <your-github-url> research-skills

# Make sure the skills dir exists
mkdir -p ~/.claude/skills

# Link each skill
ln -s ~/Code/research-skills/literature-scan ~/.claude/skills/literature-scan
```

Restart Claude Code (or open a new session). The skill should appear in the available-skills list when its trigger phrases come up.

### Option B — Package as a Claude Code plugin (sharing with others)

If you want to share these as a plugin, follow the Claude Code plugin format (see <https://docs.claude.com/claude-code/plugins>). Briefly: add a `plugin.json` at the repo root, put each skill under `skills/<name>/SKILL.md`, then publish the plugin.

### Option C — Just keep it as a reference, no auto-trigger

Don't symlink. Treat each `SKILL.md` as a manual playbook — when you start a lit-scan session, paste the SKILL.md content into the conversation as context. Less automatic but zero install.

## Verifying a skill is loaded

After installing (Option A or B), start a new Claude Code session in any project and ask something like "do a literature scan for X." If the skill is loaded, Claude should reference the skill in its first response (or you'll see the skill name surfaced internally). If not, check `/help` or the docs for the current skill-loading convention — Claude Code's exact path conventions occasionally change.

## Contributing your own lessons back

Each skill has a `references/` directory for detailed gotchas / templates. When you learn something new from a real session:
1. Update the relevant `references/*.md` file (don't bloat `SKILL.md` itself).
2. If a workflow change is broad enough to affect the protocol, update `SKILL.md`'s "Recommended workflow" section too.
3. Commit with a message describing what session taught you the lesson — future-you will want the context.

## License

MIT (or whatever you prefer — choose before pushing).
