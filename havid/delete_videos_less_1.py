import os
import cv2

def delete_short_videos(folder_path, max_frames=15):
    deleted_videos = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')):
            file_path = os.path.join(folder_path, filename)

            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                print(f"Could not open video: {filename}")
                continue

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()

            if frame_count < max_frames:
                deleted_videos.append((filename, frame_count))
                # try:
                #     os.remove(file_path)
                #     deleted_videos.append((filename, frame_count))
                #     print(f"Deleted: {filename} ({frame_count} frames)")
                # except Exception as e:
                #     print(f"Failed to delete {filename}: {e}")

    return deleted_videos

# Example usage:
folder = "cropped_videos/lh_v0"  # Change this to your folder path
results = delete_short_videos(folder)

print("Videos with less than 15 frames:")
print("Total number of the short videos: ", len(results))
for video, frame_count in results:
    print(f"{video}: {frame_count} frames")
