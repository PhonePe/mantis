#!/usr/bin/env bash
#
# Platform-aware installer for Mantis' external recon tools.
#
# Reads configs/tools.yml, detects the host platform ({linux|darwin}/{amd64|arm64}),
# and installs each tool using a fallback ladder:
#     prebuilt binary  ->  `go install`  ->  (python tools via pip / source clone)
#
# Usage:
#     install_tools.sh [target] [manifest_path]
#         target         docker | native   (default: native) — selects which tools to install
#         manifest_path  path to tools.yml  (default: <repo>/configs/tools.yml)
#
# Requires: yq (mikefarah v4), curl, unzip, tar, git, python3/pip.

set -euo pipefail

TARGET="${1:-native}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
MANIFEST="${2:-${SCRIPT_DIR}/../configs/tools.yml}"

log()  { echo -e "[+] $*"; }
warn() { echo -e "[!] $*" >&2; }
die()  { echo -e "[x] $*" >&2; exit 1; }

# --- prerequisites ----------------------------------------------------------
command -v yq   >/dev/null 2>&1 || die "yq is required (https://github.com/mikefarah/yq). Install it and re-run."
command -v curl >/dev/null 2>&1 || die "curl is required."
[ -f "$MANIFEST" ] || die "manifest not found: $MANIFEST"

# --- platform detection -----------------------------------------------------
case "$(uname -s)" in
  Linux)  OS=linux  ;;
  Darwin) OS=darwin ;;
  *)      OS=linux  ; warn "unknown OS '$(uname -s)', assuming linux" ;;
esac
case "$(uname -m)" in
  x86_64|amd64)   ARCH=amd64 ;;
  aarch64|arm64)  ARCH=arm64 ;;
  *)              ARCH="$(uname -m)"; warn "unknown arch '$(uname -m)'" ;;
esac
log "Platform: ${OS}/${ARCH} | target: ${TARGET}"

# --- privilege + helpers ----------------------------------------------------
if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo"; else SUDO=""; fi
# Allow callers (e.g. native-setup.sh on Ubuntu) to pin the interpreter, e.g. MANTIS_PIP="python3.9 -m pip".
PIP="${MANTIS_PIP:-python3 -m pip}"

INSTALL_DIR="$(yq '.install_dir // "/usr/bin"' "$MANIFEST")"
$SUDO mkdir -p "$INSTALL_DIR"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Read a manifest field for tool index $1, key $2, with optional default $3.
field() {
  local i="$1" key="$2" def="${3:-}"
  yq ".tools[$i].${key} // \"${def}\"" "$MANIFEST"
}
# Substitute {version}/{os}/{arch} placeholders.
subst() {
  local s="$1"
  s="${s//\{version\}/$VERSION}"; s="${s//\{os\}/$OS_TOK}"; s="${s//\{arch\}/$ARCH_TOK}"
  echo "$s"
}

FAILED=()

install_binary() {
  local i="$1" name="$2"
  OS_TOK="$(yq ".tools[$i].os_tokens.${OS} // \"${OS}\"" "$MANIFEST")"
  ARCH_TOK="$(yq ".tools[$i].arch_tokens.${ARCH} // \"${ARCH}\"" "$MANIFEST")"
  local archive url bin_in sha
  archive="$(field "$i" archive none)"
  url="$(subst "$(field "$i" url)")"
  bin_in="$(subst "$(field "$i" bin_in_archive "$name")")"
  sha="$(field "$i" sha256 "")"

  local ex="$WORK/$name"; rm -rf "$ex"; mkdir -p "$ex"
  local dl="$WORK/${name}.dl"

  if ! curl -fsSL "$url" -o "$dl" 2>/dev/null; then
    warn "$name: no prebuilt asset at $url — trying go install fallback"
    install_go_fallback "$i" "$name" && return 0
    FAILED+=("$name"); return 1
  fi

  # optional checksum verification (skipped when sha is empty)
  if [ -n "$sha" ] && [ "$sha" != "null" ]; then
    local got; got="$(sha256sum "$dl" 2>/dev/null | awk '{print $1}' || shasum -a 256 "$dl" | awk '{print $1}')"
    [ "$got" = "$sha" ] || { warn "$name: sha256 mismatch (want $sha got $got)"; FAILED+=("$name"); return 1; }
  fi

  case "$archive" in
    zip)    unzip -o -q "$dl" -d "$ex" ;;
    tar.gz) tar -xzf "$dl" -C "$ex" ;;
    none)   cp "$dl" "$ex/$(basename "$bin_in")" ;;
    *)      warn "$name: unknown archive type '$archive'"; FAILED+=("$name"); return 1 ;;
  esac

  local found
  found="$(find "$ex" -type f -name "$(basename "$bin_in")" | head -n1)"
  [ -n "$found" ] || { warn "$name: binary '$bin_in' not found in archive"; FAILED+=("$name"); return 1; }

  chmod +x "$found"
  $SUDO mv "$found" "${INSTALL_DIR}/${name}"
  log "installed ${name} -> ${INSTALL_DIR}/${name}"
}

