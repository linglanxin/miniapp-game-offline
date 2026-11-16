# Unity WebGL 构建分析与资源镜像

## 从分享页到可运行构建

- 微信短码、B 站扫码落地页和已下线入口常只负责跳转。先用游戏名、公开应用条目、可见开发者字段、授权范围内观察到的对应 Web 请求和录屏中的独特界面交叉核对。搜索 GitHub、Gitee 等仓库时检查提交内容、许可证、资源目录和运行入口。仓库有同名或同玩法时，继续核对画面和关卡。
- Unity WebGL 常能从入口 HTML、loader 配置、开发者页面或对应网页试玩的实际请求定位。记录入口、产品版本、Unity 版本以及对照证据。区分来自原开发者的发布构建、门户转载和第三方复刻。不同平台同名产品的存档和内容范围要分别验证。
- 以实际 loader 配置为准，按原目录保留 loader、framework、Wasm、data、StreamingAssets、符号文件和原有压缩后缀。前后对照入口、数据、场景名和 UI。对单机内容依赖的接口保留能实现同等行为的本地数据或处理。无法提供的账号联机功能按实际范围说明。

## 以清单为准镜像

- 记录原始构建文件的相对路径、大小和 SHA-256，再做可写副本。对 Addressables 读取 settings、catalog、catalog hash 和资源内部 ID，理解运行时路径占位符及不同目录。包名含空格、括号、中文等字符时，按 URL 路径段编码，落盘仍用构建查找的原名。
- 清单是下载队列和完整性基准，启动时看到的网络请求只是当前场景的子集。只有 HEAD 给出可信长度时才拿长度核对，遇到不支持 HEAD 或缺少长度，以成功 GET、保存大小、文件签名和运行时加载为证据。限定并发、超时和重试次数，保留实际失败条目。支持 UnityFS 的包可以抽查头部并读取代表性素材。
- 本地索引若包含绝对资源服务器，确认是哪一层解析内部路径，优先使用配置的本地根或最小化修改。访问失败时先看路径、大小写、编码、MIME、Content-Encoding 和跨域错误。HTTP 成功也要确认响应体确实是期望的二进制。
- [清单脚本](../scripts/mirror-manifest.py) 使用 Python 3.11 或以上，可为目录建立基准，再核对目录或 ZIP/APK。把清单放在游戏目录之外。发布包原样资源应逐个匹配，预期修改和包装附加文件单独列出。

```powershell
python mirror-manifest.py snapshot original-game -o baseline.json
python mirror-manifest.py verify baseline.json staged-game --changed index.html --changed Build/Game.wasm
python mirror-manifest.py snapshot staged-game -o release-assets.json
python mirror-manifest.py verify release-assets.json Game.apk --prefix assets/game
```

## 分析与验收修改

- Wasm 的原生路线从符号 JSON、框架 JS 接口、Wasm 反汇编和可辨认的 Unity 方法开始。先区别插件桥接、弹层、暂停、奖励回调与资源库存。静态改动使用原哈希和确定的方法体，保存匹配位置和前后指令。改变指令长度时同步更新方法体、代码段等长度字段，用 WebAssembly 编译验证，再通过正常入口实测。
- 插屏关闭时确保原本的继续回调完成。激励奖励保留成功回调、库存增量、计数、连领和失败行为。用真实状态判断，例如宝石从 3 到 13、装备入包、武器进化到下一等级、返回地图后能继续移动。即使最终仍显示广告图标，也要确认点击后直接走到真实奖励。
- 领完后按钮像卡住时，分查广告暂停、时间倍率和引导层。位于商店或背包后方的地图引导可能锁住输入。适宜在真正可见时才触发该步骤，保留其他新手引导。入口缺失时先查显示条件；用户需要提早访问时，用游玩阶段标记限定入口生效时机，验证开场和旧档。
- 浏览器自带本地存储、Unity PlayerPrefs 或 IndexedDB 可存不同的数据。固定 origin 和路径，用本地存档做一次资源到达后的退出、重新启动和读取。奖励写入可能晚于点击或动画结束，应按实际自动保存时机复测。
- 分清画布 CSS 尺寸和 GPU 像素尺寸。高 DPI 提高文字和轮廓清晰度，同时增加显存和渲染负担。贴图细节受源文件限制，可直接检查 Texture2D 的像素尺寸、MipCount 和压缩格式。

[Unity 关于 WebGL 画布尺寸和像素密度的手册](https://docs.unity3d.com/cn/2022.3/Manual/webgl-canvas-size.html)
