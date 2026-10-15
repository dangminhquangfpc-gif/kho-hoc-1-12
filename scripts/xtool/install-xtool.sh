#!/usr/bin/env bash
set -euo pipefail
umask 077
[[ "$(uname -s)" == Linux ]] || { echo 'Chạy trong Linux/WSL2.' >&2; exit 2; }
case "$(uname -m)" in
  x86_64) arch=x86_64; digest=e3176cdf861f58b7f135c755c7bfaec92d0568ef826027b4e5e3d82b3219ddfe ;;
  aarch64|arm64) arch=aarch64; digest=a42962f19874205ddd807ee4f97687fc83ddc9be176a8b1122a94af3de58d990 ;;
  *) echo 'Kiến trúc không được hỗ trợ.' >&2; exit 2 ;;
esac
root="${XTOOL_INSTALL_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/tu-hoc-111/xtool-1.22.2}"
mkdir -p "$root"
root="$(cd -- "$root" && pwd)"
image="$root/xtool-$arch.AppImage"
if [[ ! -f "$image" ]]; then
  temporary="$(mktemp "$root/download.XXXXXXXX")"
  trap 'rm -f -- "$temporary"' EXIT
  curl --fail --location --retry 2 --proto '=https' --tlsv1.2 \
    "https://github.com/xtool-org/xtool/releases/download/1.22.2/xtool-$arch.AppImage" \
    --output "$temporary"
  printf '%s  %s\n' "$digest" "$temporary" | sha256sum --check --status
  mv -- "$temporary" "$image"
  trap - EXIT
fi
printf '%s  %s\n' "$digest" "$image" | sha256sum --check --status
chmod u+x "$image"
if [[ ! -e "$root/runtime" ]]; then
  temporary="$(mktemp -d "$root/extract.XXXXXXXX")"
  trap 'rm -rf -- "$temporary"' EXIT
  (cd -- "$temporary" && "$image" --appimage-extract > extract.log)
  mv -- "$temporary/squashfs-root" "$root/runtime"
  rm -rf -- "$temporary"
  trap - EXIT
fi
[[ -x "$root/runtime/AppRun" ]] || { echo 'Runtime chưa đầy đủ.' >&2; exit 2; }
cat > "$root/xtool" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
exec "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/runtime/AppRun" "$@"
WRAPPER
chmod u+x "$root/xtool"
"$root/xtool" --version
printf 'xtool CLI: %s/xtool\n' "$root"
