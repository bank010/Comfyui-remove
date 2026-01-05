import os
import time
import uuid
from datetime import datetime

from ..client_s3 import get_s3_instance
S3_INSTANCE = get_s3_instance()


class SaveVideoFilesS3:
    def __init__(self):
        self.s3_output_dir = os.getenv("S3_OUTPUT_DIR")
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "filename_prefix": ("STRING", {"default": "VideoFiles"}),
            "filenames": ("VHS_FILENAMES", ),
            "naming_rule": (["default", "timestamp", "uuid"],),
            "delete_local": (["false", "true"],),
            },
            "optional": {
                "uuid_length": ("INT", {"default": 16, "min": 8, "max": 32, "step": 1}),
            }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_video_paths",)
    FUNCTION = "save_video_files"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "ComfyS3"

    def save_video_files(self, filenames, filename_prefix="VideoFiles", naming_rule="default", delete_local="false", uuid_length=16):
        filename_prefix += self.prefix_append
        local_files = filenames[1]
        full_output_folder, filename, counter, _, filename_prefix = S3_INSTANCE.get_save_path(filename_prefix)
        s3_video_paths = list()
        
        # 视频文件扩展名白名单
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.gif'}
        
        # 时间戳/UUID命名规则：获取日期文件夹
        date_folder = None
        if naming_rule in ["timestamp", "uuid"]:
            # 格式：YYYYMMDD
            date_folder = datetime.now().strftime("%Y%m%d")
        
        for idx, path in enumerate(local_files):
            # 获取文件扩展名
            file_ext = os.path.splitext(path)[1].lower()
            
            # 只处理视频文件，跳过图片等其他文件
            if file_ext not in video_extensions:
                print(f"⏭️  跳过非视频文件: {os.path.basename(path)} (扩展名: {file_ext})")
                # 如果设置了删除本地文件，也删除跳过的图片文件
                if delete_local == "true" and os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"   已删除本地图片文件: {path}")
                    except Exception as e:
                        print(f"   删除本地图片文件失败: {str(e)}")
                continue
            
            ext = file_ext.lstrip('.')  # 移除开头的点
            
            # 生成文件名
            if naming_rule == "timestamp":
                # 时间戳命名规则：timestamp_draw.ext
                timestamp = int(time.time() * 1000)  # 毫秒时间戳
                file = f"{timestamp}_draw.{ext}"
                # 多个视频时添加小延迟，避免时间戳重复
                if len(local_files) > 1 and idx < len(local_files) - 1:
                    time.sleep(0.001)
                # S3 路径：video/generate/draw/date/filename
                full_output_folder = f"video/generate/draw/{date_folder}"
            elif naming_rule == "uuid":
                # UUID命名规则：uuid.ext
                unique_id = str(uuid.uuid4()).replace('-', '')[:uuid_length]
                file = f"{unique_id}.{ext}"
                # S3 路径：video/generate/draw/date/filename
                full_output_folder = f"video/generate/draw/{date_folder}"
            else:
                # 默认格式：前缀_计数器_.扩展名
                file = f"{filename}_{counter:05}_.{ext}"
            
            # Upload the local file to S3
            s3_path = os.path.join(full_output_folder, file)
            
            file_path = S3_INSTANCE.upload_file(path, s3_path)
              
            # Only process if upload was successful (file_path is returned)
            if file_path:
                # Add the s3 path to the s3_video_paths list
                s3_video_paths.append(file_path)
                
                # Log successful upload
                print(f"✅ 已上传视频到 S3: {file_path}")
                
                # Delete local file after successful upload if delete_local is true
                if delete_local == "true" and os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"   已删除本地视频文件: {path}")
                    except Exception as e:
                        print(f"   删除本地视频文件失败: {str(e)}")
            else:
                print(f"❌ 上传视频文件失败，未删除本地文件: {path}")
            
            counter += 1
        
        return (s3_video_paths,)
