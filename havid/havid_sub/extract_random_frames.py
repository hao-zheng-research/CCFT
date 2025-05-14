import cv2
import os
import random

# Configuration (Modify these as needed)
INPUT_DIR = './havid_sub_videos_crop/rh_v0/train'       # Folder containing videos
OUTPUT_DIR = './havid_sub_frames_crop_extend/rh_v0/train'      # Folder to save extracted frames
NUM_EXTRACTS = 5                         # Number of extractions per video
MIN_FRAMES = 5                           # Minimum frames to extract per extraction
MAX_FRAMES = 15                          # Maximum frames to extract per extraction

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
        if total_frames < MIN_FRAMES:
            print(f"Skipping {filename} (only {total_frames} frames, less than {MIN_FRAMES})")
            cap.release()
            continue
        
        video_name = os.path.splitext(filename)[0]
        
        # Perform multiple extractions per video
        for extract_idx in range(NUM_EXTRACTS):
            # Randomly determine the number of frames to extract
            num_to_extract = random.randint(MIN_FRAMES, MAX_FRAMES)
            actual_extract = min(num_to_extract, total_frames)
            
            # Generate sorted random frame indices
            try:
                indices = sorted(random.sample(range(total_frames), actual_extract))
            except ValueError as e:
                print(f"Error sampling frames for {filename}: {e}")
                continue
            
            # Extract frames for this extraction
            for frame_idx, frame_number in enumerate(indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()
                
                if ret:
                    output_path = os.path.join(
                        OUTPUT_DIR,
                        f"{video_name}_{extract_idx}_{frame_idx}.jpg"
                    )
                    cv2.imwrite(output_path, frame)
                else:
                    print(f"Failed to read frame {frame_number} from {filename} in extraction {extract_idx}")
        
        cap.release()
        print(f"Processed {filename} - Completed {NUM_EXTRACTS} extractions")

if __name__ == "__main__":
    extract_frames()