# ADR 0003: How Agent Zero writes to Shaan

**Status:** accepted, 6 Oct 2026. **Supersedes** the "X of Y with ✅/⏳ rows, Needs you / Look / Next" scaffolding for Agent Zero's chat replies. The `adhd-agent-output` skill still holds for its first-line rule.

## Context
Agent Base renders replies as markdown inside a review card. On 6 Oct the scaffolded format came out as dropdowns and stacked status rows, and Shaan said:
- "the way you've been standardizing your output's been horrid ... should just be like your normal way in clawed code ... I don't know all these drop-down bullshits. It's just illegible."
- "titles and subtext ... tags ... hyperlinked text just the standard clawed output".
- "I like how it comes in a review document ... but look at the actual output inside".

## Decision
- **Write standard Claude markdown:**
  - a heading that says the outcome;
  - short paragraphs or bullets;
  - **bold** for the key thing;
  - real hyperlinks on the words.
- **The first line is what he should do or look at, with its URL.** If nothing needs him, say what landed and what's next.
- **No status scaffolding:** no "X of Y" headers, no ✅/⏳/⛔ rows, no "Needs you / Look / Next" labels, no nested dropdowns.
- **Short.** Five bullets or fewer per list. Cut what he didn't ask about.
- **Own a mistake in one sentence**, then the fix.
- **Tables only when comparing** (several owners against the same columns).

## Consequences
The global `CLAUDE.md` still says "state as X of Y". For Agent Zero's replies in Agent Base, this ADR wins, because it's his later and more specific word.
