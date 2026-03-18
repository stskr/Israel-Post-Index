# Israel Post Branch Index

Auto-updated daily via GitHub Actions.

## How it works

1. GitHub Actions runs every day at 06:00 UTC
2. Downloads the full branches JSON from Israel Post
3. Builds a lean city-keyed index (strips ~70% of unused fields)
4. Commits `docs/city_index.json` back to this repo
5. GitHub Pages serves it publicly

## Your public URL (after setup)

```
https://<your-username>.github.io/<repo-name>/city_index.json
```

## Manual trigger

Go to **Actions → Update Israel Post Branch Index → Run workflow**
