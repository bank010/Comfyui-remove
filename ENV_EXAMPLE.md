# S3 配置说明

## 创建 .env 文件

在项目根目录创建 `.env` 文件，填写以下配置：

```bash
# 必需配置
S3_REGION=ap-southeast-1
S3_ACCESS_KEY=AKIAXXXXXXXXXXXXXXXX
S3_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
S3_BUCKET_NAME=your-bucket-name
S3_INPUT_DIR=input
S3_OUTPUT_DIR=output

# 可选配置（用于 AWS Private Link 或其他 S3 兼容存储）
# S3_ENDPOINT_URL=https://s3.ap-southeast-1.amazonaws.com
# S3_ADDRESSING_STYLE=auto
```

## 配置说明

### 必需配置

- **S3_REGION**: AWS 区域，例如 `us-east-1`, `ap-southeast-1` 等
- **S3_ACCESS_KEY**: AWS Access Key ID
- **S3_SECRET_KEY**: AWS Secret Access Key
- **S3_BUCKET_NAME**: S3 存储桶名称
- **S3_INPUT_DIR**: 输入文件夹路径（在 bucket 中）
- **S3_OUTPUT_DIR**: 输出文件夹路径（在 bucket 中）

### 可选配置

- **S3_ENDPOINT_URL**: 自定义 S3 端点（用于兼容 MinIO、阿里云 OSS 等）
- **S3_ADDRESSING_STYLE**: S3 地址样式，可选值：
  - `auto`: 自动选择（默认）
  - `virtual`: 虚拟主机样式
  - `path`: 路径样式

## 如何获取 AWS 凭证

1. 登录 [AWS 控制台](https://console.aws.amazon.com/)
2. 进入 IAM（Identity and Access Management）
3. 创建新用户或选择现有用户
4. 生成 Access Key 和 Secret Key
5. 确保用户具有 S3 读写权限

## 测试连接

运行测试脚本验证配置：

```bash
python test_s3_connection.py
```

## 示例配置

### AWS S3
```bash
S3_REGION=us-east-1
S3_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
S3_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=my-comfyui-bucket
S3_INPUT_DIR=input
S3_OUTPUT_DIR=output
```

### MinIO（自建 S3 兼容存储）
```bash
S3_REGION=us-east-1
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=comfyui
S3_INPUT_DIR=input
S3_OUTPUT_DIR=output
S3_ENDPOINT_URL=http://localhost:9000
S3_ADDRESSING_STYLE=path
```

### 阿里云 OSS
```bash
S3_REGION=oss-cn-hangzhou
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET_NAME=your-bucket
S3_INPUT_DIR=input
S3_OUTPUT_DIR=output
S3_ENDPOINT_URL=https://oss-cn-hangzhou.aliyuncs.com
S3_ADDRESSING_STYLE=virtual
```

## 安全提示

⚠️ **重要**: 
- 不要将 `.env` 文件提交到 Git 仓库
- 不要在公开场合分享您的 Access Key 和 Secret Key
- 定期轮换密钥
- 使用 IAM 策略限制权限范围
