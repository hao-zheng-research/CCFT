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
        return ("null", "null", "null", "null")
    elif label == "wrong":
        return ("wrong", "wrong", "wrong", "wrong")

    # General parsing
    action_verb         = label[0]     if len(label) >= 1 else "null"
    manipulated_object  = label[1:3]   if len(label) >= 3 else "null"
    target_object       = label[3:5]   if len(label) >= 5 else "null"
    tool                = label[5:7]   if len(label) >= 7 else "null"

    return (action_verb, manipulated_object, target_object, tool)

def read_annotation_file(label, action_verb_mapping, object_mapping, tool_mapping, label_mapping):
    """
    Placeholder function to read a single annotation file and extract the relevant data.
    In your final version, this will parse the file content and return what you need 
    for the JSON structure (e.g., user question, assistant answer, etc.).
    """
    # TODO: Implement your logic to read the annotation file
    # Example (placeholder):
    
    user_text = {}
    assistant_text_lh = {}
    
    action_elements = parse_label(label)
    action_verb = map_label_with_semantics(action_elements[0], action_verb_mapping)
    manipulated_object = map_label_with_semantics(action_elements[1], object_mapping)
    target_object = map_label_with_semantics(action_elements[2], object_mapping)
    tool = map_label_with_semantics(action_elements[3], tool_mapping)
    semantics = map_label_with_semantics(label, label_mapping)
    
    user_text["verb"] = "<video>What is the action verb of the assembly action that the worker's left hand perform in the video?"
    user_text["manipulated_object"] = "<video>What is the manipulated object that the worker's left hand is interacting with?"
    user_text["target_object"] = "<video>What is the target object that the worker's left hand is assembling the manipulated object onto?"
    user_text["tool"] = "<video>What is the tool that the worker's left hand is using in the video?"
    user_text["complete"] = "<video>What assembly primitive task did the worker's left hand perform in the video?"
    
    assistant_text_lh_cap = "I will describe the primitive task in a structured way, using four elements: an action verb, a manipulated object, a target object, and a tool. However, the primitive task is not necessary to include all four elements. \n"
    
    if label == "null":
        assistant_text_lh["verb"] = "Observing the motion of the worker's left hand, the left hand of the worker did nothing related to the assembly task. \n "
        assistant_text_lh["manipulated_object"] = "Observing the object that the worker's left hand is manipulating, the left hand of the worker did nothing related to the assembly task. \n "
        assistant_text_lh["target_object"] = "Observing the object that the worker's left hand is assembling the manipulated object onto, the left hand of the worker did nothing related to the assembly task. \n "
        assistant_text_lh["tool"] = "Observing the tool that the worker's left hand is using, the left hand of the worker did nothing related to the assembly task. \n "
        assistant_text_lh["complete"] = assistant_text_lh_cap + "Observing the assembly task the worker's left hand perform in the video, the left hand of the worker did nothing related to the assembly task. \n "    
    elif label == "wrong":
        assistant_text_lh["verb"] =  "Observing the motion of the worker's left hand, the left hand of the worker made a mistake. \n"
        assistant_text_lh["manipulated_object"] =  "Observing the object that the worker's left hand is manipulating, the left hand of the worker made a mistake. \n"
        assistant_text_lh["target_object"] =  "Observing the object that the worker's left hand is assembling the manipulated object onto, the left hand of the worker made a mistake. \n"
        assistant_text_lh["tool"] =  "Observing the tool that the worker's left hand is using, the left hand of the worker made a mistake. \n"
        assistant_text_lh["complete"] = assistant_text_lh_cap + "Observing the assembly task the worker's left hand perform in the video, the left hand of the worker made a mistake. \n "
    else:
        assistant_text_lh["verb"] = f"Observing the motion of the worker's left hand, the assembly action verb is {{{action_verb}}}. "
        assistant_text_lh["manipulated_object"] = f"Observing the object that the worker's left hand is manipulating, the manipulated object is {{{manipulated_object}}}. "
        assistant_text_lh["target_object"] = f"Observing the object that the worker's left hand is assembling the manipulated object onto, the target object is {{{target_object}}}. "
        assistant_text_lh["tool"] = f"Observing the tool that the worker's left hand is using, the tool is {{{tool}}}. "
        assistant_text_lh["complete"] = assistant_text_lh_cap + f"Observing the assembly task the worker's left hand perform in the video, the assembly primitive task is {{{semantics}}}. \n"

    return user_text, assistant_text_lh

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
                            "content": user_text["verb"],
                            "role": "user"
                        },
                        {
                            "content": assistant_text["verb"],
                            "role": "assistant"
                        },
                        {
                            "content": user_text["manipulated_object"],
                            "role": "user"
                        },
                        {
                            "content": assistant_text["manipulated_object"],
                            "role": "assistant"
                        },
                        {
                            "content": user_text["target_object"],
                            "role": "user"
                        },
                        {
                            "content": assistant_text["target_object"],
                            "role": "assistant"
                        },
                        {
                            "content": user_text["tool"],
                            "role": "user"
                        },
                        {
                            "content": assistant_text["tool"],
                            "role": "assistant"
                        },
                        {
                            "content": user_text["complete"],
                            "role": "user"
                        },
                        {
                            "content": assistant_text["complete"],
                            "role": "assistant"
                        },
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
    output_json = "./json_split_videos/split_videos_annotations_split_QA.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Wrote {len(json_data)} annotations to {output_json}.")

if __name__ == "__main__":
    main()
