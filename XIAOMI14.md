# Xiaomi 14 Notes

当前仓库的目标只有一个：

- 设备方向：Xiaomi 14 / Xiaomi 14 Ultra
- 基线方向：`android14-6.1.138`
- 版本伪装方向：`6.1.138-android14-11-g965475777129-mi`

## 为什么重构

之前仓库沿用了通用 GKI 项目的结构，变量太多：

- 多 Android 版本
- 多 kernel 主线
- 多种可选补丁
- release/telegram/matrix 等外围流程

对这次目标来说，这些都在放大排错成本。

现在的重构原则是：

1. 只保留 Xiaomi 14 的 6.1.138 路径
2. 只保留必要补丁
3. 只保留一个 workflow 和一个构建器
4. 失败时直接落在真实编译问题，而不是外围脚本问题

## 当前固定参数

- `manifest branch`: `common-android14-6.1-2025-06`
- `susfs branch`: `gki-android14-6.1`
- `custom version`: `-android14-11-g965475777129-mi`
- `KernelSU ref`: 默认 `v4.1.3`

## 产物目标

- `xiaomi14-6.1.138-android14-11-g965475777129-mi-AnyKernel3.zip`
- `xiaomi14-6.1.138-android14-11-g965475777129-mi-AnyKernel3-gz.zip`
- `xiaomi14-6.1.138-android14-11-g965475777129-mi-AnyKernel3-lz4.zip`

如果提供签名 key，还会同时生成：

- `boot.img`
- `boot-gz.img`
- `boot-lz4.img`
