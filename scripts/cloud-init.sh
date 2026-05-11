#!/bin/bash
set -e
exec > /var/log/runner-setup.log 2>&1

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq curl jq git python3 python3-pip wget

# Cloudflare Tunnel (нет публичного SSH)
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
  | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
  > /etc/apt/sources.list.d/cloudflared.list
apt-get update -qq && apt-get install -y -qq cloudflared
cloudflared service install ${CF_TUNNEL_TOKEN}
systemctl start cloudflared
echo "✓ Cloudflare tunnel started"

# GitHub Actions Runner
RUNNER_VERSION="2.333.0"
echo "Runner version: ${RUNNER_VERSION}"

mkdir -p /opt/actions-runner && cd /opt/actions-runner
wget -q -O runner.tar.gz \
  "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

tar xzf runner.tar.gz
rm runner.tar.gz

./config.sh \
  --url "https://github.com/${GITHUB_REPO}" \
  --token "${REG_TOKEN}" \
  --name "${SERVER_NAME}" \
  --labels "ephemeral,hetzner,${SERVER_NAME}" \
  --ephemeral \
  --unattended \
  --disableupdate

echo "✓ Runner registered"
RUNNER_ALLOW_RUNASROOT=1 ./run.sh --once || true
echo "✓ Runner done"