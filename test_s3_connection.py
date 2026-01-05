#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3 连接测试脚本
用于验证 S3 配置是否正确
"""

import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 打印配置信息（隐藏敏感信息）
print("=" * 60)
print("正在检查 S3 配置...")
print("=" * 60)

S3_REGION = os.getenv("S3_REGION")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_INPUT_DIR = os.getenv("S3_INPUT_DIR")
S3_OUTPUT_DIR = os.getenv("S3_OUTPUT_DIR")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ADDRESSING_STYLE = os.getenv("S3_ADDRESSING_STYLE", "auto")

# 检查必需配置
print("\n📋 配置检查:")
print(f"  Region:        {S3_REGION or '❌ 未配置'}")
print(f"  Access Key:    {'✅ 已配置' if S3_ACCESS_KEY else '❌ 未配置'}")
print(f"  Secret Key:    {'✅ 已配置' if S3_SECRET_KEY else '❌ 未配置'}")
print(f"  Bucket Name:   {S3_BUCKET_NAME or '❌ 未配置'}")
print(f"  Input Dir:     {S3_INPUT_DIR or '❌ 未配置'}")
print(f"  Output Dir:    {S3_OUTPUT_DIR or '❌ 未配置'}")
print(f"  Endpoint URL:  {S3_ENDPOINT_URL or '(使用默认 AWS)'}")
print(f"  Style:         {S3_ADDRESSING_STYLE}")

if not all([S3_REGION, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_NAME]):
    print("\n❌ 错误: 缺少必需的配置项！")
    print("\n请在项目根目录创建 .env 文件，内容如下：")
    print("-" * 60)
    print("S3_REGION=ap-southeast-1")
    print("S3_ACCESS_KEY=your_access_key")
    print("S3_SECRET_KEY=your_secret_key")
    print("S3_BUCKET_NAME=your_bucket_name")
    print("S3_INPUT_DIR=input")
    print("S3_OUTPUT_DIR=output")
    print("# S3_ENDPOINT_URL=https://xxx  # 可选，用于兼容其他 S3 服务")
    print("-" * 60)
    sys.exit(1)

# 导入 S3 客户端
print("\n🔧 正在初始化 S3 客户端...")
try:
    from src.client_s3 import S3
    
    s3_client = S3(
        region=S3_REGION,
        access_key=S3_ACCESS_KEY,
        secret_key=S3_SECRET_KEY,
        bucket_name=S3_BUCKET_NAME,
        endpoint_url=S3_ENDPOINT_URL
    )
    
    if s3_client.s3_client is None:
        print("❌ S3 客户端初始化失败！")
        sys.exit(1)
    
    print("✅ S3 客户端初始化成功！")
    
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试连接
print("\n🌐 正在测试 S3 连接...")
try:
    # 测试 1: 列出 bucket 中的对象（最多 5 个）
    print(f"\n测试 1: 列出 bucket '{S3_BUCKET_NAME}' 中的前 5 个对象...")
    bucket = s3_client.s3_client.Bucket(S3_BUCKET_NAME)
    objects = list(bucket.objects.limit(5))
    
    if objects:
        print(f"✅ 找到 {len(objects)} 个对象:")
        for obj in objects:
            print(f"   - {obj.key} ({obj.size} bytes)")
    else:
        print("✅ Bucket 存在但为空")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 2: 检查文件夹
print(f"\n测试 2: 检查文件夹是否存在...")
try:
    input_exists = s3_client.does_folder_exist(S3_INPUT_DIR)
    output_exists = s3_client.does_folder_exist(S3_OUTPUT_DIR)
    
    print(f"  Input 文件夹 ({S3_INPUT_DIR}):  {'✅ 存在' if input_exists else '❌ 不存在'}")
    print(f"  Output 文件夹 ({S3_OUTPUT_DIR}): {'✅ 存在' if output_exists else '❌ 不存在'}")
    
except Exception as e:
    print(f"❌ 检查文件夹失败: {e}")

# 测试 3: 创建测试文件并上传
print(f"\n测试 3: 上传测试文件...")
try:
    import tempfile
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file_path = f.name
        f.write(f"ComfyS3 测试文件\n创建时间: {os.popen('date').read()}")
    
    # 上传到 S3
    test_s3_path = os.path.join(S3_OUTPUT_DIR, "test_connection.txt")
    result = s3_client.upload_file(test_file_path, test_s3_path)
    
    if result:
        print(f"✅ 上传成功: {test_s3_path}")
        
        # 测试 4: 下载测试文件
        print(f"\n测试 4: 下载测试文件...")
        download_path = test_file_path + ".download"
        download_result = s3_client.download_file(test_s3_path, download_path)
        
        if download_result and os.path.exists(download_path):
            print(f"✅ 下载成功: {download_path}")
            
            # 清理临时文件
            os.remove(download_path)
            print("✅ 清理临时文件成功")
        else:
            print("❌ 下载失败")
    else:
        print("❌ 上传失败")
    
    # 清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    
except Exception as e:
    print(f"❌ 上传/下载测试失败: {e}")
    import traceback
    traceback.print_exc()

# 总结
print("\n" + "=" * 60)
print("✅ S3 连接测试完成！")
print("=" * 60)
print("\n如果所有测试都通过，说明您的 S3 配置正确。")
print("现在可以在 ComfyUI 中使用 ComfyS3 节点了！\n")
