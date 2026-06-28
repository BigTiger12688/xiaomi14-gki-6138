# Xiaomi 14 GKI 6.1.138 Builder

这个仓库现在只做一件事：为 Xiaomi 14 / Xiaomi 14 Ultra 构建一套尽量贴近
`6.1.138-android14-11-g965475777129-mi` 的 GKI KernelSU + SUSFS 内核产物。

旧的多版本矩阵、全量发布链、通用脚本已经移除。当前项目只保留：

- 一个 GitHub Actions 工作流
- 一个本地 PowerShell + WSL 启动脚本
- 一个单文件 Python 构建器

## 固定预设

- Android: `android14`
- Kernel: `6.1`
- Sub-level: `138`
- OS patch: `2025-06`
- Custom version: `-android14-11-g965475777129-mi`
- 默认 KernelSU ref: `v4.1.3`

## 入口

- GitHub Actions: `.github/workflows/xiaomi14-6.1.138.yml`
- 本地脚本: `build-xiaomi14-6138.ps1`
- 构建器: `.github/workflows/scripts/xiaomi14_builder.py`

## GitHub Actions 用法

1. 打开 `Actions`
2. 选择 `Xiaomi 14 Android14 6.1.138 Build`
3. 点击 `Run workflow`
4. 需要时修改：
   - `kernelsu_ref`
   - `susfs_ref`

默认会构建：

- AnyKernel3 ZIP
- 如果提供 `BOOT_SIGN_KEY` secret，还会额外生成签名后的 `boot.img` / `boot-gz.img` / `boot-lz4.img`

## 本地构建

要求：

- Windows + WSL，或直接 Linux
- `python3 git curl zip unzip patch ccache`

示例：

```powershell
.\build-xiaomi14-6138.ps1
.\build-xiaomi14-6138.ps1 -PreflightOnly
.\build-xiaomi14-6138.ps1 -FromStage build_kernel
```

## 说明

这个仓库不再尝试兼容别的 Android 版本、别的 GKI 主线、别的机型，也不再保留旧项目里的矩阵和 release 生成逻辑。这样做的目的就是把变量压到最少，优先把你这台机器的 6.1.138 构建链跑通。
