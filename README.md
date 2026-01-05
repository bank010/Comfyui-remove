# ComfyS3: Amazon S3 Integration for ComfyUI 

> **基于原项目**: 本仓库 Fork 自 [TemryL/ComfyS3](https://github.com/TemryL/ComfyS3)  
> **新增功能**: 添加了上传到 S3 后自动删除本地资源的功能

ComfyS3 seamlessly integrates with [Amazon S3](https://aws.amazon.com/en/s3/) in [ComfyUI](https://github.com/comfyanonymous/ComfyUI). This open-source project provides custom nodes for effortless loading and saving of images, videos, and checkpoint models directly from S3 buckets within the ComfyUI graph interface.

## ✨ 新增功能

- **上传后删除本地文件**: `SaveVideoFilesS3` 和 `UploadFileS3` 节点新增 `delete_local` 参数，支持在成功上传到 S3 后自动删除本地资源文件（图片/视频），节省本地存储空间
- **安全保障**: 只在上传成功后才删除本地文件，避免数据丢失
- **异常处理**: 删除失败不会影响上传流程，确保稳定性

## Installation

### Using ComfyUI Manager:

- Look for ```ComfyS3```, and be sure the author is ```TemryL```. Install it.

### Manually:
- Clone this repo into `custom_nodes` folder in ComfyUI.

### Define S3 Config
Create `.env` file in ComfyS3 root folder with the following variables:

```bash 
S3_REGION = "..."
S3_ACCESS_KEY = "..."
S3_SECRET_KEY = "..."
S3_BUCKET_NAME = "..."
S3_INPUT_DIR = "..."
S3_OUTPUT_DIR = "..."
```

### Optional S3 Config Variables
- ```S3_ENDPOINT_URL``` allows the useage of a AWS Private Link or Other S3 Compatible Storage Solutions
- ```S3_ADDRESSING_STYLE``` allows the useage of different S3 addressing styles: auto/virtual/path, default is auto, useful for S3-Compatible Storage Solutions

## Available Features
ComfyUI nodes to:
- [x] standalone download/upload file from/to Amazon S3
- [x] load/save image from/to Amazon S3 buckets
- [x] save VHS (VideoHelperSuite) video files to Amazon S3 buckets
- [x] **自动删除本地文件**: 上传成功后可选择删除本地资源（新增）
- [x] install ComfyS3 from [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- [ ] load checkpoints from Amazon S3 buckets
- [ ] load video from Amazon S3 buckets

## Credits
- 原项目作者 [TemryL](https://github.com/TemryL) - [ComfyS3](https://github.com/TemryL/ComfyS3)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)
