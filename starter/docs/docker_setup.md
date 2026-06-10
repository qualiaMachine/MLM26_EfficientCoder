# Docker setup

Terminal-Bench runs every task in a fresh Docker container. That's the sandbox (the agent can't touch your real filesystem) and the reproducibility guarantee (everyone's agent sees the identical environment). **Harbor will not work without Docker running**, so this is step zero. We do a live setup walkthrough at the Week 1 kickoff — if you're stuck, bring your laptop.

Verify any install with:

```bash
docker --version          # prints a version
docker run hello-world    # prints "Hello from Docker!"
```

## macOS

1. Install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/). Pick **Apple Silicon** or **Intel** to match your machine ( → About This Mac).
2. Open the `.dmg`, drag Docker to Applications, launch it.
3. Docker Desktop must be **running** (whale icon in the menu bar) whenever you use Harbor.

Homebrew alternative: `brew install --cask docker`, then launch Docker from Applications once.

## Linux (Ubuntu/Debian)

Docker Engine only — no Desktop app needed:

```bash
curl -fsSL https://get.docker.com | sh

# Run docker without sudo
sudo usermod -aG docker $USER
newgrp docker             # or log out and back in

docker run hello-world
```

Other distros: see the [Docker Engine install docs](https://docs.docker.com/engine/install/).

## Windows

Docker on Windows requires **WSL2**. Do all challenge work **inside WSL2** (Ubuntu), not PowerShell — the toolchain (uv, Harbor, shell scripts) assumes a Unix shell.

1. PowerShell **as Administrator**:
   ```powershell
   wsl --install
   ```
   Reboot when prompted (installs Ubuntu by default).
2. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with **"Use WSL 2 based engine"** checked.
3. Docker Desktop → Settings → Resources → **WSL Integration** → enable your Ubuntu distro.
4. Open Ubuntu (Start menu) and verify:
   ```bash
   docker run hello-world
   ```

If `docker` isn't found inside Ubuntu, step 3 is the culprit.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Cannot connect to the Docker daemon` | Docker isn't running. Start Docker Desktop, or `sudo systemctl start docker` on Linux. |
| `permission denied ... docker.sock` (Linux) | You skipped `sudo usermod -aG docker $USER` + re-login. |
| Builds fail with "no space left on device" | Give Docker ≥30 GB. Reclaim space with `docker system prune` (careful: deletes stopped containers and unused images). |
| Everything is slow on Windows | Keep your repo inside the WSL2 filesystem (`~/...`), not `/mnt/c/...`. |
| Corporate laptop / no admin rights | Talk to us at kickoff — UW participants can use RunAI, and Harbor supports cloud sandboxes (Daytona) as a fallback. |
