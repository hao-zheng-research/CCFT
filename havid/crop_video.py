import cv2
import os

# Configuration (Modify these as needed)
INPUT_DIR = './split_videos_no_w/lh_v0'          # Folder containing videos
OUTPUT_DIR = './cropped_videos/lh_v0'      # Folder to save cropped videos
CROP_X = 350                                # Starting x-coordinate
CROP_Y = 120                                # Starting y-coordinate
CROP_WIDTH = 550                            # Width of crop region
CROP_HEIGHT = 550                           # Height of crop region

def crop_videos():
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
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
        output_filename = f"{os.path.splitext(filename)[0]}_cropped.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        out = cv2.VideoWriter(output_path, fourcc, fps, (CROP_WIDTH, CROP_HEIGHT))
        
        # Process each frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Crop the frame
            cropped_frame = frame[
                CROP_Y:CROP_Y + CROP_HEIGHT,
                CROP_X:CROP_X + CROP_WIDTH
            ]
            out.write(cropped_frame)
        
        # Release resources
        cap.release()
        out.release()
        print(f"Processed {filename} - Cropped video saved as {output_filename}")

if __name__ == "__main__":
    crop_videos()