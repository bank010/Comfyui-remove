import os
import json
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
            "delete_local": (["false", "true"],),
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

    def save_images(self, images, filename_prefix="ComfyUI", delete_local="false", prompt=None, extra_pnginfo=None):
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
        
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))
            
            file = f"{filename}_{counter:05}_.png"
            
            # Save to local output folder
            local_file_path = os.path.join(local_output_folder, file)
            img.save(local_file_path, pnginfo=metadata, compress_level=self.compress_level)
            
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
                    "subfolder": subfolder,
                    "type": self.type
                })
                
                # Delete local file after successful upload if delete_local is true
                if delete_local == "true" and os.path.exists(local_file_path):
                    try:
                        os.remove(local_file_path)
                        print(f"已删除本地图片文件: {local_file_path}")
                    except Exception as e:
                        print(f"删除本地图片文件失败 {local_file_path}: {str(e)}")
            else:
                print(f"上传图片文件失败，未删除本地文件: {local_file_path}")
            
            counter += 1

        return { "ui": { "images": results },  "result": (s3_image_paths,) }
