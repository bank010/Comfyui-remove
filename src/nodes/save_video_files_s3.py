import os

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
            "delete_local": (["false", "true"],),
            }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_video_paths",)
    FUNCTION = "save_video_files"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "ComfyS3"

    def save_video_files(self, filenames, filename_prefix="VideoFiles", delete_local="false"):
        filename_prefix += self.prefix_append
        local_files = filenames[1]
        full_output_folder, filename, counter, _, filename_prefix = S3_INSTANCE.get_save_path(filename_prefix)
        s3_video_paths = list()
        
        for path in local_files:
            ext = path.split(".")[-1]
            file = f"{filename}_{counter:05}_.{ext}"
            
            # Upload the local file to S3
            s3_path = os.path.join(full_output_folder, file)
            
            file_path = S3_INSTANCE.upload_file(path, s3_path)
              
            # Only process if upload was successful (file_path is returned)
            if file_path:
                # Add the s3 path to the s3_video_paths list
                s3_video_paths.append(file_path)
                
                # Delete local file after successful upload if delete_local is true
                if delete_local == "true" and os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"已删除本地视频文件: {path}")
                    except Exception as e:
                        print(f"删除本地视频文件失败 {path}: {str(e)}")
            else:
                print(f"上传视频文件失败，未删除本地文件: {path}")
            
            counter += 1
        
        return (s3_video_paths,)
