# 小程序游戏离线移植

从微信、B 站等小程序分享链接核对游戏身份，定位可用的原版构建，梳理资源和存档，再交付可离线游玩的本地副本。Skill 包含 Unity WebGL 工作流、Windows 启动器、Android APK 打包说明及资源核验工具。

## 在 Codex 中使用

把 [`skills/miniapp-game-offline`](skills/miniapp-game-offline/) 目录安装到 Codex 的技能目录。随后附上小程序链接并输入：

> 使用 $miniapp-game-offline 查找同款原版构建，核对本地资源，并按我的要求打包为可离线游玩的版本。

可以附上录屏或已有构建，用来核对版本和实际界面。

## 工具和资料

- [资源清单工具](skills/miniapp-game-offline/scripts/mirror-manifest.py) 对目录和 ZIP/APK 内文件执行 SHA-256 比对，支持明确列出预期变动。
- [本地启动服务](skills/miniapp-game-offline/scripts/serve-local.py) 以固定环回地址启动未压缩的网页游戏，支持 Unity Wasm 的 MIME 类型。
- [Unity WebGL 工作流](skills/miniapp-game-offline/references/unity-webgl.md) 和 [Android 打包流程](skills/miniapp-game-offline/references/android-apk.md) 说明资源、输入、奖励和存档的验收方法。

辅助脚本使用 Python 3.11 或以上。仓库提供 Skill、案例文档与通用脚本。游戏文件与素材沿用其各自的授权。

[MIT License](LICENSE)
