# The team's skills — three roles, one front door, one map

A skill earns its place if an agent behaves differently for having read it. Three **role**
skills (the cap: well-run agent repos measure ≤3 personas) plus one installable front door.
The tool skills they point at already exist in the SISO skills estate and are not duplicated.

| Skill | Who loads it | Points at |
|---|---|---|
| `project-agent-zero` (+ `COMPACT.md`) | the resident brain of one team | `siso-owner` (dispatch), `siso-plane-ops`, `siso-credentials`, `console`, the core packet, the project's estate skill |
| `owner` | an ephemeral domain owner | `siso-owner` (being one), `tools/siso-browse`, the estate skill, `worker-contract` (to write a JOB) |
| `worker-contract` | a Qwen or Luna arm on Codex, or an owner writing a JOB | nothing — the brief is complete or it is wrong |
| `team-front-door` | any agent joining any team host | `AGENTS.md`, `team.yaml`, the role skill |

## Installing into a box

Link, do not copy, so a lesson learned while dogfooding lands in this repo:

```bash
for s in project-agent-zero owner worker-contract team-front-door; do
  ln -sfn "$(pwd)/skills/$s" ~/.claude/skills/$s
done
```

Codex arms read `teams/<slug>/workers/AGENTS.md`, which points at `worker-contract`.

## Improving one

Fix the skill in this repo the same hour you learn the lesson, in the section the lesson
belongs to, one or two sentences with the date and the cost. Commit, push. A skill nobody
trusts is worse than no skill.
