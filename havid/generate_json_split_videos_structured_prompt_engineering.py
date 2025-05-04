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
    user_text = "<video>What assembly primitive task did the worker's left hand perform in the video?\n"
    valid_classes = """\n- Action verbs: ["insert", "slide", "place", "rotate", "screw", "wrong", "none"]\n
                    - Manipulated objects: ["ball", "assembly box", "ball seat", "cylinder base", "cylinder cap", "cylinder bracket", "cylinder subassembly", "gear shaft", "large gear", "small gear", "bar", "rod", "large placer", "small placer", "screw bolt", "hex screw", "Phillips screw", "usb male", "linear bearing", "worm gear", "hand wheel", "quarter-turn handle", "hand dial", "nut", "screw bolt", "none"]\n
                    - Target objects: ["ball", "assembly box", "cylinder base", "ball seat", "cylinder bracket", "cylinder cap", "large gear", "gear shaft", "hole for the rod", "hole for the bar", "hole for the bolt", "hole for the Phillips screw", "stud on the assembly box", "usb female", "screw hole C1", "screw hole C2", "screw hole C3", "screw hole C4", "worm gear", "hole for the large gear", "hole for the small gear", "hole for the worm gear", "screw bolt", "nut", "none"]\n
                    - Tools: ["hex screwdriver", "Phillips screwdriver", "shaft wrench", "nut wrench", "none"]\n
                    - Primitive tasks: ["insert the ball into the cylinder base", "insert the ball seat into the cylinder base", "insert the cylinder cap into the cylinder bracket", "insert the cylinder bracket into the cylinder base", "insert the large gear into the gear shaft", "insert the small gear into the gear shaft", "insert the bar into the hole for the bar", "insert the rod into the hole for the rod", "insert the large placer into the gear shaft", "insert the small placer into the gear shaft", "insert the screw bolt into the hole for the bolt", "insert the hex screw into the screw hole C1", "insert the hex screw into the screw hole C2", "insert the hex screw into the screw hole C3", "insert the hex screw into the screw hole C4", "insert the hex screw into the cyliner bracket", "insert the Phillips screw into the worm gear", "insert the usb male into the usb female", "insert the cylinder base into the ball seat", "insert the cylinder base into the cylinder bracket", "insert the cylinder cap into the cylinder base", "insert the cylinder bracket into the cylinder cap", "insert the gear shaft into the large gear", "insert the Phillips screw into the hole for the worm gear", "insert the Phillips screw into the hole for the Phillips screw", "slide the cylinder bracket", "slide the linear bearing", "place the cylinder base onto the assembly box", "place the cylinder bracket onto the assembly box", "place the worm gear onto the assembly box", "place the ball onto the ball seat", "place the ball seat onto the ball", "place the ball seat onto the assembly box", "place the ball seat on to the cylinder cap", "place the assembly box onto the desk", "place the cylinder cap onto the desk", "place the cylinder bracket onto the desk", "place the cylinder bracket onto the cylinder base", "place the cyinder subassembly onto the box", "place the large placer onto the large gear", "rotate the worm gear", "rotate the hand dial", "rotate the quarter-turn handle", "rotate the hand wheel", "screw the cylinder cap onto the cylinder base", "screw the gear shaft onto the hole for large gear", "screw the gear shaft onto the hole for large gear using the shaft wrench", "screw the gear shaft onto the hole for small gear", "screw the gear shaft onto the hole for small gear using the shaft wrench", "screw the nut onto the gear shaft", "screw the nut onto the gear shaft using the nut wrench", "screw the nut onto the stud on the assembly box", "screw the nut onto the stud on the assembly box using the nut wrench", "screw the nut onto the screw bolt", "screw the nut onto the screw bolt using the nut wrench", "screw the screw bolt onto the nut", "screw the hex screw into the screw hole C1", "screw the hex screw into the screw hole C1 using the hex screwdriver", "screw the hex screw into the screw hole C1 uing a Phillips screwdriver", "screw the hex screw into the screw hole C2", "screw the hex screw into the screw hole C2 using the hex screwdriver", "screw the hex screw into the screw hole C2 using the Phillips screwdriver", "screw the hex screw into the screw hole C3", "screw the hex screw into the screw hole C3 using the hex screwdriver", "screw the hex screw into the screw hole C3 using the Phillips screwdriver", "screw the hex screw into the screw hole C4", "screw the hex screw into the screw hole C4 using the hex screwdriver", "screw the hex screw into the screw hole C4 using the Phillips screwdriver", "screw the Phillips screw into the hole for worm gear", "screw the Phillips screw into the hole for worm gear using the Phillips screwdriver", "screw the Phillips screw into the hole for Phillips screw", "screw the Phillips screw into the hole for Phillips screw using the Phillips screwdriver", "screw the cylinder base into the cylinder cap"]\n"""
                    
    user_text = user_text + valid_classes
    
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
    output_json = "./json_split_videos/split_videos_annotations_structured_prompt_engineering.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Wrote {len(json_data)} annotations to {output_json}.")

if __name__ == "__main__":
    main()
