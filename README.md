# SYPIP

## Review-first weekly workflow

The local website directory is `SYPIP`; the GitHub repository URL remains unchanged. The engine lives in `fantasy-football-reports`. The dependency follows its `master` branch, so each build installs the latest engine automatically. Engine regressions can fail a draft build; historical reports are saved output and are not recalculated.

Tuesday's **Build report draft** workflow generates a new entry under `content/reports/<league-id>/<season>/week-NN/`, saves rankings and KTC values alongside its HTML, uploads an artifact, deploys a Netlify draft URL, and opens a review pull request. No automated report is deployed with `--prod`.

Review the draft URL in the Actions log, then **merge the report PR to publish**. Netlify's production branch must remain `main`. Do not promote a Netlify draft directly: that would skip saving its history on main. Review/merge earlier weeks before generating the next one to include their snapshots. Enable **Allow GitHub Actions to create and approve pull requests** in repository Actions settings if PR creation is blocked. The workflow never approves or merges its own PRs.

Configure `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` as Actions secrets for draft deployment. Without them, the artifact and review PR remain available but Netlify upload is skipped. Draft URLs are previews, not access-controlled private pages.

Netlify runs `python -m sleeper_rankings.cli --archive-only`: it publishes saved entries only and never generates an unreviewed report. An empty archive shows the preseason teaser. Each week has its own URL and the homepage lists all archived weeks. Existing weeks cannot be regenerated in place accidentally.

Weekly movement compares the current ranking with the previous week's stored ranking by roster ID (old rank minus new rank). Missing history is labeled explicitly; current KTC values are never used to reconstruct last week's rank. AI recaps remain disabled in `leagues/sypip.json`.

For local generation, run the normal command below. Use `--archive-only` to render saved reports without API calls. Generated entries are not published merely by running locally; review the content changes before merging them into main.

For a correction, manually run the workflow with an explicit week and the overwrite checkbox enabled, or use `python -m sleeper_rankings.cli --week N --overwrite` locally. The corrected entry still needs review and merging. Scheduled runs cannot overwrite entries. Corrections use newly fetched league data and current KTC values, not a historical replay. Later weeks' saved movement is not automatically revised when an earlier week is corrected.

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

An AI key alone does not enable recaps: SYPIP also requires an explicit change to `ai_recap` in its configuration. No Sleeper secret is required. The site and generation run in hosted services; no home server or inbound Pi access is involved.

This repository deploys only SYPIP. Future leagues should use separate website repositories that depend on the same shared report package.

## Sleeper differences

Sleeper's documented API does not provide player projections. The recap uses actual player results, and the luck index uses opponent draw (65%), performance against the team's own scoring history (25%), and close-game margin (10%). It does not claim projection-based insights.

KeepTradeCut is scraped once per generation. If its markup changes, generation fails instead of silently publishing zero roster values.
