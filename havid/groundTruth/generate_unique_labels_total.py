import os

def get_unique_labels(folder_path):
    """
    Reads all .txt files in the given folder, collects labels from each line,
    and returns a sorted list of unique labels.
    """
    unique_labels = set()

    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            # Build the full file path
            file_path = os.path.join(folder_path, filename)

            # Read the file and collect labels
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    label = line.strip()  # Remove leading/trailing whitespace
                    if label:             # Only add if it's not an empty string
                        unique_labels.add(label)

    # Return a sorted list
    return sorted(unique_labels)

def main():
    folder_path = "./unique_labels"  # <-- Change this to your folder path
    unique_labels = get_unique_labels(folder_path)

    output_file = "./pt_unique_labels.txt"
    with open(output_file, "w", encoding="utf-8") as out:
        for label in unique_labels:
            out.write(label + "\n")

    print(f"Unique labels have been written to {output_file}.")

if __name__ == "__main__":
    main()
