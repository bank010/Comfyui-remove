import os
from ..client_s3 import get_s3_instance
S3_INSTANCE = get_s3_instance()


class UploadFileS3:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":{
                "s3_filename": ("STRING", {"default": ""}),
                "local_path": ("STRING", {"default": "input/example.png"}),
                "s3_folder": ("STRING", {"default": "output"}),
                "delete_local": (["false", "true"],),
            }
        }

    CATEGORY = "ComfyS3"
    INPUT_NODE = True
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_paths",)
    FUNCTION = "upload_file_s3"

    def upload_file_s3(self, local_path, s3_folder, delete_local, s3_filename):
        if isinstance(local_path, str):
            local_path = [local_path]
        s3_paths = []
        for path in local_path:
            f_name = s3_filename if s3_filename else os.path.basename(path)
            s3_path = os.path.join(s3_folder, f_name)
            file_path = S3_INSTANCE.upload_file(path, s3_path)
            
            # Only delete local file if upload was successful (file_path is returned)
            if file_path:
                s3_paths.append(file_path)
                
                # Log successful upload
                print(f"✅ 已上传文件到 S3: {file_path}")
                
                if delete_local == "true" and os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"   已删除本地文件: {path}")
                    except Exception as e:
                        print(f"   删除本地文件失败: {str(e)}")
            else:
                print(f"❌ 上传失败，未删除本地文件: {path}")
        
        return { "ui": { "s3_paths": s3_paths },  "result": (s3_paths,) }