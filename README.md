# PipistrelloHan

游戏《Pipistrello and the Cursed Yoyo》的中文化补丁，通过运行时修补和字体图集修改实现完整中文支持。

## 项目概述

本项目为游戏《Pipistrello》提供完整的中文本地化支持，包含两个核心组件：

1. **运行时插件** ([`Plugin.cs`](Plugin.cs)) - 基于 BepInEx 的运行时补丁，动态扩展游戏字体字符集
2. **翻译工具链** ([`scripts/`](scripts/)) - 自动化处理翻译文件和生成修改后的字体图集

该项目采用 Harmony 库在运行时修改游戏的 `Global.fontCharRanges` 静态字段，无需修改游戏原始文件即可支持超过 3000 个中文字符。同时提供 Python 工具链来处理翻译数据和生成像素完美的字体图集。

## 使用的技术与库

### .NET / C#

- **[BepInEx 6.x (IL2CPP)](https://github.com/BepInEx/BepInEx)** - Unity 游戏模组框架，提供插件加载和日志系统
- **[HarmonyLib 2.x](https://github.com/pardeike/Harmony)** - .NET 运行时方法补丁库，支持前置/后置/替换补丁

### Python 3.x

- **[Pillow (PIL Fork)](https://python-pillow.org/)** - Python 图像处理库，用于生成和修改字体图集
- **[Fusion Pixel 12px 字体](https://github.com/TakWolf/fusion-pixel-font)** - 开源中文像素字体，支持简体中文和繁体中文

## 快速开始

### 准备工作

- Python 3.x
- .NET 6.0 SDK
- 按照链接中的文档加载游戏的 BepInEx 6.x 插件，运行一次游戏。链接：https://docs.bepinex.dev/master/articles/user_guide/installation/unity_il2cpp.html
- paratranz 上的 csv 文件 https://paratranz.cn/projects/14955/artifact
- fusion-pixel-12px-proportional-zh_hans.ttf 字体文件 https://github.com/TakWolf/fusion-pixel-font/releases

### 设置游戏路径

复制 `Directory.Build.props.example` 文件并重命名为 `Directory.Build.props`：

```powershell
Copy-Item Directory.Build.props.example Directory.Build.props
```

然后编辑 `Directory.Build.props` 文件，设置你的游戏安装路径：

```xml
<Project>
  <PropertyGroup>
    <GamePath>你的游戏安装路径</GamePath>
  </PropertyGroup>
</Project>
```

常见路径示例：

- Steam: `C:\Program Files (x86)\Steam\steamapps\common\Pipistrello and the Cursed Yoyo`
- 自定义安装路径：根据实际情况修改

### 开始工作

1. 将准备的字体 ttf 文件、游戏目录下`\Maps\Localization\strings.csv`、游戏目录下`\Maps\Sprites\font\main16.png`和翻译对照的 csv 文件放到项目目录下的`resources`文件夹
2. 按照顺序运行以下脚本

   ```powershell
   py .\scripts\copy_translations.py
   py .\scripts\extract_unique_chinese_chars.py
   py .\scripts\add_char_to_main16.py
   ```

3. 编译`.net`补丁

   ```powershell
   dotnet build
   ```

4. 执行如下移动文件操作
   - 将编译后的`\bin\Debug\net6.0\`文件夹下的三个文件放到游戏根目录`\BepInEx\plugins`。
   - 将`\resources\main16_modified.png`放回游戏目录下`\Maps\Sprites\font\`，并重命名为`main16.png`。
   - 将`\resource\strings_updated.csv`放回游戏目录下`\Maps\Localization\`，并重命名为`strings.csv`。
5. 运行游戏，在游戏内设置切换为日文即可使用该汉化。

## 项目结构

```
PipistrelloHan/
├── bin/                      # 编译输出目录
│   └── Debug/
├── obj/                      # 中间编译文件
├── resources/                # 资源文件（字体、图集、翻译数据）
└── scripts/                  # Python 工具脚本
    └── __pycache__/          # Python 缓存
```

### 核心目录说明

- **`resources/`** - 包含所有翻译数据文件（CSV）、字体文件（TTF）、字体图集（PNG）和字符分析结果
- **`scripts/`** - 完整的自动化工具链：
  - 字符提取器 - 分析翻译文件中的所有中文字符
  - 翻译复制工具 - 将 ParaTranz 翻译导入游戏数据
  - 图集生成器 - 渲染修改后的字体图集并绘制精确的网格线

## 技术亮点

### C# 运行时补丁

- **[Harmony Patching](https://harmony.pardeike.net/articles/patching.html)** - 使用 HarmonyLib 在游戏运行时动态修改静态构造函数和初始化方法，实现无侵入式的字符集扩展
- **IL2CPP 兼容性** - 通过 BepInEx.Unity.IL2CPP 支持 Unity IL2CPP 编译的游戏
- **双重拦截策略** - 同时 Patch 静态构造函数（`StaticConstructor`）和初始化方法（`Init`），确保在字符集初始化前成功注入
- **数组操作优化** - 使用 `System.Array.Copy` 高效处理大型字符数组的分段复制

### Python 工具链

- **[Pillow (PIL) 图像处理](https://pillow.readthedocs.io/)** - 精确的像素级字体图集生成，支持 1 位深度位图渲染实现无抗锯齿效果
- **CSV 数据处理** - 智能匹配翻译 ID，支持带前缀的续行标记（`^1$`, `^2$` 等）
- **Unicode 字符分析** - 自动提取 CJK 统一汉字（U+4E00-U+9FFF）及扩展区字符
- **参数化网格布局** - 精确控制字体图集的像素网格，支持自定义间距模式和红色边框线

## 实现细节

### 字符集注入原理

游戏使用 `Global.fontCharRanges` 字符数组定义字体支持的字符范围。插件通过以下步骤扩展字符集：

1. 在静态构造函数后置补丁中检测数组初始化
2. 定位原数组中的重复字符标记（`一一`）作为插入点
3. 保留原始字符和网格标记（`™`），插入新的中文字符
4. 每个字符重复两次以符合游戏的字符范围格式
5. 添加特殊符号（`"` 和 `·`）到指定位置

### 字体图集生成

字体图集使用精确的像素网格布局：

- **单元格尺寸**: 11×11 像素内容区域
- **网格间距**: 横向间距遵循 `[4, 4, 5]` 模式循环，纵向固定 21 像素
- **边框线**: 红色（#FF0000）主线加深红色（#820000）延伸 2 像素
- **渲染模式**: 1 位位图模式确保纯黑白输出，避免抗锯齿导致的模糊

## 工具脚本

### [`scripts/extract_unique_chinese_chars.py`](scripts/extract_unique_chinese_chars.py)

从翻译 CSV 文件中提取所有不重复的中文字符，生成字符列表文件供图集生成器使用。

### [`scripts/copy_translations.py`](scripts/copy_translations.py)

将 ParaTranz 翻译平台导出的翻译内容复制到游戏的字符串文件中，支持基础 ID 和续行标记的智能匹配。

### [`scripts/add_char_to_main16.py`](scripts/add_char_to_main16.py)

核心图集生成器，读取字符列表并渲染到字体图集图片中。包含精确的像素级网格绘制和字符定位逻辑。

### [`scripts/const.py`](scripts/const.py)

共享配置文件，定义所有脚本使用的文件路径和常量。

## 许可证

### 本项目代码

本项目的源代码（包括 C# 插件和 Python 工具脚本）采用 **LGPL-2.1 或更高版本** 许可证发布。

详见 [LICENSE](LICENSE) 文件。

### 第三方组件

- **BepInEx**: [LGPL-2.1 License](https://github.com/BepInEx/BepInEx/blob/master/LICENSE)
- **HarmonyLib**: [MIT License](https://github.com/pardeike/Harmony/blob/master/LICENSE)
- **Fusion Pixel 字体**: [SIL Open Font License 1.1](https://github.com/TakWolf/fusion-pixel-font/blob/master/LICENSE-OFL)

### 翻译内容

本项目仅提供技术实现，不包含翻译内容本身。

翻译内容来自 [ParaTranz 平台](https://paratranz.cn/projects/14955)，采用 **CC BY-NC 4.0** 许可证。使用本补丁时，请确保您获取的翻译内容符合该许可证要求。

---

**注意**: 本项目仅供学习交流使用，请支持正版游戏。
