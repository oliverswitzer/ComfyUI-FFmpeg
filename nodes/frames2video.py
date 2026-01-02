import os
import subprocess
import tempfile
from ..func import get_image_size

class Frames2Video:
 
    # 初始化方法
    def __init__(self): 
        pass 
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "frame_path": ("STRING", {"default": "C:/Users/Desktop",}), 
                "fps": ("FLOAT", {
                    "default": 30, 
                    "min": 1,
                    "max": 120,
                    "step": 1,
                    "display": "number",
                }),
                "video_name": ("STRING", {"default": "new_video"}),
                "output_path": ("STRING", {"default": "C:/Users/Desktop/output"}),
                "device":(["CPU","GPU"],{"default": "CPU",}),
            },
            "optional":{
                "audio_path":("STRING",{"default": "C:/Users/audio.mp3",}),
                }
        }

    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("frame_path","output_path",)
    FUNCTION = "frames2video" 
    OUTPUT_NODE = True
    CATEGORY = "🔥FFmpeg" 

    def frames2video(self,frame_path,fps,video_name,output_path,audio_path,device):
        try:
            frame_path = os.path.abspath(frame_path).strip()
            output_path = os.path.abspath(output_path).strip()
            if audio_path != "":
                audio_path = os.path.abspath(audio_path).strip()
                if not os.path.exists(audio_path):
                    raise ValueError("audio_path："+audio_path+"不存在（audio_path:"+audio_path+" does not exist）")
            if not os.path.exists(frame_path):
                raise ValueError("frame_path："+frame_path+"不存在（frame_path:"+frame_path+" does not exist）")
                
            #判断output_path是否是一个目录
            if not os.path.isdir(output_path):
                raise ValueError("output_path："+output_path+"不是目录（output_path:"+output_path+" is not a directory）")
            
            #output_path =  f"{output_path}\\{video_name}.mp4" # 将输出目录和输出文件名合并为一个输出路径
            output_path =  os.path.join(output_path, f"{video_name}.mp4")
            # 获取输入目录中的所有图像文件
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
            # 获取所有图片并按文件名排序
            images = [os.path.join(frame_path, f) for f in os.listdir(frame_path) if f.endswith(valid_extensions)]
            # 按文件名进行排序
            images.sort()
            
            if len(images) == 0:
                raise FileNotFoundError("目录："+frame_path+"中没有图片文件（No image files found in directory："+frame_path+"）")

            # 构建ffmpeg命令
            width,height = get_image_size(images[0]);
            
            # Create a temporary file list for FFmpeg concat demuxer
            # This approach works with any filename pattern and handles many images efficiently
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                filelist_path = f.name
                # Write each image path to the file list
                # Format: file 'path' with duration for each frame
                frame_duration = 1.0 / fps
                for img in images:
                    # Normalize path separators for FFmpeg (use forward slashes)
                    img_path = img.replace('\\', '/')
                    # Escape single quotes in the path
                    img_path_escaped = img_path.replace("'", "'\\''")
                    f.write(f"file '{img_path_escaped}'\n")
                    f.write(f"duration {frame_duration}\n")
                # Add the last frame again without duration to ensure it's displayed
                if images:
                    last_img = images[-1].replace('\\', '/').replace("'", "'\\''")
                    f.write(f"file '{last_img}'\n")
            
            try:
                # Build FFmpeg command using concat demuxer
                cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path]
                
                # Add audio if provided
                if audio_path != '':
                    cmd.extend(['-i', audio_path])
                    cmd.append('-shortest')
                
                # Add video filter for scaling
                cmd.extend(['-vf', f'scale={width}:{height}'])
                
                # Add video encoding options
                if device == "CPU":
                    cmd.extend(['-c:v', 'libx264', '-crf', '28'])
                else:
                    cmd.extend(['-c:v', 'h264_nvenc', '-preset', 'fast', '-cq', '22'])
                
                # Add audio codec if audio is provided
                if audio_path != '':
                    cmd.extend(['-c:a', 'aac'])
                
                cmd.extend(['-pix_fmt', 'yuv420p', '-y', str(output_path)])
                
                # 执行ffmpeg命令
                result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if result.returncode != 0:
                    # 如果有错误，输出错误信息
                     print(f"Error: {result.stderr.decode('utf-8')}")
                     raise ValueError(f"Error: {result.stderr.decode('utf-8')}")
                else:
                    # 输出标准输出信息
                    print(result.stdout)
            finally:
                # Clean up temporary file list
                try:
                    os.unlink(filelist_path)
                except:
                    pass
            
            frame_path = str(frame_path) # 输出路径为字符串
            return (frame_path,output_path)
        except Exception as e:
            raise ValueError(e)