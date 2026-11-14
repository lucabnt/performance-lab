# Source inside the Fedora Toolbox, AFTER the usual ambiente.sh of ANDROID_WHEEL_FEDORA.md:
#   source ambiente.sh
#   FUORIGIRI_NEUTRAL=/build/fuorigiri-<id> source <repo>/scripts/android_neutral_env.sh
# Prepares a neutral build root so wheels, SBOMs and static libraries do not
# record the builder's home. Tools (SDK, NDK, rustup) stay where they are; their
# paths are remapped. The root must be new: previous outputs are never reused.

if [ -z "${FUORIGIRI_NEUTRAL:-}" ]; then
  echo "Impostare FUORIGIRI_NEUTRAL, ad esempio /build/fuorigiri-$(date +%Y%m%d)-01" >&2
  return 1 2>/dev/null || exit 1
fi
case "$FUORIGIRI_NEUTRAL" in
  /build/*) ;;
  *) echo "FUORIGIRI_NEUTRAL deve stare sotto /build" >&2; return 1 2>/dev/null || exit 1 ;;
esac
if [ -e "$FUORIGIRI_NEUTRAL" ]; then
  echo "$FUORIGIRI_NEUTRAL esiste già: scegliere una radice nuova" >&2
  return 1 2>/dev/null || exit 1
fi
if [ -z "${ANDROID_NDK_ROOT:-}" ] || [ -z "${RUSTUP_HOME:-}" ]; then
  echo "Caricare prima ambiente.sh (NDK e rustup separato)" >&2
  return 1 2>/dev/null || exit 1
fi

sudo mkdir -p /build && sudo chown "$(id -u):$(id -g)" /build
mkdir -p "$FUORIGIRI_NEUTRAL"/{downloads,wheelhouse,cargo}

# Fresh cargo registry inside the neutral root; rustup proxies remain on PATH.
export FUORIGIRI_TOOL_CARGO_HOME="$CARGO_HOME"
export CARGO_HOME="$FUORIGIRI_NEUTRAL/cargo"
export PATH="$FUORIGIRI_TOOL_CARGO_HOME/bin:$PATH"

# Remap any remaining tool path under the account home (NDK, rustup sources).
export FUORIGIRI_REMAP_RUST="--remap-path-prefix=$HOME=/home/builder --remap-path-prefix=$FUORIGIRI_NEUTRAL=/build/src"
export FUORIGIRI_REMAP_C="-ffile-prefix-map=$HOME=/home/builder"

echo "Radice neutra pronta: $FUORIGIRI_NEUTRAL"
echo "CARGO_HOME=$CARGO_HOME"
