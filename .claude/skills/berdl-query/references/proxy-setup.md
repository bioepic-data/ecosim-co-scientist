# BERDL Proxy Setup (Local)

Use this when querying BERDL off-cluster.

## Typical Ports

- SOCKS tunnel A: `1337`
- SOCKS tunnel B: `1338`
- HTTP bridge (pproxy): `8123`

## Verify Listeners

```bash
lsof -i :1337 -i :1338 -i :8123 | grep LISTEN
```

If ports are missing, restart your tunnel/proxy process.

## Notes

- Keep tunnels active during long-running queries.
- If authentication/connect timeouts occur, check tunnels first.
