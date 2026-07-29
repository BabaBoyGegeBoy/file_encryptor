# File Encryptor

> **声明**：本项目是本人根据某网盘客户端（小白羊类工具）公开的**功能文字描述**，自行尝试复现的一套文件加密/解密工具，**并非该软件的官方实现，也未参考其源码**。算法与文件格式均为独立设计，仅供学习研究。

一个基于 Python 的文件加密/解密工具，支持 AES-CTR 和 RC4-MD5 两种加密算法。

## 功能特性

- **加密算法**：支持 AES-CTR（安全高效）和 RC4-MD5（兼容性好）
- **密码保护**：支持设置密码进行加密/解密
- **文件名加密**：可选加密文件名，保护文件隐私
- **格式筛选**：支持按文件格式筛选加密
- **批量处理**：支持整个目录的批量加密/解密
- **大文件支持**：流式处理，支持任意大小文件
- **跳过小文件**：可选自动跳过小于指定大小的文件

## 技术实现

### 加密流程

```
输入文件 → 读取文件流 → 密码派生密钥(PBKDF2-SHA256) → 逐块加密(AES-CTR/RC4-MD5) → 写入加密文件
```

### 解密流程

```
加密文件 → 读取头部信息 → 密码派生密钥 → 逐块解密 → 还原原始文件
```

### 文件格式

加密文件包含 128 字节头部：
- 魔数（7 字节）：标识加密文件格式
- 算法标识（1 字节长度 + 算法名）
- IV（1 字节长度 + 初始化向量）
- Salt（1 字节长度 + 盐值）
- 原始文件名（2 字节长度 + 文件名）
- 文件名加密标记（1 字节）

## 安装依赖

```bash
pip install cryptography
```

## 命令行使用

### 加密文件/目录

```bash
python cli.py encrypt -i <输入路径> -o <输出路径> [选项]
```

### 解密文件/目录

```bash
python cli.py decrypt -i <输入路径> -o <输出路径> [选项]
```

### 参数说明

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--algorithm` | `-a` | 加密算法：`AES-CTR`（默认）或 `RC4-MD5` |
| `--input` | `-i` | 输入目录或文件路径（必填） |
| `--output` | `-o` | 输出目录路径（必填） |
| `--password` | `-p` | 加密/解密密码 |
| `--format` | `-f` | 文件格式筛选，如 `.mp4` |
| `--encrypt-name` | `-n` | 加密文件名 |
| `--skip-small` | `-s` | 跳过小于指定大小的文件 |
| `--threshold` | `-t` | 小文件阈值（字节），默认 5MB |

## 使用示例

### 加密单个文件

```bash
python cli.py encrypt -i ./test.txt -o ./encrypted -p mypassword
```

### 加密整个目录（只加密 mp4 文件）

```bash
python cli.py encrypt -i ./videos -o ./encrypted_videos -p mypassword -f .mp4
```

### 加密目录并加密文件名

```bash
python cli.py encrypt -i ./documents -o ./encrypted_docs -p mypassword -n
```

### 解密目录

```bash
python cli.py decrypt -i ./encrypted_docs -o ./decrypted_docs -p mypassword
```

## API 使用

```python
from encryptor import FileEncryptor

encryptor = FileEncryptor('AES-CTR')

# 加密文件
encryptor.encrypt_file('input.txt', 'output.txt.enc', password='mypassword')

# 解密文件
encryptor.decrypt_file('output.txt.enc', './decrypted', password='mypassword')

# 加密目录
results = encryptor.encrypt_directory('./input', './output', password='mypassword')

# 解密目录
results = encryptor.decrypt_directory('./output', './decrypted', password='mypassword')
```

## 注意事项

1. **仅支持加密文件**，不支持文件夹格式
2. **不能把文件夹打包加密成一个文件**，每个文件独立加密
3. **加密后的文件需要设置安全密码解密**，加密时设置了密码，解密时必须提供正确密码
4. **被加密的文件可以认为是全世界独一无二的**，相同内容使用不同密码加密结果不同
5. **AES-CTR 可以跑满 800Mbps+ 带宽**，RC4-MD5 理论上可以跑满 300Mbps 带宽

## 为什么要加密？

1. 网盘里存放了一些个人数据，想要保护个人隐私，杜绝可能的 AI 审查
2. 对文件安全传输有一定的需求，防止云盘扫描删除，有实时播放视频和下载的需求

## 我直接打压缩包不就好了吗？

1. **加密后的文件是密文**，普通软件无法直接打开或识别，杜绝网盘 AI 审查与内容扫描
2. **分块流式处理**，逐块加解密，内存占用恒定，支持任意大小文件
3. **每个文件独立加密**，可选加密文件名，隐私性更强

## 文件加密方式说明

1. **AES-CTR**：更加安全、速度更快，推荐在支持 AES 指令集（AES-NI）的 CPU 上使用
2. **RC4-MD5**：纯算法实现、兼容性更好，适合在不支持 AES 指令集的低端设备上使用
3. **加密文件需要正确密码才能解密**，相同内容使用不同密码加密结果完全不同，请妥善保管密码

## 待做 / TODO

以下功能尚未实现，欢迎参考或自行补充：

- [ ] **自带解密播放端**：实现本地/命令行边下边播，目前仅支持整文件解密到磁盘（无播放端）
- [ ] **流式随机访问解密**：当前为逐块顺序解密，尚未实现任意偏移随机读（如播放进度拖拽）
- [ ] **可选对齐某闭源网盘格式**：若需配合特定网盘的下载端自动解密，可改为对应的异或（XOR）方案
- [ ] **测试覆盖与 CI**：补充单元测试、加解密往返校验的自动化
- [ ] **批量进度与错误恢复**：目录批量处理时显示进度、跳过损坏文件

## 许可证 / 说明

本项目为基于公开功能描述的学习性复现，代码逻辑参照既有实现，仅供个人研究使用。如需用于其他用途，请遵循原作者的相关许可。
