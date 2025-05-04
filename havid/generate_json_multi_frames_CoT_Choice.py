import os
import json
import re
from collections import defaultdict

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
    # Create a list of (code, description) pairs with line numbers
    indexed_mapping = {code: (desc, idx) for idx, (code, desc) in enumerate(mapping_file.items())}
    
    # Get both semantics and line index
    semantics, line_index = indexed_mapping.get(label_element, (label_element, -1)) 
    
    # Handle special cases
    if label_element == "null":
        semantics = "null"
    elif label_element == "wrong":
        semantics = "wrong"

    return semantics, line_index

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
    user_text = "<image>\nWhat is the assembly primitive task that the worker's left hand is performing in the video?\n" 
    
    # user_text = user_text + """Analyze the assembly primitive task being performed by the worker's left hand in this frame through systematic observation:  
    #                             \n1. Examine the spatial relationship between hand posture and tools/components  
    #                             \n2. Identify assembly parts in direct contact with the hand  
    #                             \n3. Analyze biomechanical characteristics of the motion  
    #                             \n4. Consider contextual workshop elements  
    #                             \nBased on the observation, describe the primitive task in a structured way, using four elements: an action verb, a manipulated object, a target object, and a tool.\n"""
    
    valid_classes = """Possible classes for each action element and primitive task are the following:\n- Action verbs: ["insert", "slide", "place", "rotate", "screw", "wrong", "none"]\n
                    - Manipulated objects: ["ball", "assembly box", "ball seat", "cylinder base", "cylinder cap", "cylinder bracket", "cylinder subassembly", "gear shaft", "large gear", "small gear", "bar", "rod", "large placer", "small placer", "screw bolt", "hex screw", "Phillips screw", "usb male", "linear bearing", "worm gear", "hand wheel", "quarter-turn handle", "hand dial", "nut", "screw bolt", "none"]\n
                    - Target objects: ["ball", "assembly box", "cylinder base", "ball seat", "cylinder bracket", "cylinder cap", "large gear", "gear shaft", "hole for the rod", "hole for the bar", "hole for the bolt", "hole for the Phillips screw", "stud on the assembly box", "usb female", "screw hole C1", "screw hole C2", "screw hole C3", "screw hole C4", "worm gear", "hole for the large gear", "hole for the small gear", "hole for the worm gear", "screw bolt", "nut", "none"]\n
                    - Tools: ["hex screwdriver", "Phillips screwdriver", "shaft wrench", "nut wrench", "none"]\n
                    - Primitive tasks: ["insert the ball into the cylinder base", "insert the ball seat into the cylinder base", "insert the cylinder cap into the cylinder bracket", "insert the cylinder bracket into the cylinder base", "insert the large gear into the gear shaft", "insert the small gear into the gear shaft", "insert the bar into the hole for the bar", "insert the rod into the hole for the rod", "insert the large placer into the gear shaft", "insert the small placer into the gear shaft", "insert the screw bolt into the hole for the bolt", "insert the hex screw into the screw hole C1", "insert the hex screw into the screw hole C2", "insert the hex screw into the screw hole C3", "insert the hex screw into the screw hole C4", "insert the hex screw into the cyliner bracket", "insert the Phillips screw into the worm gear", "insert the usb male into the usb female", "insert the cylinder base into the ball seat", "insert the cylinder base into the cylinder bracket", "insert the cylinder cap into the cylinder base", "insert the cylinder bracket into the cylinder cap", "insert the gear shaft into the large gear", "insert the Phillips screw into the hole for the worm gear", "insert the Phillips screw into the hole for the Phillips screw", "slide the cylinder bracket", "slide the linear bearing", "place the cylinder base onto the assembly box", "place the cylinder bracket onto the assembly box", "place the worm gear onto the assembly box", "place the ball onto the ball seat", "place the ball seat onto the ball", "place the ball seat onto the assembly box", "place the ball seat on to the cylinder cap", "place the assembly box onto the desk", "place the cylinder cap onto the desk", "place the cylinder bracket onto the desk", "place the cylinder bracket onto the cylinder base", "place the cyinder subassembly onto the box", "place the large placer onto the large gear", "rotate the worm gear", "rotate the hand dial", "rotate the quarter-turn handle", "rotate the hand wheel", "screw the cylinder cap onto the cylinder base", "screw the gear shaft onto the hole for large gear", "screw the gear shaft onto the hole for large gear using the shaft wrench", "screw the gear shaft onto the hole for small gear", "screw the gear shaft onto the hole for small gear using the shaft wrench", "screw the nut onto the gear shaft", "screw the nut onto the gear shaft using the nut wrench", "screw the nut onto the stud on the assembly box", "screw the nut onto the stud on the assembly box using the nut wrench", "screw the nut onto the screw bolt", "screw the nut onto the screw bolt using the nut wrench", "screw the screw bolt onto the nut", "screw the hex screw into the screw hole C1", "screw the hex screw into the screw hole C1 using the hex screwdriver", "screw the hex screw into the screw hole C1 uing a Phillips screwdriver", "screw the hex screw into the screw hole C2", "screw the hex screw into the screw hole C2 using the hex screwdriver", "screw the hex screw into the screw hole C2 using the Phillips screwdriver", "screw the hex screw into the screw hole C3", "screw the hex screw into the screw hole C3 using the hex screwdriver", "screw the hex screw into the screw hole C3 using the Phillips screwdriver", "screw the hex screw into the screw hole C4", "screw the hex screw into the screw hole C4 using the hex screwdriver", "screw the hex screw into the screw hole C4 using the Phillips screwdriver", "screw the Phillips screw into the hole for worm gear", "screw the Phillips screw into the hole for worm gear using the Phillips screwdriver", "screw the Phillips screw into the hole for Phillips screw", "screw the Phillips screw into the hole for Phillips screw using the Phillips screwdriver", "screw the cylinder base into the cylinder cap"]\n"""
                    
    user_text = user_text + valid_classes
    
    assistant_text_general = ("Below is the primitive task performed by the worker's left hand: \n")
    
    action_elements = parse_label(label)
    action_verb, action_verb_index = map_label_with_semantics(action_elements[0], action_verb_mapping)
    manipulated_object, manipulated_object_index = map_label_with_semantics(action_elements[1], object_mapping)
    target_object, target_object_index = map_label_with_semantics(action_elements[2], object_mapping)
    tool, tool_index = map_label_with_semantics(action_elements[3], tool_mapping)
    semantics, semantics_index = map_label_with_semantics(label, label_mapping)
    
    CoT_head = "Let's analyze this step-by-step: \n" 
    if label == "null":
       CoT_template = f"""
                   The worker's left hand is not assembling something onto something. Therefore the action verb is \"None\". Therefore, the manipulated object,
                   target object and tool are all \"None\".\n
                   """
    else:
        if action_verb == 'insert':
            CoT_main = f"""
                   1. The worker's left hand initiates a inserting motion, suggesting the action verb \"{action_verb}\".\n
                   2. Next, attention shifts to the object being manipulated by the left hand – a \"{manipulated_object}\" – which is interacted with the \"{target_object}\" visible in the frame.\n 
                   """
        elif action_verb == 'slide':
            CoT_main = f"""
                   1. The worker's left hand initiates a sliding motion, suggesting the action verb \"{action_verb}\".\n
                   2. Next, attention shifts to the object being manipulated by the left hand – a \"{manipulated_object}\" – which is interacted with the \"{target_object}\" visible in the frame.\n
                   """
        elif action_verb == 'place':
            CoT_main = f"""
                   1. The worker's left hand initiates a downward motion, suggesting the action verb \"{action_verb}\".\n
                   2. Next, attention shifts to the object being manipulated by the left hand – a \"{manipulated_object}\" – which is interacted with the \"{target_object}\" visible in the frame.\n
                   """
        elif action_verb == 'rotate':
            CoT_main = f"""
                   1. The worker's left hand initiates a rotational motion, suggesting the action verb \"{action_verb}\".\n
                   2. Next, attention shifts to the object being manipulated by the left hand – a \"{manipulated_object}\" – which is interacted with the \"{target_object}\" visible in the frame.\n
                   """
        elif action_verb == 'screw':
            CoT_main = f"""
                   1. The worker's left hand initiates a fine rotational motion, suggesting the action verb \"{action_verb}\".\n
                   2. Next, attention shifts to the object being manipulated by the left hand – a \"{manipulated_object}\" – which is interacted with the \"{target_object}\" visible in the frame.\n
                   """
        if tool == 'None':
            CoT_tool = f"""
                        3. No external tool is observed – the worker uses their hands to directly \"{action_verb}\" the \"{manipulated_object}\" onto the \"{target_object}\".\n
                        """
        else:
            CoT_tool = f"""
                        3. A \"{tool}\" can be seen in the worker's hand to perform the assembly task.\n
                        """
        CoT_template = CoT_head + CoT_main + CoT_tool    
    
    if label == "null":
        description = f"\n- Action verb: \"{action_verb}\"\n- Manipulated object: \"{manipulated_object}\"\n- Target object: \"{target_object}\"\n- Tool: \"{tool}\"\n\nConclusion: The left hand of the worker did nothing related to the assembly task. \n "
    else:
        description = f"\n- Action verb: \"{action_verb}\"\n- Manipulated object: \"{manipulated_object}\"\n- Target object: \"{target_object}\"\n- Tool: \"{tool}\"\n\nConclusion: The left hand of the worker is performing the primitive task \"{semantics}\". \n"
        #description =  f"The left hand of the worker performed the action verb is {action_verb}; manipulated object is {manipulated_object}; target object is {target_object}; using the tool {tool}. \n"
    
    assistant_text = assistant_text_general + description

    return user_text, assistant_text, CoT_template

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
    if ext.lower() != ".jpg":
        return None

    # Example pattern: S04A04I01M0_label_1
    # We'll assume an underscore-based pattern:
    #   <baseName>_<label>_<index>
    # You can adjust the pattern to match your actual filenames.
    parts = name_no_ext.split("_")

    if len(parts) < 4:
        # Filename doesn't match the expected pattern
        return None

    # Re-join everything up to the second-to-last part as base_name
    # (In case the label has underscores, you may need more advanced logic.)
    *base_parts, label, idx_str, idx_frame = parts
    base_name = "_".join(base_parts)

    # Attempt to convert index to integer
    try:
        clip_index = int(idx_str)
    except ValueError:
        clip_index = None
        
    try:
        frame_index = int(idx_frame)
    except ValueError:
        frame_index = None

    return (base_name, label, clip_index, frame_index)

