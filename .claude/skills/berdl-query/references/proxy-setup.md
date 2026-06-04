# BERDL Proxy Setup (Local)

Use this when querying BERDL **off-cluster** (from your local machine). BERDL
services (`hub.berdl.kbase.us`, the Spark Connect endpoint, and
`minio.berdl.kbase.us`) are not directly reachable from external networks. Two
layers bridge the gap:

1. **SSH SOCKS tunnels** — encrypted reach into the BERDL network. Require the
   user's own SSH credentials, so **ask the user to start these**; Claude cannot.
2. **pproxy HTTP bridge** — converts the SOCKS proxy into a plain `https_proxy`
   that `mc`, `requests`, and Spark Connect can use. Claude can start this from
   `.venv-berdl`.

## Typical Ports

- SOCKS tunnel A: `1337`
- SOCKS tunnel B: `1338`
- HTTP bridge (pproxy): `8123`

## Step 1: SSH SOCKS Tunnels (user runs these)

Open one SOCKS proxy per required upstream. Replace `<bastion>` with the BERDL
SSH jump host the user was given.

```bash
# Tunnel A
ssh -N -D 1337 <user>@<bastion>
# Tunnel B (separate terminal, if a second upstream is required)
ssh -N -D 1338 <user>@<bastion>
```

`-N` opens the tunnel without a remote shell; `-D` starts a local SOCKS proxy on
the given port. Leave both running for the whole session. Add `-f` to background
them, or run each in its own terminal/`tmux` pane so drops are visible.

## Step 2: pproxy HTTP Bridge (Claude can run this)

`mc` and most HTTP clients speak `https_proxy=http://...`, not SOCKS, so bridge
the SOCKS tunnel to an HTTP proxy on `8123`:

```bash
source .venv-berdl/bin/activate   # pproxy is installed here by bootstrap_client.sh
pproxy -l http://127.0.0.1:8123 -r socks5://127.0.0.1:1337 &
```

If `pproxy` is missing, install it into the venv: `uv pip install pproxy` (or
`pip install pproxy`).

## Step 3: Point Clients at the Bridge

```bash
export https_proxy=http://127.0.0.1:8123
export no_proxy=localhost,127.0.0.1
```

The helper scripts (`run_sql.py`, `export_sql.py`, `configure_mc.sh`) accept
`--berdl-proxy`, which sets the same routing internally.

## Verify Listeners

```bash
lsof -i :1337 -i :1338 -i :8123 | grep LISTEN
```

All required ports should appear as `LISTEN`. If any are missing, restart the
corresponding tunnel or the pproxy bridge.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Connect call failed` / `authentication service timed out` | SSH tunnel dropped | Re-run the `ssh -N -D` command for the dead port |
| `mc` hangs or returns connection refused | `https_proxy` not exported, or pproxy not running | Export `https_proxy=http://127.0.0.1:8123` and confirm pproxy is listening on `8123` |
| Port already in use when starting pproxy | A previous bridge is still running | Reuse it, or kill the old process (`lsof -i :8123`) before restarting |
| Works briefly then fails on long queries | Tunnel idled out or laptop slept | Keep tunnels and a JupyterHub tab active; restart dropped tunnels and re-probe with `SELECT 1` |
| `Permission denied (publickey)` on `ssh` | Wrong SSH key/user for the bastion | Confirm SSH access details with the BERDL admin; this is a user-credential issue, not a proxy bug |

## Notes

- Keep tunnels active during long-running queries.
- If authentication/connect timeouts occur, check tunnels first.
- On-cluster (BERDL JupyterHub) sessions need **no** proxy — use the active
  Spark session directly and do not pass `--berdl-proxy`.
