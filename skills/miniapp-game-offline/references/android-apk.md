# Android APK 打包与验证

## 从已可离线运行的构建封装

- 打包前先确认独立网页能跑过实际关卡。WebGL 版可封装到硬件加速 WebView，按原游戏的画幅和触屏可达区域决定方向。apk 内保存完整相对目录，适配状态栏、导航栏、异形屏和原有底栏。手指点按和拖动都要通过真实 Android 输入测试。
- 静态本地游戏使用固定 HTTPS origin，例如 `https://appassets.androidplatform.net/assets/game/index.html`。用 AndroidX WebViewAssetLoader 或限定同源与路径的 `shouldInterceptRequest` 从 APK 资产读取。启用 JavaScript、DOM 存储和硬件加速；指定 Wasm 响应为 `application/wasm`，其他类型和压缩标头以构建要求为准。固定 origin 和入口路径以便覆盖安装后读到旧存档。纯离线包可省略 INTERNET 权限。输入来源由本地 WebView 指向自有资产目录。
- 先设正常的渲染缩放，再按设备画质和帧率取舍。例如 2× 密度设备上，把 Unity DPR 上限从 1.5 调到 2 会减少画布拉伸。Unity 启动阶段要确认资源连通性和当前设备 WebView 的 WebGL 支持。
- 已有可用的 Android 项目时沿用其构建方式。轻量 WebView 壳可以用官方 SDK Build Tools 构建。手工链路依次执行 `javac`、`d8 --lib android.jar`、`aapt2 compile` 和 `link`、将 `classes.dex` 及 `assets/game/` 合入 ZIP、`zipalign`、`apksigner sign`、`apksigner verify`。AAPT2 合入大批资产后出现 ZIP header 警告时，先用 AAPT2 链接清单和资源，再用标准 ZIP 写入资产和 DEX、对齐并签名。
- 后续版本保留包名、签名和存档 origin，递增 versionCode。首次本地签名把私钥和口令置于工作区的非交付位置。仅交付可安装 APK 和用户要求的附加文件。为 APK 内游戏目录生成单独的资产清单，执行签名验证和资产 SHA-256 对照。

[Android 的 WebViewAssetLoader 文档](https://developer.android.com/reference/androidx/webkit/WebViewAssetLoader) · [官方命令行构建说明](https://developer.android.com/build/building-cmdline)

## 用最终 APK 验证

1. 用已有设备或隔离的官方 Android 模拟器安装同一个待交付 APK。可以先用 `adb install -r` 对已安装测试版验证覆盖更新。设备有多个时指定测试序列号。记录系统及 WebView 版本。
2. 在测试设备断网，实际启动并完成开场、第一关的触屏点按和移动。用最新画面验证背包、菜单、商店和返回键的位置。纵向商店里的奖励可能需要滚动才完整出现。
3. 新档按原画面走到用户关注的入口，按原按钮领一项代表奖励并记录余额或库存变化。返回地图等自动保存，结束进程并重开，复核保存结果。必要时保留一张原始入口截图为说明。
4. 对用户区分模拟器与真机测试，说明最低安装版本与 WebView 能力的条件。压缩包、自签名指纹、HTTP 响应、应用启动状态和画面出现各是单项证据，完整验收以实际操作和存档为准。
