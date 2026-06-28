#!/usr/bin/env python3
import argparse
import json
import ssl
import urllib.request
from pathlib import Path
import sys as _sys

_sys.path.insert(0, str(Path(__file__).parent))
from config import DEFAULT_BUILD_MATRIX, SUSFS_VERSION


class ReleaseGenerator:
    def __init__(self):
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

    def _fetch_json(self, url: str) -> dict:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Python"})
            with urllib.request.urlopen(req, context=self.ssl_ctx) as response:
                return json.loads(response.read())
        except Exception:
            return {}

    def get_ksu_info(self, explicit_ref: str = "") -> tuple[str, str]:
        if explicit_ref:
            return explicit_ref, explicit_ref

        ksu_tag, ksu_commit = "latest", "unknown"
        latest_release = self._fetch_json("https://api.github.com/repos/SukiSU-Ultra/SukiSU-Ultra/releases/latest")
        if latest_release.get("tag_name"):
            ksu_tag = latest_release["tag_name"]
        else:
            tags = self._fetch_json("https://api.github.com/repos/SukiSU-Ultra/SukiSU-Ultra/tags")
            if isinstance(tags, list) and tags:
                ksu_tag = tags[0].get("name", ksu_tag)

        commit = self._fetch_json("https://api.github.com/repos/SukiSU-Ultra/SukiSU-Ultra/commits/main")
        if commit.get("sha"):
            ksu_commit = commit["sha"][:7]
        return ksu_tag, ksu_commit

    def generate_body(self, susfs_version: str, explicit_ksu_ref: str = "") -> str:
        ksu_tag, ksu_commit = self.get_ksu_info(explicit_ksu_ref)
        configs = [
            f"- Android {key.split('-')[0].replace('android', '')} (Kernel {key.split('-')[1]})"
            for key in sorted(DEFAULT_BUILD_MATRIX.keys())
        ]
        return "\n".join([
            f"## GKI Kernel with SukiSU & SUSFS {susfs_version}",
            "",
            "### SukiSU Info",
            f"- Tag/Ref: `{ksu_tag}`",
            f"- Commit: `{ksu_commit}`",
            "",
            "### Supported Configurations",
            *configs,
            "",
            "### Features",
            f"- SUSFS {susfs_version}",
            "- Manual Syscall Hooks",
            "- Magic Mount Support",
            "- BBR Support",
            "- LZ4KD Support",
        ])

    def save_body(self, output_path: str, susfs_version: str, explicit_ksu_ref: str = ""):
        body = self.generate_body(susfs_version, explicit_ksu_ref)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(body)
        print(body)


def parse_args():
    parser = argparse.ArgumentParser(description="生成 GitHub Release 说明")
    parser.add_argument("output_path", nargs="?", default="RELEASE_BODY.md")
    parser.add_argument("--ksu-ref", default="")
    parser.add_argument("--susfs-version", default=SUSFS_VERSION)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ReleaseGenerator().save_body(args.output_path, args.susfs_version, args.ksu_ref)
