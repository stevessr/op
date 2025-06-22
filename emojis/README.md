# 图片智能重命名工具

这是一个使用Google Gemini API 2.5 Flash模型来识别图片内容并自动重命名的Python脚本。

## 功能特点

- 🔍 使用Gemini 2.5 Flash模型智能识别图片内容
- 📁 递归处理目录及其所有子目录中的图片
- 🏷️ 根据图片内容生成有意义的中文文件名
- 🛡️ 支持试运行模式，预览重命名结果
- 📝 详细的日志记录和重命名历史
- ⚡ 支持多种图片格式（JPG, PNG, GIF, BMP, WebP等）
- 🔄 自动处理文件名冲突
- ⏱️ 可配置API调用间隔，避免频率限制
- 🚫 智能跳过已处理文件，避免重复重命名
- 🔄 支持强制重新处理选项
- ⏭️ 灵活的文件跳过配置（格式、文件名模式、目录）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 获取Gemini API密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 保存密钥备用

## 自定义API端点配置

如果你需要使用代理或其他API端点，可以通过以下方式配置：

### 方法1：修改配置文件

编辑 `config.py` 文件：
```python
GEMINI_BASE_URL = "https://your-proxy.com/v1"  # 设置你的代理URL
```

### 方法2：命令行参数

```bash
python image_renamer.py /path/to/images --api-key YOUR_KEY --base-url https://your-proxy.com/v1
```

### 支持的代理格式

- OpenAI兼容格式：`https://your-proxy.com/v1`
- 直接Gemini代理：`https://your-gemini-proxy.com`
- 其他自定义端点

## 使用方法

### 基本用法

```bash
python image_renamer.py /path/to/your/images --api-key YOUR_API_KEY
```

### 试运行模式（推荐先使用）

```bash
python image_renamer.py /path/to/your/images --api-key YOUR_API_KEY --dry-run
```

### 高级选项

```bash
python image_renamer.py /path/to/your/images \
    --api-key YOUR_API_KEY \
    --model gemini-2.0-flash-exp \
    --base-url https://your-proxy.com/v1 \
    --max-files 100 \
    --delay 2.0 \
    --dry-run
```

## 参数说明

- `directory`: 要处理的图片目录路径（必需）
- `--api-key`: Gemini API密钥（必需）
- `--model`: 使用的模型名称（默认：gemini-2.0-flash-exp）
- `--base-url`: 自定义API基础URL，用于代理或其他端点（可选）
- `--dry-run`: 试运行模式，只显示重命名预览，不实际重命名
- `--max-files`: 限制处理的最大文件数量
- `--delay`: API调用间隔秒数（默认：1.0秒）
- `--force-reprocess`: 强制重新处理已处理过的文件
- `--skip-formats`: 跳过的图片格式（如：--skip-formats .gif .svg）
- `--skip-patterns`: 跳过的文件名模式（如：--skip-patterns thumb* *_backup.*）
- `--skip-dirs`: 跳过的目录名（如：--skip-dirs thumbnails backup）

## 示例

### 处理当前目录的所有图片（试运行）

```bash
python image_renamer.py . --api-key YOUR_API_KEY --dry-run
```

### 处理特定目录，限制100个文件

```bash
python image_renamer.py /path/to/emojis --api-key YOUR_API_KEY --max-files 100
```

### 使用较长的API调用间隔

```bash
python image_renamer.py /path/to/images --api-key YOUR_API_KEY --delay 3.0
```

### 跳过特定文件

```bash
# 跳过GIF和SVG格式
python image_renamer.py /path/to/images --api-key YOUR_API_KEY --skip-formats .gif .svg

# 跳过缩略图和备份文件
python image_renamer.py /path/to/images --api-key YOUR_API_KEY --skip-patterns thumb* *_backup.*

# 跳过特定目录
python image_renamer.py /path/to/images --api-key YOUR_API_KEY --skip-dirs thumbnails backup temp
```

