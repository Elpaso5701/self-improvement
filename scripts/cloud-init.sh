#!/bin/bash
set -e
exec > /var/log/runner-setup.log 2>&1

export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq curl jq git python3 python3-pip wget

# =========================
# Cloudflared
# =========================
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
  | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null

echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
  > /etc/apt/sources.list.d/cloudflared.list

apt-get update -qq
apt-get install -y -qq cloudflared

nohup cloudflared tunnel run --token ${CF_TUNNEL_TOKEN} \
  > /var/log/cloudflared.log 2>&1 &

echo "✓ Cloudflare tunnel started"

# =========================
# GitHub Runner
# =========================
RUNNER_VERSION="2.333.0"
echo "Runner version: ${RUNNER_VERSION}"

mkdir -p /opt/actions-runner
cd /opt/actions-runner

wget -q -O runner.tar.gz \
  "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

tar xzf runner.tar.gz
rm runner.tar.gz

RUNNER_ALLOW_RUNASROOT=1 ./config.sh \
  --url "https://github.com/${GITHUB_REPO}" \
  --token "${REG_TOKEN}" \
  --name "${SERVER_NAME}" \
  --labels "self-hosted,hetzner,ephemeral,${SERVER_NAME}" \
  --ephemeral \
  --unattended

echo "Waiting for GitHub sync..."
sleep 10

echo "✓ Runner registered"

nohup RUNNER_ALLOW_RUNASROOT=1 ./run.sh \
  > /var/log/gha-runner.log 2>&1 &

echo "✓ Runner started"