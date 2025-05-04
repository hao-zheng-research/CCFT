import os
import json
import re

def load_object_mapping(file_path):
    """
    Reads a file where each line has the format:
        XX "semantic name"
    For example:
        ba "ball"
        bs "ball seat"

    Returns a dictionary mapping:
        {"ba": "ball", "bs": "ball seat", ...}
    """
    mapping = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Split into code and name (strip quotes from name)
            code, name = line.split(" ", 1)
            name = name.strip().strip('"')
            mapping[code] = name
    return mapping

def map_label_with_semantics(label_element, mapping_file):
    # Handle special cases
    if label_element == "null":
        return "null"
    elif label_element == "wrong":
        return "wrong"

    # Map codes to semantic names (if a code isn't found, fallback to the raw code)
    semantics = mapping_file.get(label_element, label_element)

    return semantics

def parse_label(label):
    """
    Splits a label into four elements according to these rules:
      - If the label == "null": all four elements are None.
      - If the label == "wrong": all four elements are "wrong".
      - Otherwise:
          * action_verb         = label[0]
          * manipulated_object  = label[1:3]
          * target_object       = label[3:5]
          * tool               = label[5:7]

    Returns a tuple: (action_verb, manipulated_object, target_object, tool).
    """
    # Special cases
    if label == "null":
        return ("None", "None", "None", "None")
    elif label == "wrong":
        return ("wrong", "None", "None", "None")

    # General parsing
    action_verb         = label[0]     if len(label) >= 1 else "None"
    manipulated_object  = label[1:3]   if len(label) >= 3 else "None"
    target_object       = label[3:5]   if len(label) >= 5 else "None"
    tool                = label[5:7]   if len(label) >= 7 else "None"

    return (action_verb, manipulated_object, target_object, tool)

def read_annotation_file(label, action_verb_mapping, object_mapping, tool_mapping, label_mapping):
    """
    Placeholder function to read a single annotation file and extract the relevant data.
    In your final version, this will parse the file content and return what you need 
    for the JSON structure (e.g., user question, assistant answer, etc.).
    """
    # TODO: Implement your logic to read the annotation file
    # Example (placeholder):
    user_text = "<video>What assembly primitive task did the worker's left hand perform in the video?"
    
    assistant_text_general = ("This video demonstrates a worker performing a critical assembly step. Although the assembly task is bimanual, the user asked me to focus on the worker's left hand."
                              "Therefore, I will describe the primitive assembly task performed by the worker's left hand." 
                              "I will describe the primitive task in a structured way, using four elements: an action verb, a manipulated object, a target object, and a tool. However, the primitive task is not necessary to include all four elements. \n")
    
    action_elements = parse_label(label)
    action_verb = map_label_with_semantics(action_elements[0], action_verb_mapping)
    manipulated_object = map_label_with_semantics(action_elements[1], object_mapping)
    target_object = map_label_with_semantics(action_elements[2], object_mapping)
    tool = map_label_with_semantics(action_elements[3], tool_mapping)
    semantics = map_label_with_semantics(label, label_mapping)
    
    if label == "null":
        description = f"Below is the primitive task performed by the worker's left hand:\n- Action verb: \"{action_verb}\"\n- Manipulated object: \"{manipulated_object}\"\n- Target object: \"{target_object}\"\n- Tool: \"{tool}\"\n\nConclusion: The left hand of the worker did nothing related to the assembly task. \n "
    elif label == "wrong":
        description =  f"Below is the primitive task performed by the worker's left hand:\n- Action verb: \"{action_verb}\"\n- Manipulated object: \"{manipulated_object}\"\n- Target object: \"{target_object}\"\n- Tool: \"{tool}\"\n\nConclusion: The left hand of the worker made a mistake. \n"
    else:
        description = f"Below is the primitive task performed by the worker's left hand:\n- Action verb: \"{action_verb}\"\n- Manipulated object: \"{manipulated_object}\"\n- Target object: \"{target_object}\"\n- Tool: \"{tool}\"\n\nConclusion: The left hand of the worker \"{semantics}\". \n"
        #description =  f"The left hand of the worker performed the action verb is {action_verb}; manipulated object is {manipulated_object}; target object is {target_object}; using the tool {tool}. \n"
    
    assistant_text = assistant_text_general + description

    return user_text, assistant_text

