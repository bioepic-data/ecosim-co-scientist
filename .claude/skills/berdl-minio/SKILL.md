---
name: berdl-minio
description: Retrieve and use BERDL MinIO credentials and transfer result artifacts between BERDL object storage and the local machine. Use when exported query results need to be listed, downloaded, shared, or when only KBASE_AUTH_TOKEN is available and MinIO keys must be acquired.
---

# BERDL MinIO Skill

## Compatibility Modes

- Full BERDL mode: derive credentials from KBase context and helper scripts.
- Limited mode: use direct MinIO credentials and `mc` commands without helper scripts.

## Overview

Use this skill to work with BERDL MinIO from local tools.
It handles credential sourcing, MinIO client setup, and object transfer operations.

## Step 0: Environment Check

Run before anything else:

```bash
if [ -f scripts/berdl_env.py ]; then python3 scripts/berdl_env.py --check; else echo "berdl_env.py not found; validate network/proxy manually"; fi
```

If `--check` reports off-cluster and not ready, follow the printed next steps. The MinIO endpoint (`minio.berdl.kbase.us`) is only reachable through the proxy chain off-cluster, so this check is mandatory.

## Preconditions

1. Either `KBASE_AUTH_TOKEN` is available OR direct MinIO credentials are already available.
2. **`mc` (MinIO client) installed.** Check with `command -v mc`. Install with:
   - macOS: `brew install minio/stable/mc` or download directly:
     `curl -sSL https://dl.min.io/client/mc/release/darwin-arm64/mc -o /usr/local/bin/mc && chmod +x /usr/local/bin/mc`
   - Linux: `curl -sSL https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && chmod +x /usr/local/bin/mc`
3. **Proxy running** (when off-cluster): MinIO is not directly reachable from external networks. See the berdl-query skill's `references/proxy-setup.md` for setup instructions.

## Credential Strategy

Use credentials in this order:
1. Existing `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY` in environment or `.env`.
2. Derive credentials from BERDL remote environment using `berdl-remote` (authenticated by `KBASE_AUTH_TOKEN`).

## Workflow

1. Resolve credentials:
   - If helper exists: `python3 scripts/get_minio_creds.py --shell`
   - If helper exists and remote bootstrap is needed: `python3 scripts/get_minio_creds.py --bootstrap-remote --shell`
   - To load creds from helper: `eval "$(python3 scripts/get_minio_creds.py --shell)"`
   - Without helper, export existing credentials manually.
2. Configure `mc` alias:
   - If helper exists: `bash scripts/configure_mc.sh --berdl-proxy`
   - Without helper, run `mc alias set` directly.
3. Move files with `mc`.
   **Important:** Every `mc` command needs `https_proxy` set when off-cluster, not just the alias setup. Either export it in your shell or prefix each command:
   ```bash
   export https_proxy=http://127.0.0.1:8123
   export no_proxy=localhost,127.0.0.1
   mc ls berdl-minio/cdm-lake/users-general-warehouse/<user>/exports/
   mc cp --recursive berdl-minio/cdm-lake/.../run_20260217 ./exports/run_20260217
   mc cp --recursive ./local_data berdl-minio/cdm-lake/.../uploads/local_data
   ```

## Scripts

If helper scripts are missing in this repository, use direct `mc` and environment-variable workflows.

- `scripts/berdl_env.py`: environment check entrypoint (Step 0).
- `scripts/get_minio_creds.py`: resolve MinIO keys locally or via BERDL remote context.
- `scripts/configure_mc.sh`: configure MinIO CLI alias and test connectivity.
  - Supports `--berdl-proxy` to route through `http://127.0.0.1:8123` (required when off-cluster).

## References

- `references/minio-endpoints.md`: environment endpoints and path patterns.
- See berdl-query `references/proxy-setup.md` for proxy chain setup.

## Safety Rules

1. Never print full secrets in final user-facing summaries unless explicitly requested.
2. Do not commit credentials into repository files.
3. Prefer short-lived retrieval and local shell export for active sessions.
