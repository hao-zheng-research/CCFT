import cv2
import os

def trim_video(input_folder, output_folder, frames_to_trim=5):
    """
    Trims the first `frames_to_trim` frames and the last `frames_to_trim` frames
    from each .mp4 video in `input_folder`, then saves the trimmed video to
    `output_folder`, preserving the same filename.
    """

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        # Process only files that look like videos (e.g. .mp4)
        if not filename.lower().endswith(".mp4"):
            continue

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # Open the video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"[WARNING] Could not open video: {input_path}")
            continue

        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate the new start and end frames
        start_frame = frames_to_trim
        end_frame   = total_frames - frames_to_trim  # non-inclusive upper bound

        # If the video is too short to trim, skip it (or handle as you wish)
        if end_frame <= start_frame:
            print(f"[WARNING] Video too short to trim: {filename} (frames={total_frames})")
            cap.release()
            continue

        # Set up a VideoWriter to write the trimmed frames
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID', 'avc1', etc.
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        current_frame = 0

        # Read frames in a loop
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Write the frame if it's within our trimming range
            if start_frame <= current_frame < end_frame:
                out.write(frame)

            current_frame += 1

        cap.release()
        out.release()

        print(f"Trimmed {filename}: removed first/last {frames_to_trim} frames.")

def main():
    # Set up your folders
    input_folder = "./videos"
    output_folder = "./trimmed_videos"

    # Call the trimming function
    trim_video(input_folder, output_folder, frames_to_trim=5)

if __name__ == "__main__":
    main()
