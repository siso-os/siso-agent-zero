# Publishing the front-end

The front end is `docs/index.html`, live at **https://siso-project-team.pages.dev/** (Cloudflare
Pages project `siso-project-team`, created 2026-09-11 with the account's wrangler login).

```sh
tools/publish-front        # deploys docs/ and refuses to report success until the live page hashes the same
```

Rules: nothing under `teams/` is ever published — it holds the human's verbatim words. The
script scans `docs/` for anything that looks like a key before uploading. Any agent that
changes how the team works updates `docs/index.html` and republishes in the same commit series;
a design that only lives in a skill is invisible to the human. `agent-team-v2.html` stays as
the record of what broke on 2026-09-11 and why each mechanism exists.
