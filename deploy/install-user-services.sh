#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

install -d -m 0755 "$unit_dir"
install -m 0644 "$project_root/deploy/systemd/canvas-lab.target" "$unit_dir/canvas-lab.target"
install -m 0644 "$project_root/deploy/systemd/canvas-lab-web.service" "$unit_dir/canvas-lab-web.service"
install -m 0644 "$project_root/deploy/systemd/canvas-lab-gateway.service" "$unit_dir/canvas-lab-gateway.service"
install -m 0644 "$project_root/deploy/systemd/canvas-lab-agent.service" "$unit_dir/canvas-lab-agent.service"
systemctl --user daemon-reload

printf 'Installed Canvas Lab user services. Start from Hive0 (无线画布) or run:\n'
printf '  systemctl --user start canvas-lab.target\n'