def parse_splitted_filename(filename):
    """
    Given a filename like 'S04A04I01M0_label_1.mp4',
    extract:
      - base_name = 'S04A04I01M0'
      - label     = 'label'
      - index     = '1'

    Returns a tuple: (base_name, label, clip_index).
    If the filename doesn't match the expected pattern, handle it gracefully.
    """

    # Remove extension
    name_no_ext, ext = os.path.splitext(filename)
    if ext.lower() != ".mp4":
        return None

    # Example pattern: S04A04I01M0_label_1
    # We'll assume an underscore-based pattern:
    #   <baseName>_<label>_<index>
    # You can adjust the pattern to match your actual filenames.
    parts = name_no_ext.split("_")

    if len(parts) < 3:
        # Filename doesn't match the expected pattern
        return None

    # Re-join everything up to the second-to-last part as base_name
    # (In case the label has underscores, you may need more advanced logic.)
    *base_parts, label, idx_str = parts
    base_name = "_".join(base_parts)

    # Attempt to convert index to integer
    try:
        clip_index = int(idx_str)
    except ValueError:
        clip_index = None

    return (base_name, label, clip_index)

def gather_split_video_annotations(split_videos_folder, action_verb_mapping, object_mapping, tool_mapping, label_mapping):
    """
    Goes through the folder containing your split .mp4 files.
    For each .mp4, parse its name to extract baseName, label, and index.
    Returns a list of annotation dictionaries.
    """
    json_data = []

    for filename in os.listdir(split_videos_folder):
        if filename.lower().endswith(".mp4"):
            parsed = parse_splitted_filename(filename)
            if parsed is not None:
                base_name, label, clip_index = parsed
                # Create the JSON structure for this file
                
                # Read or parse your annotation file
                user_text, assistant_text = read_annotation_file(label, action_verb_mapping, object_mapping, tool_mapping, label_mapping)
                
            # The "videos" field can be derived from the annotation filename
            # or however your naming convention is set
                data_entry = {
                    "messages": [
                        {
                            "content": user_text,
                            "role": "user"
                        },
                        {
                            "content": assistant_text,
                            "role": "assistant"
                        }
                    ],
                    "videos": [
                        # For example: "mllm_demo_data/filename_without_extension.mp4"
                        # Adjust to match your actual naming scheme or folder path
                        "../split_videos/" + os.path.splitext(filename)[0] + ".mp4"
                    ]
                }
            
                json_data.append(data_entry)

    return json_data

def main():
    # 1. Specify your folder of split videos
    split_videos_folder = "./split_videos/lh_v0"
    
    # Load the mapping files for action verb, manipulated object, target object and tool
    action_verb_mapping_file = "./groundTruth/action_verb_mapping.txt"  # <-- Update this path
    action_verb_mapping = load_object_mapping(action_verb_mapping_file)
    object_mapping_file = "./groundTruth/object_mapping.txt"  # <-- Update this path
    object_mapping = load_object_mapping(object_mapping_file)   
    tool_mapping_file = "./groundTruth/tool_mapping.txt"  # <-- Update this path
    tool_mapping = load_object_mapping(tool_mapping_file)
    label_mapping_file = "./groundTruth/label_mapping.txt"  # <-- Update this path
    label_mapping = load_object_mapping(label_mapping_file)

    # 2. Gather annotations
    json_data = gather_split_video_annotations(split_videos_folder, action_verb_mapping, object_mapping, tool_mapping, label_mapping)

    # 3. Write them to a JSON file
    output_json = "./json_split_videos/split_videos_annotations_structured.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Wrote {len(json_data)} annotations to {output_json}.")

if __name__ == "__main__":
    main()