def gather_split_frames_annotations(split_frames_folder, action_verb_mapping, object_mapping, tool_mapping, label_mapping):
    """
    Goes through the folder containing your split .mp4 files.
    For each .mp4, parse its name to extract baseName, label, and index.
    Returns a list of annotation dictionaries.
    """
    grouped_images = defaultdict(list)
    json_data = []
    entry_id = 0  # Initialize ID counter

    for filename in os.listdir(split_frames_folder):
        if filename.lower().endswith(".jpg"):
            parsed = parse_splitted_filename(filename)
            if parsed is not None:
                base_name, label, clip_index, frame_index = parsed
                group_key = (base_name, label, clip_index)
                grouped_images[group_key].append((frame_index, filename))
                
    for group_key, frames in grouped_images.items():
        base_name, label, clip_index = group_key
        
        # Sort frames by frame index
        sorted_frames = sorted(frames, key=lambda x: x[0])
        
        # Create image dictionary with placeholders
        image_dict = {}
        image_paths = []
        for idx, (frame_idx, filename) in enumerate(sorted_frames):
            placeholder = f"<image_{idx:02d}>"
            image_dict[placeholder] = f"../frames_cropped/lh_v0/{filename}"
            image_paths.append(placeholder)
                
                # Create the JSON structure for this file
                
                # Read or parse your annotation file
        user_text, assistant_text, CoT_template = read_annotation_file(label, action_verb_mapping, object_mapping, tool_mapping, label_mapping)
                
        image_tags = "\n".join(image_paths)
        user_text = user_text.replace("<image>", f"<image>\n{image_tags}")
                
            # The "videos" field can be derived from the annotation filename
            # or however your naming convention is set
        data_entry = {
            "id": str(entry_id),  # Add unique ID as string
            "image": image_dict,
            "conversations": [
                {
                    "content": user_text,
                    "role": "user"
                },
                {
                    "content": {
                        "chain_of_thought": CoT_template,
                        "final_answer": assistant_text
                        },
                    "role": "assistant"
                }
            ],
        }
            
        json_data.append(data_entry)
        entry_id += 1

    return json_data

def main():
    # 1. Specify your folder of split videos
    split_frames_folder = "./frames_cropped_no_w/lh_v0"
    
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
    json_data = gather_split_frames_annotations(split_frames_folder, action_verb_mapping, object_mapping, tool_mapping, label_mapping)

    # 3. Write them to a JSON file
    output_json = "./json_split_videos/multi_frames_cropped_CoT.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Wrote {len(json_data)} annotations to {output_json}.")

if __name__ == "__main__":
    main()
