# How to work with Agent Zero (for Shaan)

Shaan, 4 Oct 2026: "teach me how you want me to actually interact with the system through you. When to talk to you, when to talk
to other agents ... Sometimes I need to upskill myself." Built from what the labs and the best operators do
(`research/agent-zero-v2/human-operator.md`) and from what went wrong for us in September and October.

## The one rule
**Talk to Agent Zero.** One voice in. It turns what you say into jobs, runs them on the right model, checks them, lands them, and
shows you what needs your eye. Two thirds of our tokens on 2-3 Oct went on agents talking to agents; one front door fixes that.

## When to talk to Agent Zero (almost always)
- Anything new: an idea, a bug, a client ask, a feeling that something is off.
- "Where are we?" You get X of Y, what is live, and the one thing only you can do.
- Feedback on something you were shown.
- Changing priorities, or stopping something.

## When to talk to another agent directly (rare)
- Only when you are sitting with **the one coder** on a project for fast taste back-and-forth (tuning a screen together). Agent
  Zero tells you which agent that is. When you are done, tell Agent Zero "finished with X" so it picks the thread back up.
- Never relay between agents, and never ask one agent what another did. Ask Agent Zero; it reads their files.

## How to say what you want (30 seconds, by voice)
1. **Done when:** what is true when it is finished ("I can open the Tokens page and see today's spend per model").
2. **Why**, in one line, so the trade-offs go your way.
3. **Must work or taste?** "This must never break" gets a test. "I'll judge it by eye" gets a screenshot.
4. **Hands off:** what must not change ("don't touch my side nav").

## What comes back to you
- **A Look**: a link or screenshot, with your words beside it, only when taste decides. Answer with changes you can see: "more
  space under the header", "v2, not v3", "the old icon was better".
- **The board** (Agent Base) shows everything else as X of Y. Nothing pings you.
- **"Needs you"** is only for things only you can do: money, a login, a password, your presence, a call no one else can make.

## When to interrupt
It is doing the wrong thing, the same fix failed twice, or it touched your design. Say "stop: the outcome is X". That is all it needs.

## What you don't do any more
Restart agents, relay messages, test things yourself, watch progress, approve every step.

## Handing over UI issues (the punch list)
Shaan, 4 Oct: "i'll hand go through some small issues and then you can note them down and somehow we can get one builder to tick them off".
- Say them to Agent Zero as you see them, screenshots welcome. Each becomes a task with your words (`UI: ...`).
- Agent Zero sorts each one: **clear** goes straight to the Builder; **needs reasoning** (a layout, a top bar) gets options from Agent
  Zero first, and you pick by voice.
- **One Builder** (Codex Sol) works the list in batches, one commit per task, with before/after screenshots. It is a row in Agent
  Base's left nav: click it to watch the ticket it is on. You never talk to it; Agent Zero lands its work and checks it live.
- **Fast lane, about 5 minutes an item:** the Builder locates every item in one pass, reads only the lines it changes, takes all
  screenshots in one browser, and leaves the full checks to the ship queue (which runs them at landing anyway). Minutes per item are
  measured from `codex-run`'s log; anything slower, Agent Zero finds out why.
- **Design before build** (Shaan, 4 Oct 05:04: "if you'd reasoned it better I feel like you would have been able to get something
  better"). A surface he looks at is designed first: Agent Zero (Opus) reasons out what it is for, then draws it as a picture from the
  existing components, and he reacts to the picture in minutes. Only an approved picture goes to the Builder, which builds to match it
  and proves the match with screenshots side by side. Bug fixes and data work skip the picture.
- A component you love gets a **taste lock**: a screenshot test, so no builder changes it without you.

## How the agents are arranged (so you know who does what)
- **One coder per codebase**: two writers in one repo cause conflicts and rework.
- **Many researchers**: they read and write findings files in `research/`, never code, so many can run at once. You can watch
  them on the Research page; Agent Zero reads their findings and tells you what changed.
- **Agent Zero (Opus)** decides, specs, checks and lands. Cheap models (Luna, DeepSeek) do most of the work; Sol and Opus take
  the hard parts. Which model gets which job is in `routing.json`.

## Getting better at it (your five skills)
1. **Say "done when".** It is the biggest single lever: a clear finish line is what a machine can check.
2. **Give taste as changes you can see**, against a screenshot.
3. **Batch your feedback**: one message with every change beats five.
4. **Pick from variations.** Ask for three; picking is faster than describing.
5. **Ask what it cost.** Once a week: tokens per change that went live. It should fall every week.
