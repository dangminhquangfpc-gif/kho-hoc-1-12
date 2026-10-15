#!/usr/bin/env python3
"""Render original Tự học 111 brand assets using Inkscape and ImageMagick.

Run from any directory. --check renders into a temporary tree and compares all
generated assets with the checked-in files. No network requests are made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID = Path("apps/mobile/android/app/src/main/res")
IOS = Path("apps/mobile/ios/Runner/Assets.xcassets/AppIcon.appiconset")
WEB = Path("apps/mobile/web")
STORE = Path("docs/store/assets")
WHITE = "#ffffff"
INDIGO = "#263677"
TEAL = "#51d9ca"
SVG_NS = "{http://www.w3.org/2000/svg}"


def run(*command: str, env: dict[str, str]) -> None:
    subprocess.run(command, check=True, env=env, capture_output=True)


def render(output: Path, scratch: Path) -> list[Path]:
    inkscape = shutil.which("inkscape")
    magick = shutil.which("magick")
    if not inkscape or not magick:
        raise SystemExit("Install Inkscape and ImageMagick 7 before rendering.")
    env = dict(os.environ)
    env["INKSCAPE_PROFILE_DIR"] = str(scratch / "inkscape")
    env["XDG_CACHE_HOME"] = str(scratch / "cache")
    env["SOURCE_DATE_EPOCH"] = "0"
    generated: list[Path] = []

    def target(relative: Path) -> Path:
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        generated.append(relative)
        return destination

    full = scratch / "icon-1024.png"
    run(inkscape, str(ROOT / "assets/brand/tu-hoc-111-icon.svg"),
        "--export-type=png", f"--export-filename={full}", env=env)

    def png(relative: Path, size: int) -> None:
        destination = target(relative)
        run(magick, str(full), "-resize", f"{size}x{size}", "-strip",
            "-define", "png:exclude-chunk=date,time", f"PNG24:{destination}", env=env)
        check_png(destination, size, size)

    for density, size in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96),
                          ("xxhdpi", 144), ("xxxhdpi", 192)):
        png(ANDROID / f"mipmap-{density}/ic_launcher.png", size)
        png(ANDROID / f"mipmap-{density}/ic_launcher_round.png", size)

    # Retain the Xcode idiom/size/scale mapping, including the opaque 1024 icon.
    contents = json.loads((ROOT / IOS / "Contents.json").read_text())
    ios_sizes: dict[str, int] = {}
    for entry in contents["images"]:
        size = round(float(entry["size"].split("x")[0]) * float(entry["scale"][:-1]))
        ios_sizes[entry["filename"]] = size
    for filename, size in sorted(ios_sizes.items()):
        png(IOS / filename, size)

    for size in (192, 512):
        png(WEB / f"icons/Icon-{size}.png", size)
        png(WEB / f"icons/Icon-maskable-{size}.png", size)
    png(WEB / "favicon.png", 32)
    png(STORE / "icon-512.png", 512)

    feature_raw = scratch / "feature.png"
    run(inkscape, str(ROOT / "assets/brand/tu-hoc-111-feature.svg"),
        "--export-type=png", f"--export-filename={feature_raw}", env=env)
    feature = target(STORE / "feature-1024x500.png")
    run(magick, str(feature_raw), "-strip", "-define", "png:exclude-chunk=date,time",
        f"PNG24:{feature}", env=env)
    check_png(feature, 1024, 500)

    # Adaptive artwork is scaled inside the Android safe circle. The background
    # is separate so launcher masks and Android 13 themed icons remain legible.
    svg = ET.parse(ROOT / "assets/brand/tu-hoc-111-icon.svg").getroot()
    digit_and_book = svg.find(f"{SVG_NS}g")
    assert digit_and_book is not None
    paths = [node.attrib["d"] for node in digit_and_book]
    accent = svg.findall(f"{SVG_NS}path")[-1].attrib["d"]
    vector_header = ('<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
                     '    android:width="108dp" android:height="108dp"\n'
                     '    android:viewportWidth="1024" android:viewportHeight="1024">\n'
                     '    <group android:scaleX="0.8" android:scaleY="0.8"\n'
                     '        android:pivotX="512" android:pivotY="512">\n')
    for monochrome, filename in ((False, "ic_launcher_foreground.xml"),
                                 (True, "ic_launcher_monochrome.xml")):
        chunks = [vector_header]
        for path in paths:
            chunks.append(f'        <path android:fillColor="{WHITE}" android:pathData="{path}"/>\n')
        chunks.append(f'        <path android:fillColor="@android:color/transparent" '
                      f'android:strokeColor="{WHITE if monochrome else TEAL}" '
                      'android:strokeWidth="22" android:strokeLineCap="round" '
                      f'android:pathData="{accent}"/>\n')
        chunks.append('    </group>\n</vector>\n')
        target(ANDROID / f"drawable/{filename}").write_text("".join(chunks))
    target(ANDROID / "values/brand_colors.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        f'    <color name="ic_launcher_background">{INDIGO}</color>\n</resources>\n')
    for api in (26, 33):
        monochrome = ('    <monochrome android:drawable="@drawable/ic_launcher_monochrome"/>\n'
                      if api >= 33 else "")
        adaptive = ('<?xml version="1.0" encoding="utf-8"?>\n'
                    '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
                    '    <background android:drawable="@color/ic_launcher_background"/>\n'
                    '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n'
                    f'{monochrome}</adaptive-icon>\n')
        for name in ("ic_launcher", "ic_launcher_round"):
            target(ANDROID / f"mipmap-anydpi-v{api}/{name}.xml").write_text(adaptive)

    checksums = {
        str(path): hashlib.sha256((output / path).read_bytes()).hexdigest()
        for path in sorted(generated)
    }
    target(STORE / "brand-assets.sha256.json").write_text(
        json.dumps(checksums, indent=2, ensure_ascii=False) + "\n")
    return generated


def check_png(path: Path, width: int, height: int) -> None:
    content = path.read_bytes()
    if content[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG: {path}")
    actual_width, actual_height, depth, color_type = struct.unpack(">IIBB", content[16:26])
    if (actual_width, actual_height, depth, color_type) != (width, height, 8, 2):
        raise ValueError(f"Expected opaque RGB8 {width}x{height}: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare regenerated assets without editing files")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="tu-hoc-brand-") as temporary:
        scratch = Path(temporary)
        output = scratch / "generated" if args.check else ROOT
        generated = render(output, scratch)
        if args.check:
            mismatches = [str(path) for path in generated
                          if not (ROOT / path).is_file()
                          or (ROOT / path).read_bytes() != (output / path).read_bytes()]
            if mismatches:
                raise SystemExit("Brand assets differ: " + ", ".join(mismatches))
        print(f"{'Verified' if args.check else 'Generated'} {len(generated)} original brand assets.")


if __name__ == "__main__":
    main()
