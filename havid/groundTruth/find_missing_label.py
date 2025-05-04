import sys

def read_labels(filename):
    """Read labels from a file and return them as a set."""
    with open(filename, 'r') as f:
        return set(line.strip() for line in f)

def main():
    #if len(sys.argv) != 3:
    #    print("Usage: python find_unique_labels.py file1.txt file2.txt")
    #    sys.exit(1)
    
    #file1, file2 = sys.argv[1], sys.argv[2]
    
    file1 = './unique_labels.txt'
    file2 = './pt_unique_labels.txt'
    
    # Read labels from both files
    set1 = read_labels(file1)
    set2 = read_labels(file2)
    
    # Find labels unique to each file
    unique_in_file1 = set1 - set2
    unique_in_file2 = set2 - set1
    
    # Combine and sort the results
    all_unique = sorted(unique_in_file1 | unique_in_file2)
    
    # Print the results
    print("Labels unique to each file:")
    for label in all_unique:
        origin = file1 if label in unique_in_file1 else file2
        print(f"{label} (only in {origin})")

if __name__ == "__main__":
    main()