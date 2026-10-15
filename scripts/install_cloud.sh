#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p /workspace/cache /workspace/state /workspace/venvs /workspace/toolchains /workspace/scratch
export PUB_CACHE=/workspace/cache/pub XDG_CONFIG_HOME=/workspace/cache/config
export ANDROID_HOME=/workspace/android-sdk ANDROID_USER_HOME=/workspace/cache/android GRADLE_USER_HOME=/workspace/cache/gradle CHROME_EXECUTABLE=/usr/bin/chromium
python3 scripts/install_jdk.py
export JAVA_HOME=/workspace/toolchains/jdk-21
export PATH=/workspace/toolchains/jdk-21/bin:/workspace/toolchains/flutter-3.35.7/bin:$PATH
if [[ ! -x /workspace/toolchains/flutter-3.35.7/bin/flutter ]]; then
  git clone --depth 1 --branch 3.35.7 https://github.com/flutter/flutter.git /workspace/toolchains/flutter-3.35.7
fi
[[ "$(git -C /workspace/toolchains/flutter-3.35.7 rev-parse HEAD)" == adc901062556672b4138e18a4dc62a4be8f4b3c2 ]]
flutter --version
dart --disable-analytics
[[ -x /workspace/venvs/khohoc/bin/python ]] || python3 -m venv /workspace/venvs/khohoc
/workspace/venvs/khohoc/bin/pip install -r services/api/requirements.lock.txt
npm ci --prefix apps/admin --cache /workspace/cache/npm
(cd apps/mobile && flutter pub get --enforce-lockfile)
python3 scripts/install_android.py
python3 scripts/configure_gradle.py
python3 - <<'PY'
from pathlib import Path
import secrets
p=Path('/workspace/state/khohoc.env')
if not p.exists():
    p.write_text('KHOHOC_ADMIN_TOKEN='+secrets.token_urlsafe(32)+'\nKHOHOC_MODE=development\n')
    p.chmod(0o600)
PY
/workspace/venvs/khohoc/bin/python data/pipelines/import_cli.py data/seeds/questions.json
