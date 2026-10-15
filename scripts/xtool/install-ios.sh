#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mode=install
case "${1:-}" in
  --check) mode=check; shift ;;
  --login) mode=login; shift ;;
esac
[[ $# -le 1 ]] || { echo 'Dùng: bash install-ios.sh [--check|--login] [tệp.ipa]' >&2; exit 2; }
ipa="${1:-$here/tu-hoc-111-ios-unsigned.ipa}"
[[ -f "$ipa" ]] || { echo 'Không thấy IPA. Giải nén toàn bộ gói hoặc truyền đường dẫn IPA.' >&2; exit 2; }
printf '%s  %s\n' '20ebc3e2bd5205bf9367db496c5a06bef5b57ba09dfccc06bdbfa3d5cdfdcd7f' "$ipa" | sha256sum --check --status
echo 'IPA .20: SHA256 khớp bản phát hành.'
root="${XTOOL_INSTALL_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/tu-hoc-111/xtool-1.22.2}"
bash "$here/install-xtool.sh"
binary="$root/xtool"
devices="$("$binary" devices --usb --no-wait)"
if [[ -z "$devices" ]]; then
  echo 'Chưa thấy iPhone qua USB. Kết nối/passthrough USB vào WSL rồi thử lại.' >&2
  exit 3
fi
echo 'Đã thấy thiết bị USB; thông tin thiết bị không được ghi vào log của script.'
[[ "$mode" != check ]] || exit 0
if [[ "$mode" == login ]]; then
  echo 'Đăng nhập Apple trực tiếp trong xtool; không gửi mật khẩu/mã 2FA vào chat.'
  "$binary" auth login --mode password
fi
"$binary" install --usb "$ipa"