## 输出文件

- `image_renamer.log`: 详细的运行日志
- `rename_history.json`: 重命名历史记录（仅在实际重命名时生成）

## 重命名历史功能

程序会自动记录所有重命名操作，并在后续运行时智能跳过已处理的文件：

### 自动跳过已处理文件
- 程序启动时自动加载 `rename_history.json`
- 跳过已经重命名过的文件，避免重复处理
- 节省API调用次数和处理时间

### 强制重新处理
如果需要重新处理已处理过的文件：
```bash
# 命令行方式
python image_renamer.py /path/to/images --api-key YOUR_KEY --force-reprocess

# 简化脚本方式
python simple_rename.py
# 选择"是否强制重新处理？(y/N): y"
```

### 历史记录格式
```json
[
  {
    "original": "原始文件路径",
    "new": "重命名后路径",
    "timestamp": 1234567890.123
  }
]
```

## 文件跳过配置

程序支持灵活的文件跳过配置，避免处理不需要的文件：

### 配置方式

#### 方法1：修改配置文件

编辑 `config.py` 文件：
```python
# 跳过的图片格式
SKIP_FORMATS = {'.gif', '.svg', '.ico'}

# 跳过的文件名模式（支持通配符）
SKIP_FILENAME_PATTERNS = [
    'thumb*',           # 跳过缩略图
    '*_backup.*',       # 跳过备份文件
    'temp_*',           # 跳过临时文件
]

# 跳过的目录名
SKIP_DIRECTORIES = {
    'thumbnails',       # 跳过缩略图目录
    'backup',           # 跳过备份目录
    'temp',             # 跳过临时目录
}
```

#### 方法2：命令行参数

```bash
python image_renamer.py /path/to/images \
    --api-key YOUR_KEY \
    --skip-formats .gif .svg \
    --skip-patterns thumb* *_backup.* \
    --skip-dirs thumbnails backup
```

### 跳过规则说明

1. **格式跳过**: 根据文件扩展名跳过（如 .gif, .svg）
2. **模式跳过**: 支持通配符匹配文件名
   - `*` 匹配任意字符
   - `?` 匹配单个字符
   - 示例：`thumb*` 匹配所有以thumb开头的文件
3. **目录跳过**: 跳过指定名称的目录及其所有子文件

### 常用跳过配置

```python
# 跳过动图和矢量图
SKIP_FORMATS = {'.gif', '.svg', '.ico'}

# 跳过系统和临时文件
SKIP_FILENAME_PATTERNS = [
    '.*',               # 隐藏文件
    'Thumbs.db',        # Windows缩略图
    '.DS_Store',        # macOS系统文件
    'thumb*',           # 缩略图
    '*_backup.*',       # 备份文件
    'temp_*',           # 临时文件
]

# 跳过系统目录
SKIP_DIRECTORIES = {
    '.git', '.svn',     # 版本控制
    'node_modules',     # 依赖目录
    '__pycache__',      # Python缓存
    'thumbnails',       # 缩略图目录
    'backup', 'temp',   # 备份和临时目录
}
```

## 注意事项

1. **先使用试运行模式**: 建议先使用 `--dry-run` 参数预览重命名结果
2. **API费用**: Gemini API按使用量收费，建议先小批量测试
3. **备份数据**: 重命名前请备份重要图片文件
4. **网络连接**: 需要稳定的网络连接访问Gemini API
5. **文件名限制**: 生成的文件名会自动清理特殊字符，确保兼容性

## 支持的图片格式

- JPG/JPEG
- PNG
- GIF
- BMP
- WebP

## 故障排除

### API密钥错误
确保API密钥正确且有效，检查是否有足够的配额。

### 网络连接问题
检查网络连接，确保可以访问Google AI服务。

### 文件权限问题
确保脚本有读取源文件和写入目标目录的权限。

### 内存不足
对于大量图片，可以使用 `--max-files` 参数分批处理。

## 许可证

MIT License
