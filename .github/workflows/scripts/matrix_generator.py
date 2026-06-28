#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import DEFAULT_BUILD_MATRIX, SUSFS_VERSION


def _sub_level_sort_key(sub_level: str):
    return (1, 0) if sub_level == "X" else (0, int(sub_level))


def generate_build_matrix() -> list:
    builds = []
    for key, configs in DEFAULT_BUILD_MATRIX.items():
        android, kernel = key.split('-')
        for cfg in configs:
            build = {
                "android": android,
                "kernel": kernel,
                "sub_level": cfg["sub_level"],
                "os_patch": cfg["os_patch_level"],
            }
            if "revision" in cfg:
                build["revision"] = cfg["revision"]
            builds.append(build)

    # 按 Android 版本和 Kernel 版本排序
    builds.sort(key=lambda x: (
        int(x["android"].replace("android", "")),
        float(x["kernel"]),
        _sub_level_sort_key(x["sub_level"]),
    ))

    return builds


def generate_classified_matrix() -> dict:
    """生成按 Android 版本分类的矩阵"""
    classified = {}
    for key, configs in DEFAULT_BUILD_MATRIX.items():
        android, kernel = key.split('-')
        if android not in classified:
            classified[android] = {}
        if kernel not in classified[android]:
            classified[android][kernel] = []
        for cfg in configs:
            classified[android][kernel].append(cfg)

    # 排序
    sorted_classified = {}
    for android in sorted(classified.keys(), key=lambda x: int(x.replace("android", ""))):
        sorted_classified[android] = {}
        for kernel in sorted(classified[android].keys(), key=lambda x: float(x)):
            sorted_classified[android][kernel] = sorted(
                classified[android][kernel],
                key=lambda x: _sub_level_sort_key(x["sub_level"])
            )

    return sorted_classified


def save_matrix_output():
    builds = generate_build_matrix()
    output = 'matrix=' + json.dumps(builds)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(output + '\n')
    print(f"Matrix generated: {len(builds)} builds")

    # 保存版本号
    version_output = f'susfs_version={SUSFS_VERSION}'
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(version_output + '\n')
    print(f"SUSFS version: {SUSFS_VERSION}")

    # 同时保存分类后的矩阵
    classified = generate_classified_matrix()
    classified_output = 'classified_matrix=' + json.dumps(classified)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(classified_output + '\n')
    print(f"Classified matrix saved")

    # 保存矩阵摘要
    summary = []
    for android in sorted(classified.keys(), key=lambda x: int(x.replace("android", ""))):
        for kernel, configs in classified[android].items():
            sub_levels = [c["sub_level"] for c in configs]
            summary.append(f"{android}-{kernel}: {', '.join(sub_levels)}")

    summary_output = 'matrix_summary=' + json.dumps(summary)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(summary_output + '\n')

    # 保存 Markdown 格式的摘要
    md_summary = "### 构建矩阵摘要\n\n"
    for android in sorted(classified.keys(), key=lambda x: int(x.replace("android", ""))):
        md_summary += f"**{android.upper()}**\n\n"
        for kernel, configs in classified[android].items():
            sub_levels = ", ".join([c["sub_level"] for c in configs])
            md_summary += f"- {kernel}: {sub_levels}\n"
        md_summary += "\n"

    github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_step_summary:
        with open(github_step_summary, 'a', encoding='utf-8') as f:
            f.write(md_summary)


if __name__ == '__main__':
    save_matrix_output()
