# PAD Multi-Omics Atlas — public deployment

Existing Dash application, packaged for SciLifeLab Serve. Python 3.11, Gunicorn, port 8000, linux/amd64. One worker avoids duplicating cached data; four threads handle requests. No authentication is added to this public version.

## Prepare

Extract these deployment-only files into your existing `pad_atlas_public` directory (the directory containing app.py). No application source or data is replaced. Merge the supplied .gitignore with any existing rules and review requirements.txt before replacing an existing dependency file. The Dockerfile expects your existing 17 reviewed Parquet files. The wsgi.py adapter exposes app.server without editing app.py. Do not copy private backups or raw expression matrices. Keep absolute abundance summaries only if approved: the boxplot whiskers can be observed sample values. Review clinical small cells, correlation sample sizes, all data values and release permissions. The automated check is not a privacy certification.

From the directory containing `app.py`:

```bash
conda activate pad_atlas
python scripts/check_data.py Parquet
```

If needed, install packages: `python -m pip install -r requirements.txt`.
For native development, run from the parent directory: `python -m pad_atlas_public.app` (port 8050).

## Docker local test

Start Docker Desktop. From `pad_atlas_public`:

```bash
docker build --platform linux/amd64 -t pad-atlas:local .
docker run --rm -p 127.0.0.1:8000:8000 pad-atlas:local
```

Open http://localhost:8000. In a second terminal run `curl -f http://localhost:8000/_dash-layout` and `curl -f http://localhost:8000/_dash-dependencies`. Test every sidebar page, both plot choices, cohort selection and downloads. Stop with Ctrl+C. On Apple Silicon the amd64 container runs under emulation.

## GitHub and GHCR

Create a new empty GitHub repository for the approved public release. Serve requires code and data to be publicly available; keep private research files in a different repository. Review existing history before making any existing repo public. Remove old competing publishing workflows. From this directory, for a NEW repository:

```bash
git init
git add .
git status --short
git diff --cached --stat
git commit -m "Prepare PAD Atlas for Serve"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

For an existing repository, omit init/remote add and use its established remote. Review `git ls-files` for private files, including previously tracked files (gitignore does not untrack them). Do not publish until reviewed. GitHub Actions builds, starts and smoke-tests the container before pushing the tested image to GHCR. Check Actions for errors. In your profile Packages, open the package and Package settings, change visibility to Public if necessary. No personal registry token is needed for this workflow.

Use the exact lower-case image name and SHA tag shown in Actions/Packages, e.g. `ghcr.io/YOUR_USERNAME/YOUR_REPOSITORY:sha-abcdef0`. Test anonymous pull from a logged-out Docker client:

```bash
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPOSITORY:sha-abcdef0
```

Replace examples with real values. In SciLifeLab Serve, sign in, create or open a project, create a Dash app, enter the public image reference and port 8000 if requested, then submit. Check the running app and logs. For every update, commit and push; use the new unique SHA or version tag in Serve. `latest` is also published on main but unique tags are preferable for reproducibility.

References: https://github.com/ScilifelabDataCentre/serve-app-template and https://serve.scilifelab.se/docs/application-hosting/dash/.

## Validation limits

These files are adapted from the previous deployment bundle. Your latest local source and actual Parquet data were not tested. The dependency list is based on the earlier source. If your local app imports additional packages or uses additional assets, update requirements.txt or the Docker allowlist accordingly. CI smoke tests do not exercise all callbacks. Do not publish credentials or private data in the image or repository.
