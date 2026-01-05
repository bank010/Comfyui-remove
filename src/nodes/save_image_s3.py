import os
import json
import time
import uuid
from datetime import datetime
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from comfy.cli_args import args

from ..client_s3 import get_s3_instance
S3_INSTANCE = get_s3_instance()


class SaveImageS3:
    def __init__(self):
        self.s3_output_dir = os.getenv("S3_OUTPUT_DIR")
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "images": ("IMAGE", ),
            "filename_prefix": ("STRING", {"default": "Image"}),
            "image_format": (["png", "jpg", "webp"],),
            "naming_rule": (["default", "timestamp", "uuid"],),
            "delete_local": (["false", "true"],),
            },
            "optional": {
                "custom_filename": ("STRING", {"default": ""}),
                "uuid_length": ("INT", {"default": 16, "min": 8, "max": 32, "step": 1}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
                }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_image_paths",)
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "ComfyS3"

    def save_images(self, images, filename_prefix="ComfyUI", image_format="png", naming_rule="default", delete_local="false", custom_filename="", uuid_length=16, prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = S3_INSTANCE.get_save_path(filename_prefix, images[0].shape[1], images[0].shape[0])
        results = list()
        s3_image_paths = list()
        
        # Get local output folder from ComfyUI
        from folder_paths import get_output_directory
        local_output_folder = get_output_directory()
        if subfolder:
            local_output_folder = os.path.join(local_output_folder, subfolder)
        if not os.path.exists(local_output_folder):
            os.makedirs(local_output_folder)
        
        # 图片格式配置
        format_config = {
            "png": {"ext": "png", "save_args": {"pnginfo": None, "compress_level": self.compress_level}},
            "jpg": {"ext": "jpg", "save_args": {"quality": 95, "optimize": True}},
            "webp": {"ext": "webp", "save_args": {"quality": 95, "method": 6}}
        }
        
        config = format_config.get(image_format, format_config["png"])
        ext = config["ext"]
        save_args = config["save_args"].copy()
        
        # 时间戳/UUID命名规则：获取日期文件夹
        date_folder = None
        if naming_rule in ["timestamp", "uuid"]:
            # 格式：YYYYMMDD
            date_folder = datetime.now().strftime("%Y%m%d")
        
        for idx, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # 处理 metadata（仅 PNG 格式支持）
            if image_format == "png" and not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                save_args["pnginfo"] = metadata
            
            # 生成文件名
            if naming_rule == "timestamp":
                # 时间戳命名规则：timestamp_draw.ext
                timestamp = int(time.time() * 1000)  # 毫秒时间戳
                file = f"{timestamp}_draw.{ext}"
                # 多张图片时添加小延迟，避免时间戳重复
                if len(images) > 1 and idx < len(images) - 1:
                    time.sleep(0.001)
                # S3 路径：img/generate/date/filename
                full_output_folder = f"img/generate/{date_folder}"
                # 本地路径也包含日期文件夹
                local_output_folder_with_date = os.path.join(local_output_folder, date_folder)
                if not os.path.exists(local_output_folder_with_date):
                    os.makedirs(local_output_folder_with_date)
                local_file_path = os.path.join(local_output_folder_with_date, file)
            elif naming_rule == "uuid":
                # UUID命名规则：uuid.ext
                unique_id = str(uuid.uuid4()).replace('-', '')[:uuid_length]
                file = f"{unique_id}.{ext}"
                # S3 路径：img/generate/date/filename
                full_output_folder = f"img/generate/{date_folder}"
                # 本地路径也包含日期文件夹
                local_output_folder_with_date = os.path.join(local_output_folder, date_folder)
                if not os.path.exists(local_output_folder_with_date):
                    os.makedirs(local_output_folder_with_date)
                local_file_path = os.path.join(local_output_folder_with_date, file)
            elif custom_filename:
                # 使用自定义文件名
                if len(images) > 1:
                    # 多张图片时添加索引
                    file = f"{custom_filename}_{idx+1}.{ext}"
                else:
                    # 单张图片直接使用自定义文件名
                    file = f"{custom_filename}.{ext}"
                local_file_path = os.path.join(local_output_folder, file)
            else:
                # 使用默认格式：前缀_计数器_.扩展名
                file = f"{filename}_{counter:05}_.{ext}"
                local_file_path = os.path.join(local_output_folder, file)
            
            # Save to local output folder
            img.save(local_file_path, **save_args)
            
            # Upload to S3
            s3_path = os.path.join(full_output_folder, file)
            file_path = S3_INSTANCE.upload_file(local_file_path, s3_path)
            
            # Only process if upload was successful
            if file_path:
                # Add the s3 path to the s3_image_paths list
                s3_image_paths.append(file_path)
                
                # Add the result to the results list
                results.append({
                    "filename": file,
                    "subfolder": subfolder if naming_rule not in ["timestamp", "uuid"] else date_folder,
                    "type": self.type
                })
                
                # Log successful upload
                print(f"✅ 已上传图片到 S3: {file_path}")
                
                # Delete local file after successful upload if delete_local is true
                if delete_local == "true" and os.path.exists(local_file_path):
                    try:
                        os.remove(local_file_path)
                        print(f"   已删除本地图片文件: {local_file_path}")
                    except Exception as e:
                        print(f"   删除本地图片文件失败: {str(e)}")
            else:
                print(f"❌ 上传图片文件失败，未删除本地文件: {local_file_path}")
            
            counter += 1

        return { "ui": { "images": results },  "result": (s3_image_paths,) }
