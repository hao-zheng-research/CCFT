import os
import cv2

def check_annotations_and_videos(annotation_folder, video_folder):
    """
    For each .txt annotation file in annotation_folder:
      1. Find the matching .mp4 video in video_folder
      2. Count the lines in the annotation file
      3. Count the frames in the video
      4. If (frames_in_video - lines_in_annotation) != 10, print the difference
    """

    for annotation_filename in os.listdir(annotation_folder):
        # Only process .txt files
        if not annotation_filename.endswith(".txt"):
            continue

        # Build full path to the annotation file
        annotation_path = os.path.join(annotation_folder, annotation_filename)
        
        # Read all lines to get annotation length
        with open(annotation_path, "r", encoding="utf-8") as f:
            annotation_lines = f.readlines()
            annotation_length = len(annotation_lines)

        # Construct the expected video filename (replace .txt with .mp4)
        base_name = os.path.splitext(annotation_filename)[0]
        video_filename = base_name + ".mp4"
        video_path = os.path.join(video_folder, video_filename)

        # If the video doesn't exist, skip or notify
        if not os.path.exists(video_path):
            print(f"[WARNING] No matching video found for annotation: {annotation_filename}")
            continue

        # Read frame count using OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[ERROR] Unable to open video: {video_filename}")
            continue
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # Compute difference
        difference = frame_count - annotation_length
        
        #print(f"{frame_count}, {annotation_length}")

        # Check if difference != 10
        if difference != 10:
            print(f"For '{base_name}', frame_count={frame_count}, annotation_length={annotation_length}, difference={difference}")

def main():
    # Update these paths to your actual folders
    annotation_folder = "./groundTruth/View0/lh_pt"
    video_folder = "./videos"

    check_annotations_and_videos(annotation_folder, video_folder)

if __name__ == "__main__":
    main()