install_go_fallback() {
  local i="$1" name="$2" mod
  mod="$(subst "$(field "$i" go_module "")")"
  [ -n "$mod" ] || return 1
  command -v go >/dev/null 2>&1 || { warn "$name: Go toolchain not available for fallback"; return 1; }
  log "$name: go install $mod"
  GOBIN="$WORK/gobin" go install "$mod" || return 1
  $SUDO mv "$WORK/gobin/$name" "${INSTALL_DIR}/${name}"
  log "installed ${name} (go) -> ${INSTALL_DIR}/${name}"
}

install_pip() {
  local i="$1" name="$2" spec
  spec="$(field "$i" pip_spec "$name")"
  log "$name: pip install $spec"
  $PIP install --no-cache-dir "$spec" || { FAILED+=("$name"); return 1; }
  log "installed ${name} (pip)"
}

install_source() {
  local i="$1" name="$2"
  VERSION="$(field "$i" version "")"
  OS_TOK="$OS"; ARCH_TOK="$ARCH"
  local url archive dest exdir
  url="$(subst "$(field "$i" url)")"
  archive="$(field "$i" archive zip)"
  dest="$(field "$i" dest "${INSTALL_DIR}/${name}")"
  exdir="$(subst "$(field "$i" extracted_dir "$name")")"

  local ex="$WORK/$name"; rm -rf "$ex"; mkdir -p "$ex"
  local dl="$WORK/${name}.dl"
  curl -fsSL "$url" -o "$dl" || { warn "$name: download failed $url"; FAILED+=("$name"); return 1; }
  case "$archive" in
    zip)    unzip -o -q "$dl" -d "$ex" ;;
    tar.gz) tar -xzf "$dl" -C "$ex" ;;
    *)      warn "$name: unsupported source archive '$archive'"; FAILED+=("$name"); return 1 ;;
  esac
  [ -d "$ex/$exdir" ] || { warn "$name: '$exdir' not found after extraction"; FAILED+=("$name"); return 1; }
  $SUDO rm -rf "$dest"
  $SUDO mv "$ex/$exdir" "$dest"
  log "installed ${name} (source) -> ${dest}"
}

# --- main loop --------------------------------------------------------------
COUNT="$(yq '.tools | length' "$MANIFEST")"
for i in $(seq 0 $((COUNT - 1))); do
  name="$(field "$i" name)"
  method="$(field "$i" method binary)"
  targets="$(yq ".tools[$i].targets // [\"docker\",\"native\"] | join(\",\")" "$MANIFEST")"
  case ",${targets}," in
    *",${TARGET},"*) ;;
    *) log "skip ${name} (not in target '${TARGET}')"; continue ;;
  esac

  VERSION="$(field "$i" version "")"
  case "$method" in
    binary) install_binary "$i" "$name" || true ;;
    pip)    install_pip    "$i" "$name" || true ;;
    source) install_source "$i" "$name" || true ;;
    *)      warn "${name}: unknown method '${method}'" ;;
  esac
done

if [ "${#FAILED[@]}" -gt 0 ]; then
  warn "Completed with failures: ${FAILED[*]}"
  exit 1
fi
log "All tools installed successfully into ${INSTALL_DIR}"
