---
agent:
  effort: low
---

# Runbook：Flutter 构建

## 适用场景

- 生成 Flutter 客户端可分发产物：iOS、Android、Web 与桌面端。
- 调整构建参数注入、release 混淆、符号表、签名配置或产物校验方式。
- 发布、上传、灰度与回滚不在本文范围，见[客户端发布](../../delivery/client-release.md)。

## 前置读取

- [Make 构建入口](../../implementation/make.md)
- [客户端运行](runtime.md)

## 构建入口

- 构建统一通过 `make` 目标执行，交付流程中不手写 `flutter build`；目标内部负责依赖解析、生成步骤、参数注入与产物定位。
- 每个端至少有一个构建目标，命名沿用项目 Make 约定；同一目标重复执行必须得到同一组产物路径。
- 目标结束时打印产物绝对路径、版本号与构建参数摘要；缺少必需参数时以非零状态退出，不使用默认地址继续构建。
- 目标在构建开始与结束时输出 Git 分支、提交 hash 与工作区状态；`git status --porcelain` 非空时明确标记为未提交工作区。
- 构建机需满足目标端工具链：iOS 与 macOS 需要 macOS 与 Xcode，Android 需要 Android SDK 与项目要求的 JDK 主版本；工具链不满足时在构建前失败并报告缺失项。
- `build/`、`.dart_tool/` 与符号表目录不提交；产物只由构建生成，不手工打包或修改包内容。

## 构建参数

- 环境地址、环境名与功能开关全部通过 `--dart-define` 注入，代码与资源文件中不硬编码。
- 可分发产物至少注入：API 基址 `<APP>_API_BASE_URL`、公共基址 `<APP>_APP_BASE_URL`、环境名 `<APP>_APP_ENV`。
- 每个目标只对应一个环境；生产构建缺少参数时失败，不回退到开发地址或默认生产地址。
- release 构建关闭调试开关，例如 `<APP>_HTTP_INSPECTOR_ENABLED=false`；开发专用入口不出现在可分发产物中。

## 版本与构建号

- `pubspec.yaml` 的 `version: <x.y.z>+<构建号>` 是唯一版本来源，构建号随每次对外构建单调递增。
- 构建前确认版本号与构建号已更新；同一版本号与构建号不重复产出不同内容。
- iOS 导出配置固定 `manageAppVersionAndBuildNumber=false`，不允许签名工具自动改写版本号或构建号。

## Release 构建

- 可分发产物一律使用 `--release`，不使用 `--profile` 或 debug 产物对外。
- 需要压缩 Dart 代码时同时使用 `--obfuscate --split-debug-info=build/symbols/<端>`；符号表按端与版本归档，缺失符号表的产物不交付。
- 使用 `--no-pub` 时，目标必须先显式执行 `flutter pub get`；依赖未解析时不得跳过。
- 交付构建从 `flutter clean` 与 `flutter pub get` 后的工作区开始；目标可复用与源文件指纹匹配的产物，并提供强制重建开关，复用时不得跳过产物校验。

## 各端产物

| 端 | 构建命令 | 产物位置 | 额外要求 |
| --- | --- | --- | --- |
| iOS | `flutter build ipa --release --obfuscate --split-debug-info=build/symbols/ios --export-options-plist=<plist>` | `build/ios/ipa/*.ipa` | export options 固定 `method=app-store-connect`、`teamID=<团队 ID>`、`signingStyle=automatic`、`signingCertificate=Apple Distribution`、`uploadSymbols=true` |
| Android | `flutter build appbundle --release` 与 `flutter build apk --release`，两条命令都带 `--obfuscate --split-debug-info=build/symbols/android` 与同一组 `--dart-define` | `build/app/outputs/bundle/release/*.aab`、`build/app/outputs/flutter-apk/*.apk` | 包名与项目事实一致；签名取自 `android/key.properties` |
| Web | `flutter build web --release --no-web-resources-cdn`；目标端要求 Wasm 时加 `--wasm` | `build/web/` | 使用 Android App Links 时，构建前生成 `web/.well-known/assetlinks.json`；引擎与静态资源由自有 CDN 提供时固定版本 |
| macOS | `flutter build macos --release` | `build/macos/Build/Products/Release/` | 签名与公证凭据按 macOS 发布要求配置 |
| Windows | `flutter build windows --release` | `build/windows/x64/runner/Release/` | 安装包格式在构建目标内生成 |
| Linux | `flutter build linux --release` | `build/linux/x64/release/bundle/` | 安装包格式在构建目标内生成 |

## 签名与凭据

- 签名材料只在构建配置中引用：iOS 团队 ID、证书名与 export options plist，Android keystore 路径、别名与密码；应用代码不读取凭据。
- `android/key.properties`、keystore 文件、App Store Connect API Key 与签名密码不入库，通过本地环境文件或密钥管理注入。
- release 签名材料缺失时构建失败，不回退 debug 签名，不产出可分发产物。
- 构建前确认证书与 profile 在有效期内，团队 ID、包名与产物目标一致。

## 产物校验

- 产物存在且非空，路径与「各端产物」表格一致，不依赖人工查找。
- 版本名与构建号等于 `pubspec.yaml` 的值。
- 包名（iOS bundle id、Android applicationId）等于项目事实，未随构建参数变化。
- iOS 产物通过 `codesign --verify`（对解包后的 `.app`），Android APK 通过 `apksigner verify`。
- 每个端的符号表存在于 `build/symbols/<端>`，并与产物同版本归档。
- 记录产物 SHA-256 与构建输出的 Git 提交；工作区不干净时在记录中标注。
- 同一提交重复构建的版本号与构建号一致。

## 步骤

1. 确认目标端、目标环境、版本号与构建号，核对 `pubspec.yaml`。
2. 确认签名材料、`--dart-define` 参数与 CDN、资源依赖已就绪。
3. 在仓库根目录执行 `make <构建目标>`，记录退出码、末尾输出与 Git 提交。
4. 按「产物校验」逐项检查路径、版本、包名、签名与符号表。
5. 记录 SHA-256 与提交；发布、上传与灰度按[客户端发布](../../delivery/client-release.md)执行。
6. 清理临时文件，确认 `build/`、符号表与凭据未进入提交。

## 验证

- `make <构建目标>` 退出码为 0，产物路径与表格一致且非空。
- 版本名与构建号与 `pubspec.yaml` 一致，包名与项目事实一致。
- release 产物启用混淆，符号表存在并与产物同版本归档。
- iOS 与 Android 签名校验通过，签名材料未提交。
- 产物 SHA-256 与提交已记录，工作区无构建产物或凭据改动。
- 构建输出包含 Git 分支、提交 hash 与工作区状态，产物记录中的提交与输出一致。

## 相关

- [客户端发布](../../delivery/client-release.md)
