#!/usr/bin/env sh
set -eu
demo_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$demo_root"
for demo_python in python3.12 python3 python; do
    if command -v "$demo_python" >/dev/null 2>&1 && "$demo_python" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 12))' >/dev/null 2>&1; then
        exec "$demo_python" -X utf8 "$demo_root/scripts/run_local_demo.py" "$@"
    fi
done
echo 'Python 3.12 is required. Install it from https://www.python.org/downloads/ then run this script again.' >&2
exit 1
