import os
import shutil
from moviepy.editor import VideoFileClip, vfx

def process_videos(input_folder, output_folder):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    
    for root, dirs, files in os.walk(input_folder):
        # Skip processing the output folder
        
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_folder, relative_path)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, file)
                
                try:
                    with VideoFileClip(input_path) as clip:
                        duration = clip.duration
                        
                        if duration > 15:
                            # Calculate speed multiplier
                            speed_factor = duration / 15
                            # Speed up the entire video
                            processed_clip = clip.fx(vfx.speedx, speed_factor)
                            # Write processed video
                            processed_clip.write_videofile(
                                output_path,
                                codec='libx264',
                                audio_codec='aac',
                                logger=None,
                                threads=4  # Use multiple threads for faster processing
                            )
                            action = f"SPED UP {speed_factor:.1f}x (Original: {duration:.1f}s)"
                        else:
                            # Copy original if under 25s
                            shutil.copy(input_path, output_path)
                            action = f"COPIED (Original: {duration:.1f}s)"
                            
                        print(f"{action: <45} | {file}")
                        if 'processed_clip' in locals():
                            processed_clip.close()
                        clip.close()
                        
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
             

if __name__ == "__main__":
    input_folder = "./havid_sub_videos_crop/rh_v0/train"
    output_folder = "./havid_sub_videos_crop_shorten/rh_v0/train"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    print("\nProcessing videos...")
    print("Action".ljust(35), "| File")
    print("-" * 80)
    process_videos(input_folder, output_folder)
    print("\nProcessing complete! Check the 'processed_videos' folder.")