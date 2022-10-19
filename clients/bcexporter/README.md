# BlockchainNodeExporter

### Supported Blockchains

- harmony
- polygon
- xdai
- eth
- bsc
- swimmer
- avax
- dfk
- other EVM chains should work but not tested

### Quickstart

```bash
docker compose up
```

# Configuration

### Add endpoints to export metrics from

Edit chains.json or plug and play with your blockchain #'s and endpoints then run

```bash
docker compose down && docker compose up
```

### Change rate of metric polling

Edit `config.yml` and change `polling_interval_seconds` then run

```bash
docker compose down && docker compose up
```
