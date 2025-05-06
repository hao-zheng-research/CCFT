import os
import cv2

def parse_annotation_file(annotation_path):
    """
    Reads an annotation file where each line is a label
    for one frame (e.g., lines[i] is the label of frame i).
    Groups consecutive identical labels into segments:
        (start_frame, end_frame, label)
    Returns a list of these segments.
    """
    with open(annotation_path, "r", encoding="utf-8") as f:
        labels = [line.strip() for line in f]

    if not labels:
        return []

    segments = []
    current_label = labels[0]
    start_frame = 0

    for frame_idx in range(1, len(labels)):
        if labels[frame_idx] != current_label:
            # Close off the previous segment
            segments.append((start_frame, frame_idx - 1, current_label))
            # Start a new segment
            current_label = labels[frame_idx]
            start_frame = frame_idx

    # Add the final segment
    segments.append((start_frame, len(labels) - 1, current_label))

    return segments

def extract_clips_from_video(video_path, segments, output_folder, base_name):
    """
    Given a video and a list of segments (start_frame, end_frame, label),
    create separate small videos for each segment in the output_folder.
    Naming convention: baseName_label_index.mp4
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    for idx, (start_frame, end_frame, label) in enumerate(segments):
        # Construct output filename
        clip_filename = f"{base_name}_{label}_{idx}.mp4"
        clip_path = os.path.join(output_folder, clip_filename)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Adjust if needed
        out = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))

        # Move video capture position to start_frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Write frames from start_frame to end_frame (inclusive)
        current_frame = start_frame
        while current_frame <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            current_frame += 1

        out.release()
        print(f"Saved clip: {clip_filename}, frames [{start_frame}..{end_frame}], label={label}")

    cap.release()

def split_videos_by_annotations(annotation_folder, video_folder, output_folder):
    """
    1. For each .txt annotation file in annotation_folder:
       - Build its base name (file without extension).
       - Find a matching .mp4 video in video_folder with the same base name.
       - Parse the annotation to get segments (start_frame, end_frame, label).
       - Split the video into small clips according to these segments.
    2. Save the clips to output_folder, with naming convention:
         baseName_label_index.mp4
    """

    os.makedirs(output_folder, exist_ok=True)

    for ann_filename in os.listdir(annotation_folder):
        if not ann_filename.endswith(".txt"):
            continue

        annotation_path = os.path.join(annotation_folder, ann_filename)
        base_name = os.path.splitext(ann_filename)[0]
        video_filename = base_name + ".mp4"
        video_path = os.path.join(video_folder, video_filename)

        if not os.path.exists(video_path):
            print(f"[WARNING] No matching .mp4 for annotation: {ann_filename}")
            continue

        # Parse annotation into segments
        segments = parse_annotation_file(annotation_path)
        if not segments:
            print(f"[WARNING] No frames in annotation: {ann_filename}")
            continue

        # Extract clips from the video
        extract_clips_from_video(video_path, segments, output_folder, base_name)

def main():
    # Change these paths to match your setup
    annotation_folder = "./groundTruth/View0/lh_pt"
    video_folder = "./trimmed_videos"
    output_folder = "./split_videos/lh_v0"

    split_videos_by_annotations(annotation_folder, video_folder, output_folder)

if __name__ == "__main__":
    main()
