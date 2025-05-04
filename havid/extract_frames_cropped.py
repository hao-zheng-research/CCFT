import cv2
import os

# Configuration (Modify these as needed)
INPUT_DIR = './split_videos/lh_v0'          # Folder containing videos
OUTPUT_DIR = './frames_cropped/lh_v0' # Folder to save extracted frames
NUM_FRAMES = 5                # Number of frames to extract per video

# Crop configuration (coordinates of top-left corner and dimensions)
CROP_X = 350                                # Starting x-coordinate
CROP_Y = 120                                 # Starting y-coordinate
CROP_WIDTH = 550                            # Width of crop region
CROP_HEIGHT = 550                           # Height of crop region

def extract_frames():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Supported video file extensions
    VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
    
    # Process each file in input directory
    for filename in os.listdir(INPUT_DIR):
        # Check if file is a video
        ext = filename.split('.')[-1].lower()
        if ext not in VIDEO_EXTENSIONS:
            continue
        
        video_path = os.path.join(INPUT_DIR, filename)
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error opening video: {filename}")
            continue
        
        # Get total frames in video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            print(f"Skipping {filename} (0 frames detected)")
            cap.release()
            continue
        
        # Calculate number of frames to extract
        num_to_extract = min(NUM_FRAMES, total_frames)
        
        # Generate frame indices to extract
        if num_to_extract == 1:
            indices = [0]
        else:
            indices = [(i * (total_frames - 1)) // (num_to_extract - 1) 
                      for i in range(num_to_extract)]
        
        # Extract frames
        video_name = os.path.splitext(filename)[0]
        for frame_idx, frame_number in enumerate(indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            if ret:
                cropped_frame = frame[
                    CROP_Y:CROP_Y+CROP_HEIGHT,
                    CROP_X:CROP_X+CROP_WIDTH
                ]
                
                output_path = os.path.join(
                    OUTPUT_DIR,
                    f"{video_name}_{frame_idx}.jpg"
                )
                cv2.imwrite(output_path, cropped_frame)
            else:
                print(f"Failed to read frame {frame_number} from {filename}")
        
        cap.release()
        print(f"Processed {filename} - Extracted {len(indices)} frames")

if __name__ == "__main__":
    extract_frames()