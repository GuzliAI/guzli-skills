# Install Guzli skills on common agents

All of these hosts understand (or import) the [Agent Skills](https://agentskills.io) layout: a folder containing `SKILL.md`.

Replace `<skill>` with `guzli-mcp-core`, `guzli-mcp-email-outreach`, or `guzli-mcp-voice-campaigns`.

```bash
REPO=https://github.com/GuzliAI/guzli-skills.git
git clone "$REPO" /tmp/guzli-skills
```

## Claude Code

User skills:

```bash
mkdir -p ~/.claude/skills
cp -R /tmp/guzli-skills/skills/<skill> ~/.claude/skills/<skill>
```

Project skills (repo-local):

```bash
mkdir -p .claude/skills
cp -R /tmp/guzli-skills/skills/<skill> .claude/skills/<skill>
```

Restart or start a new Claude Code session so skills are rediscovered.

## OpenAI Codex / ChatGPT desktop skills

Codex scans `.agents/skills` (and related scopes). ChatGPT desktop / Codex also use Agent Skills.

User-wide:

```bash
mkdir -p ~/.agents/skills
cp -R /tmp/guzli-skills/skills/<skill> ~/.agents/skills/<skill>
```

Repo-local (recommended for teams):

```bash
mkdir -p .agents/skills
cp -R /tmp/guzli-skills/skills/<skill> .agents/skills/<skill>
```

Each skill ships `agents/openai.yaml` declaring the Guzli MCP HTTP endpoint as a dependency hint. You still need Guzli MCP authenticated in that product.

Invoke explicitly with `$guzli-mcp-core` / `@` skill pickers where available, or rely on description matching.

## Cursor

```bash
mkdir -p .cursor/skills
cp -R /tmp/guzli-skills/skills/<skill> .cursor/skills/<skill>
```

Cursor also discovers `.claude/skills` and `.codex/skills` / `.agents/skills` for compatibility. Grok Bot-style workflow folders can use the same copy of `SKILL.md`.

## Grok Bot (and similar workflow loaders)

Copy into your agent’s skills/workflows directory so each skill is `<id>/SKILL.md`. Keep the folder name equal to frontmatter `name`.

## OpenClaw

Workspace:

```bash
mkdir -p skills
cp -R /tmp/guzli-skills/skills/<skill> ./skills/<skill>
```

Global:

```bash
mkdir -p ~/.openclaw/skills
cp -R /tmp/guzli-skills/skills/<skill> ~/.openclaw/skills/<skill>
```

Or install from Git when your CLI expects a single-skill root (copy one folder, or use `--as`):

```bash
# example: local path whose root contains SKILL.md
openclaw skills install ./skills/guzli-mcp-core
```

ClawHub publish is optional for wider OpenClaw distribution (`clawhub skill publish <path>`).

## Muse Code

Muse imports Claude/Codex skill trees and uses Agent Skills-style folders:

```bash
muse skills import --from claude   # if already installed under ~/.claude/skills
# or copy into Muse’s skills path / import from this repo’s skills/<skill>
```

Repo `AGENTS.md` points agents at `skills/` when working inside this repository.

## Generic / other hosts

Any agent that implements agentskills.io:

1. Ensure Guzli MCP is connected in that host.
2. Place `skills/<skill>/` (with `SKILL.md` inside) on that host’s skill search path.
3. Prefer explicit invoke (`/skill`, `$skill`, `@skill`) once to confirm load, then rely on description triggers.

## Verify

Ask the agent: “What Guzli skills do you have?” or invoke `guzli-mcp-core` and request `list_lifecycle_stages` or `list_campaigns` via MCP.
