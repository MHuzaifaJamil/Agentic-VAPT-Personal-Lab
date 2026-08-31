#!/bin/bash
# =============================================================================
# Arsenal Bootstrap — idempotent, no-root installer for the external tool
# arsenal (tools/external_arsenal.sh).
#
# WHY THIS EXISTS: tool installs under $HOME (go/bin, .local/bin, ~/tools/)
# do not survive a container/sandbox reset — only the git repo does. Run this
# once at the start of any session where you need the full arsenal. Re-runs
# are fast: every tool is skipped if already on $PATH.
#
# Usage:
#   bash tools/bootstrap_arsenal.sh
#
# Covers everything proven to install cleanly without root on a Debian/Kali
# base with go, pipx, cargo/rustup, gcc/make, and git available. Installs
# rustup itself (user-level, no root) if no Rust toolchain is present, since
# x8 and noseyparker need it. Deliberately excludes only the tools with no
# legitimate fix:
#   - freebuff, kimchi   (unrelated AI-assistant installers, unvetted domains)
#   - gqlmap             (upstream repo deleted, no legitimate replacement)
#
# aquatone has no go.mod (pre-Go-modules project, last commit 2019) and fails
# a plain `go install` because it re-resolves its xurls dependency to a newer
# version with a breaking API change. Fixed below by cloning it, generating a
# go.mod, and pinning mvdan.cc/xurls/v2@v2.0.0 — the exact version its Gopkg.toml
# originally specified, where the API still matches the code.
#
# bbot, mobsf install cleanly via pipx and are kept — but note bbot's first
# real scan needs 'libssl-dev' (apt, root) to finish its one-time core-deps
# setup, so it will not actually run here until you install that yourself.
# =============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/go/bin:$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
export GOBIN="$HOME/go/bin"
mkdir -p "$GOBIN" "$HOME/.local/bin" "$HOME/tools"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[+]${NC} $1"; }
skip() { echo -e "\033[0;36m[=]${NC} $1 (already present)"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[-]${NC} $1"; }

_have() { command -v "$1" >/dev/null 2>&1; }

go_install() {  # $1=binary name, $2=module path
  if _have "$1"; then skip "$1"; return; fi
  echo "  go install $2 ..."
  if GOBIN="$GOBIN" go install "$2" 2>/tmp/bootstrap_err.log; then
    ok "$1"
  else
    err "$1 — $(tail -1 /tmp/bootstrap_err.log)"
  fi
}

pipx_install() {  # $1=binary name, $2=pypi package name
  if _have "$1"; then skip "$1"; return; fi
  echo "  pipx install $2 ..."
  if pipx install "$2" >/tmp/bootstrap_err.log 2>&1; then
    ok "$1"
  else
    err "$1 — $(tail -1 /tmp/bootstrap_err.log)"
  fi
}

# clone_shim NAME REPO_URL SHIM_TARGET_RELATIVE_TO_CLONE [pip_requirements: yes|no]
clone_shim() {
  local name="$1" url="$2" target="$3" needs_reqs="${4:-no}"
  if _have "$name"; then skip "$name"; return; fi
  local dest="$HOME/tools/$name"
  if [ ! -d "$dest" ]; then
    echo "  git clone $url ..."
    git clone --depth 1 -q "$url" "$dest" 2>/tmp/bootstrap_err.log || { err "$name clone — $(tail -1 /tmp/bootstrap_err.log)"; return; }
  fi
  if [ "$needs_reqs" = "yes" ] && [ -f "$dest/requirements.txt" ]; then
    pip install --user --break-system-packages -q -r "$dest/requirements.txt" 2>/dev/null || true
  fi
  cat > "$HOME/.local/bin/$name" <<EOF
#!/bin/bash
exec python3 "$dest/$target" "\$@"
EOF
  chmod +x "$HOME/.local/bin/$name"
  ok "$name"
}

echo "=============================================="
echo "  Arsenal Bootstrap — restoring tool install"
echo "=============================================="
echo

echo "--- Go tools ---"
go_install assetfinder     github.com/tomnomnom/assetfinder@latest
go_install bbscope         github.com/sw33tLie/bbscope@latest
go_install byp4xx          github.com/lobuhi/byp4xx@latest
go_install unwaf           github.com/mmarting/unwaf@latest
go_install gf              github.com/tomnomnom/gf@latest
go_install qsreplace       github.com/tomnomnom/qsreplace@latest
go_install anew            github.com/tomnomnom/anew@latest
go_install interactsh-client github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest
# aquatone: needs a manual go.mod + pinned xurls dependency (see header comment).
if _have aquatone; then
  skip "aquatone"
else
  echo "  building aquatone (clone + pin mvdan.cc/xurls/v2@v2.0.0)..."
  AQ_SRC="$HOME/tools/aquatone-src"
  if [ ! -d "$AQ_SRC" ]; then
    git clone --depth 1 -q https://github.com/michenriksen/aquatone "$AQ_SRC" 2>/tmp/bootstrap_err.log \
      || { err "aquatone clone — $(tail -1 /tmp/bootstrap_err.log)"; }
  fi
  if [ -d "$AQ_SRC" ]; then
    (
      cd "$AQ_SRC" \
        && sed -i 's|github.com/mvdan/xurls|mvdan.cc/xurls/v2|' parsers/regex.go \
        && [ -f go.mod ] || go mod init github.com/michenriksen/aquatone >/dev/null 2>&1
      cd "$AQ_SRC" \
        && go get mvdan.cc/xurls/v2@v2.0.0 >/dev/null 2>&1 \
        && go mod tidy >/dev/null 2>&1 \
        && go build -o aquatone . 2>/tmp/bootstrap_err.log
    )
    if [ -x "$AQ_SRC/aquatone" ]; then
      cp "$AQ_SRC/aquatone" "$GOBIN/aquatone"
      ok "aquatone"
    else
      err "aquatone build — $(tail -1 /tmp/bootstrap_err.log)"
    fi
  fi
fi
go_install smap            github.com/s0md3v/smap/cmd/smap@latest
go_install gospider        github.com/jaeles-project/gospider@latest
go_install hakrawler       github.com/hakluke/hakrawler@latest
go_install waybackurls     github.com/tomnomnom/waybackurls@latest
go_install puredns         github.com/d3mondev/puredns/v2@latest
go_install shuffledns      github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest
go_install kerbrute        github.com/ropnop/kerbrute@latest
go_install shhgit          github.com/eth0izzle/shhgit@latest
go_install git-hound       github.com/tillson/git-hound@latest
go_install s3scanner       github.com/sa7mon/s3scanner@latest
go_install subjack         github.com/haccer/subjack@latest
go_install dnsx            github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go_install naabu           github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go_install cariddi         github.com/edoardottt/cariddi/cmd/cariddi@latest
# feroxbuster is Rust/cargo, not go-installable — only reached if truly missing,
# in which case there's nothing this script can do without cargo/rustup.
if ! _have feroxbuster; then warn "feroxbuster missing — needs cargo/rustup, not covered by this script"; else skip "feroxbuster"; fi
go_install gobuster        github.com/OJ/gobuster/v3@latest
go_install ffuf            github.com/ffuf/ffuf/v2@latest
go_install katana          github.com/projectdiscovery/katana/cmd/katana@latest
go_install gau             github.com/lc/gau/v2/cmd/gau@latest
go_install dalfox          github.com/hahwul/dalfox/v2@latest
go_install nuclei          github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go_install httpx           github.com/projectdiscovery/httpx/cmd/httpx@latest
go_install subfinder       github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go_install gitleaks        github.com/gitleaks/gitleaks/v8@latest
go_install trufflehog      github.com/trufflesecurity/trufflehog@latest

echo
echo "--- Python CLI tools (pipx) ---"
pipx_install bbot          bbot
pipx_install ghauri        git+https://github.com/r0oth3x49/ghauri.git
pipx_install semgrep       semgrep
pipx_install mobsf         mobsf
pipx_install arjun         arjun
pipx_install scoutsuite    scoutsuite
pipx_install waymore       waymore
pipx_install trevorspray   trevorspray
pipx_install maigret       maigret
pipx_install pywhat        pywhat
pipx_install objection     objection
pipx_install cewler        cewler
pipx_install dnsrecon      dnsrecon
pipx_install theHarvester  theHarvester

echo
echo "--- Python pip (system libs, no console-script conflict risk) ---"
if ! python3 -c "import impacket" >/dev/null 2>&1; then
  pip install --user --break-system-packages -q impacket 2>/tmp/bootstrap_err.log \
    && ok "impacket" || err "impacket — $(tail -1 /tmp/bootstrap_err.log)"
else
  skip "impacket"
fi

echo
echo "--- Git-clone + shim (script-only repos) ---"
clone_shim cupp        https://github.com/Mebus/cupp                  cupp.py
clone_shim log4j-scan  https://github.com/fullhunt/log4j-scan         log4j-scan.py
clone_shim xsstrike    https://github.com/s0md3v/XSStrike             xsstrike.py yes
clone_shim linkfinder  https://github.com/GerbenJavado/LinkFinder     linkfinder.py yes
clone_shim graphw00f   https://github.com/dolevf/graphw00f            main.py yes
clone_shim graphql-cop https://github.com/dolevf/graphql-cop          graphql-cop.py yes
clone_shim cloudfail   https://github.com/m0rtem/CloudFail            cloudfail.py yes
clone_shim whatwaf     https://github.com/Ekultek/WhatWaf             whatwaf yes
clone_shim apkleaks    https://github.com/dwisiswant0/apkleaks        apkleaks.py yes
clone_shim fuxploider  https://github.com/almandin/fuxploider         fuxploider.py yes
clone_shim knockpy     https://github.com/guelfoweb/knockpy           knockpy.py yes
clone_shim dnsreaper   https://github.com/punk-security/dnsReaper     main.py yes
clone_shim cloud_enum  https://github.com/initstring/cloud_enum       cloud_enum.py yes
clone_shim sublert     https://github.com/yassineaboukir/sublert      sublert.py yes
clone_shim jwt_tool    https://github.com/ticarpi/jwt_tool             jwt_tool.py yes

echo
echo "--- knockpy: PyPI has an unrelated package under this name (a stats"
echo "    'knockoffs' library) — do NOT 'pipx install knockpy'. The clone_shim"
echo "    call above installs the real github.com/guelfoweb/knockpy instead."
echo

echo "--- clairvoyance (package needs 'python -m' invocation, not a direct script) ---"
if _have clairvoyance; then
  skip "clairvoyance"
else
  if [ ! -d "$HOME/tools/clairvoyance" ]; then
    git clone --depth 1 -q https://github.com/nikitastupin/clairvoyance "$HOME/tools/clairvoyance" 2>/tmp/bootstrap_err.log \
      || { err "clairvoyance clone — $(tail -1 /tmp/bootstrap_err.log)"; }
  fi
  if [ -d "$HOME/tools/clairvoyance/clairvoyance" ]; then
    pip install --user --break-system-packages -q graphql-core aiohttp click 2>/dev/null || true
    cat > "$HOME/.local/bin/clairvoyance" <<EOF
#!/bin/bash
cd "$HOME/tools/clairvoyance" && exec python3 -m clairvoyance "\$@"
EOF
    chmod +x "$HOME/.local/bin/clairvoyance"
    ok "clairvoyance"
  fi
fi

echo "--- massdns (build from source) ---"
if _have massdns; then
  skip "massdns"
else
  if [ ! -d "$HOME/tools/massdns" ]; then
    git clone --depth 1 -q https://github.com/blechschmidt/massdns "$HOME/tools/massdns" 2>/dev/null
  fi
  ( cd "$HOME/tools/massdns" && make -s ) 2>/tmp/bootstrap_err.log \
    && cp "$HOME/tools/massdns/bin/massdns" "$HOME/.local/bin/massdns" \
    && ok "massdns" \
    || err "massdns — $(tail -1 /tmp/bootstrap_err.log)"
fi

echo
echo "--- Rust tools (x8, noseyparker) ---"
if [ -f "$HOME/.cargo/env" ]; then
  # shellcheck source=/dev/null
  . "$HOME/.cargo/env"
fi

if ! _have cargo; then
  echo "  no rust toolchain found — installing rustup (user-level, no root)..."
  if curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/rustup-init.sh 2>/tmp/bootstrap_err.log \
     && bash /tmp/rustup-init.sh -y --default-toolchain stable --profile minimal >/tmp/bootstrap_err.log 2>&1; then
    . "$HOME/.cargo/env"
    ok "rustup + stable toolchain"
  else
    err "rustup install — $(tail -1 /tmp/bootstrap_err.log)"
  fi
  rm -f /tmp/rustup-init.sh
fi

if _have cargo; then
  if _have x8; then
    skip "x8"
  else
    echo "  cargo install x8 ..."
    if cargo install x8 >/tmp/bootstrap_err.log 2>&1; then
      ln -sf "$HOME/.cargo/bin/x8" "$HOME/.local/bin/x8"
      ok "x8"
    else
      err "x8 — $(tail -1 /tmp/bootstrap_err.log)"
    fi
  fi

  if _have noseyparker; then
    skip "noseyparker"
  else
    echo "  fetching noseyparker prebuilt release (not on crates.io)..."
    NP_URL=$(curl -s https://api.github.com/repos/praetorian-inc/noseyparker/releases/latest \
      | grep -o 'https://[^"]*x86_64-unknown-linux-gnu\.tar\.gz' | head -1)
    if [ -n "$NP_URL" ] && curl -sL "$NP_URL" -o /tmp/noseyparker.tar.gz; then
      mkdir -p "$HOME/tools/noseyparker"
      tar -xzf /tmp/noseyparker.tar.gz -C "$HOME/tools/noseyparker"
      rm -f /tmp/noseyparker.tar.gz
      if [ -f "$HOME/tools/noseyparker/bin/noseyparker" ]; then
        chmod +x "$HOME/tools/noseyparker/bin/noseyparker"
        ln -sf "$HOME/tools/noseyparker/bin/noseyparker" "$HOME/.local/bin/noseyparker"
        ok "noseyparker"
      else
        err "noseyparker — extracted archive missing bin/noseyparker"
      fi
    else
      err "noseyparker — release download failed"
    fi
  fi
else
  warn "x8/noseyparker skipped — no cargo available and rustup install failed"
fi

echo
echo "--- jadx (release zip, needs java) ---"
if _have jadx; then
  skip "jadx"
elif ! _have java; then
  warn "jadx skipped — no java on PATH (needs a JRE, can't install without root)"
else
  if [ ! -d "$HOME/tools/jadx" ]; then
    JADX_URL=$(curl -s https://api.github.com/repos/skylot/jadx/releases/latest | grep -o 'https://[^"]*\.zip' | head -1)
    if [ -n "$JADX_URL" ]; then
      curl -sL "$JADX_URL" -o /tmp/jadx.zip && unzip -q /tmp/jadx.zip -d "$HOME/tools/jadx" && rm -f /tmp/jadx.zip
    fi
  fi
  if [ -x "$HOME/tools/jadx/bin/jadx" ]; then
    ln -sf "$HOME/tools/jadx/bin/jadx" "$HOME/.local/bin/jadx"
    ok "jadx"
  else
    err "jadx — download or extract failed"
  fi
fi

echo
echo "--- General VAPT extras (wordlists / exploit-db / TLS scanner) ---"
if [ ! -d "$HOME/tools/SecLists" ]; then
  echo "  SecLists is ~2.5GB — cloning in the background, won't block this script."
  echo "  Check progress later with: du -sh ~/tools/SecLists"
  nohup git clone --depth 1 https://github.com/danielmiessler/SecLists \
    "$HOME/tools/SecLists" > /tmp/seclists_bootstrap_clone.log 2>&1 &
  disown
  ok "SecLists clone started in background (PID $!)"
else
  skip "SecLists"
fi

if _have searchsploit; then
  skip "searchsploit"
else
  if [ ! -d "$HOME/tools/exploitdb" ]; then
    git clone --depth 1 -q https://gitlab.com/exploit-database/exploitdb "$HOME/tools/exploitdb" 2>/dev/null
  fi
  if [ -f "$HOME/tools/exploitdb/searchsploit" ]; then
    ln -sf "$HOME/tools/exploitdb/searchsploit" "$HOME/.local/bin/searchsploit"
    ok "searchsploit"
  fi
fi

if _have testssl.sh || _have testssl; then
  skip "testssl.sh"
else
  if [ ! -d "$HOME/tools/testssl.sh" ]; then
    git clone --depth 1 -q https://github.com/testssl/testssl.sh "$HOME/tools/testssl.sh" 2>/dev/null
  fi
  if [ -f "$HOME/tools/testssl.sh/testssl.sh" ]; then
    ln -sf "$HOME/tools/testssl.sh/testssl.sh" "$HOME/.local/bin/testssl.sh"
    ln -sf "$HOME/tools/testssl.sh/testssl.sh" "$HOME/.local/bin/testssl"
    ok "testssl.sh"
  fi
fi

echo
echo "=============================================="
echo "  Bootstrap complete — final status:"
echo "=============================================="
bash "$REPO_ROOT/tools/external_arsenal.sh" | tail -5

echo
echo "Known non-functional-without-root caveat:"
echo "  bbot installs and shows as present, but its first real scan needs"
echo "  'libssl-dev' (dev headers) installed via apt/sudo to finish its"
echo "  one-time core-dependency setup. Run 'sudo apt install libssl-dev'"
echo "  once yourself if you want bbot to actually run scans."
