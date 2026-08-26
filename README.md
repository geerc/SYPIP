# Sleeper Power Rankings

The SYPIP-specific website and deployment configuration for weekly Sleeper fantasy-football reports. Ranking generation is provided by the shared [fantasy-football-reports](https://github.com/geerc/fantasy-football-reports) package.

- ESPN-style two-step-dominance performance rankings
- KeepTradeCut roster-value rankings and a season-adjusted composite power score
- weekly matchup recap (optional OpenAI API key)
- projected standings and Monte Carlo playoff probabilities
- a projection-independent luck index

The configured league is **SYPIP** (`1389341850288009216`). It is public and requires no Sleeper credentials.

## Local setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/python -m sleeper_rankings.cli --skip-ai
```

The generated site is written to `dist/`. During the preseason, pass the previous league and a completed week to validate historical data:

```bash
.venv/bin/python -m sleeper_rankings.cli --league-id 1255668983974072320 --week 10 --skip-ai
```

## Deployment

Create one Netlify project per league and connect it to that league's repository. Netlify publishes `dist/`. The weekly GitHub workflow is scheduled for Tuesday morning during the NFL season and can also be run manually.

The checked-in `netlify.toml` installs the project and its dependencies before generating the site; no manual dependency settings are required in Netlify.

Add `OPENAI_API_KEY` as a GitHub Actions secret to enable the recap. Add `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` repository secrets to let the scheduled workflow deploy directly to that league's Netlify project. No Sleeper secret is required. The site and generation run in hosted services; no home server or inbound Pi access is involved.

This repository deploys only SYPIP. Future leagues should use separate website repositories that depend on the same shared report package.

## Sleeper differences

Sleeper's documented API does not provide player projections. The recap uses actual player results, and the luck index uses opponent draw (65%), performance against the team's own scoring history (25%), and close-game margin (10%). It does not claim projection-based insights.

KeepTradeCut is scraped once per generation. If its markup changes, generation fails instead of silently publishing zero roster values.
