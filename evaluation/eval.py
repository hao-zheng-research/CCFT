import os
import re
import spacy
import numpy as np
from nltk.corpus import wordnet
from sentence_transformers import SentenceTransformer, util
from transformers import AutoProcessor
from vllm import LLM, SamplingParams
from qwen_vl_utils import process_vision_info
import pandas as pd

sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

ACTION_VERBS = ["insert", "slide", "place", "rotate", "screw", "wrong", "null"]                   
MANIPULATED_OBJS  = ["ball", "assembly box", "ball seat", "cylinder base", "cylinder cap", "cylinder bracket", "cylinder subassembly", "gear shaft", "large gear", "small gear", "bar", "rod", "large placer", "small placer", "screw bolt", "hex screw", "Phillips screw", "usb male", "linear bearing", "worm gear", "hand wheel", "quarter-turn handle", "hand dial", "nut", "screw bolt", "null"]                    
TARGET_OBJS  = ["ball", "assembly box", "cylinder base", "ball seat", "cylinder bracket", "cylinder cap", "large gear", "gear shaft", "hole for the rod", "hole for the bar", "hole for the bolt", "hole for the Phillips screw", "stud on the assembly box", "usb female", "screw hole C1", "screw hole C2", "screw hole C3", "screw hole C4", "worm gear", "hole for the large gear", "hole for the small gear", "hole for the worm gear", "screw bolt", "nut", "null"]                    
TOOLS = ["hex screwdriver", "Phillips screwdriver", "shaft wrench", "nut wrench", "null"]                    
PRIMITIVE_TASKS = ["insert the ball into the cylinder base", "insert the ball seat into the cylinder base", "insert the cylinder cap into the cylinder bracket", "insert the cylinder bracket into the cylinder base", "insert the large gear into the gear shaft", "insert the small gear into the gear shaft", "insert the bar into the hole for the bar", "insert the rod into the hole for the rod", "insert the large placer into the gear shaft", "insert the small placer into the gear shaft", "insert the screw bolt into the hole for the bolt", "insert the hex screw into the screw hole C1", "insert the hex screw into the screw hole C2", "insert the hex screw into the screw hole C3", "insert the hex screw into the screw hole C4", "insert the hex screw into the cyliner bracket", "insert the Phillips screw into the worm gear", "insert the usb male into the usb female", "insert the cylinder base into the ball seat", "insert the cylinder base into the cylinder bracket", "insert the cylinder cap into the cylinder base", "insert the cylinder bracket into the cylinder cap", "insert the gear shaft into the large gear", "insert the Phillips screw into the hole for the worm gear", "insert the Phillips screw into the hole for the Phillips screw", "slide the cylinder bracket", "slide the linear bearing", "place the cylinder base onto the assembly box", "place the cylinder bracket onto the assembly box", "place the worm gear onto the assembly box", "place the ball onto the ball seat", "place the ball seat onto the ball", "place the ball seat onto the assembly box", "place the ball seat on to the cylinder cap", "place the assembly box onto the desk", "place the cylinder cap onto the desk", "place the cylinder bracket onto the desk", "place the cylinder bracket onto the cylinder base", "place the cyinder subassembly onto the box", "place the large placer onto the large gear", "rotate the worm gear", "rotate the hand dial", "rotate the quarter-turn handle", "rotate the hand wheel", "screw the cylinder cap onto the cylinder base", "screw the gear shaft onto the hole for large gear", "screw the gear shaft onto the hole for large gear using the shaft wrench", "screw the gear shaft onto the hole for small gear", "screw the gear shaft onto the hole for small gear using the shaft wrench", "screw the nut onto the gear shaft", "screw the nut onto the gear shaft using the nut wrench", "screw the nut onto the stud on the assembly box", "screw the nut onto the stud on the assembly box using the nut wrench", "screw the nut onto the screw bolt", "screw the nut onto the screw bolt using the nut wrench", "screw the screw bolt onto the nut", "screw the hex screw into the screw hole C1", "screw the hex screw into the screw hole C1 using the hex screwdriver", "screw the hex screw into the screw hole C1 uing a Phillips screwdriver", "screw the hex screw into the screw hole C2", "screw the hex screw into the screw hole C2 using the hex screwdriver", "screw the hex screw into the screw hole C2 using the Phillips screwdriver", "screw the hex screw into the screw hole C3", "screw the hex screw into the screw hole C3 using the hex screwdriver", "screw the hex screw into the screw hole C3 using the Phillips screwdriver", "screw the hex screw into the screw hole C4", "screw the hex screw into the screw hole C4 using the hex screwdriver", "screw the hex screw into the screw hole C4 using the Phillips screwdriver", "screw the Phillips screw into the hole for worm gear", "screw the Phillips screw into the hole for worm gear using the Phillips screwdriver", "screw the Phillips screw into the hole for Phillips screw", "screw the Phillips screw into the hole for Phillips screw using the Phillips screwdriver", "screw the cylinder base into the cylinder cap", "null"]
PRIMITIVE_TASKS_no_null = ["insert the ball into the cylinder base", "insert the ball seat into the cylinder base", "insert the cylinder cap into the cylinder bracket", "insert the cylinder bracket into the cylinder base", "insert the large gear into the gear shaft", "insert the small gear into the gear shaft", "insert the bar into the hole for the bar", "insert the rod into the hole for the rod", "insert the large placer into the gear shaft", "insert the small placer into the gear shaft", "insert the screw bolt into the hole for the bolt", "insert the hex screw into the screw hole C1", "insert the hex screw into the screw hole C2", "insert the hex screw into the screw hole C3", "insert the hex screw into the screw hole C4", "insert the hex screw into the cyliner bracket", "insert the Phillips screw into the worm gear", "insert the usb male into the usb female", "insert the cylinder base into the ball seat", "insert the cylinder base into the cylinder bracket", "insert the cylinder cap into the cylinder base", "insert the cylinder bracket into the cylinder cap", "insert the gear shaft into the large gear", "insert the Phillips screw into the hole for the worm gear", "insert the Phillips screw into the hole for the Phillips screw", "slide the cylinder bracket", "slide the linear bearing", "place the cylinder base onto the assembly box", "place the cylinder bracket onto the assembly box", "place the worm gear onto the assembly box", "place the ball onto the ball seat", "place the ball seat onto the ball", "place the ball seat onto the assembly box", "place the ball seat on to the cylinder cap", "place the assembly box onto the desk", "place the cylinder cap onto the desk", "place the cylinder bracket onto the desk", "place the cylinder bracket onto the cylinder base", "place the cyinder subassembly onto the box", "place the large placer onto the large gear", "rotate the worm gear", "rotate the hand dial", "rotate the quarter-turn handle", "rotate the hand wheel", "screw the cylinder cap onto the cylinder base", "screw the gear shaft onto the hole for large gear", "screw the gear shaft onto the hole for large gear using the shaft wrench", "screw the gear shaft onto the hole for small gear", "screw the gear shaft onto the hole for small gear using the shaft wrench", "screw the nut onto the gear shaft", "screw the nut onto the gear shaft using the nut wrench", "screw the nut onto the stud on the assembly box", "screw the nut onto the stud on the assembly box using the nut wrench", "screw the nut onto the screw bolt", "screw the nut onto the screw bolt using the nut wrench", "screw the screw bolt onto the nut", "screw the hex screw into the screw hole C1", "screw the hex screw into the screw hole C1 using the hex screwdriver", "screw the hex screw into the screw hole C1 uing a Phillips screwdriver", "screw the hex screw into the screw hole C2", "screw the hex screw into the screw hole C2 using the hex screwdriver", "screw the hex screw into the screw hole C2 using the Phillips screwdriver", "screw the hex screw into the screw hole C3", "screw the hex screw into the screw hole C3 using the hex screwdriver", "screw the hex screw into the screw hole C3 using the Phillips screwdriver", "screw the hex screw into the screw hole C4", "screw the hex screw into the screw hole C4 using the hex screwdriver", "screw the hex screw into the screw hole C4 using the Phillips screwdriver", "screw the Phillips screw into the hole for worm gear", "screw the Phillips screw into the hole for worm gear using the Phillips screwdriver", "screw the Phillips screw into the hole for Phillips screw", "screw the Phillips screw into the hole for Phillips screw using the Phillips screwdriver", "screw the cylinder base into the cylinder cap"]



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

def load_all_mappings(base_dir):
    """Load all mapping files from a directory and return them as a tuple.
    
    Args:
        base_dir (str): Path to directory containing mapping files. Defaults to "./eval_utils/"
        
    Returns:
        tuple: Contains four mappings in order:
            - action_verb_mapping
            - object_mapping
            - tool_mapping
            - label_mapping
    """
    def load(path):
        return load_object_mapping(os.path.join(base_dir, path))
    
    return (
        load("action_verb_mapping.txt"),
        load("object_mapping.txt"),
        load("tool_mapping.txt"),
        load("label_mapping.txt"),
    )

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

# Extract Ground Truth Label from Filename
def extract_label(filename):
    # Split filename by underscores and extract the label part (e.g., "ibacb" in "S04A04I01M0_ibacb_2.mp4")
    parts = filename.split("_")
    if len(parts) < 3:
        raise ValueError(f"Invalid filename format: {filename}")
    return parts[1]  # Assumes format: name_label_index.mp4

def exact_match(response, task_list):
    for task in task_list:
        if task in response:
            return task
    return None  # No exact match found

# Parse VLM Output to Extract Primitive Task
def parse_vlm_output(vlm_text):
    # Use regex to find the task description (e.g., "screw the nut onto the gear shaft")
    patterns = {
        "action_verb": r"action verb is\s*['\"]?([\w-]+(?:\s+[\w-]+)*)",
        "manipulated_object": r"manipulated object is\s*['\"]?([\w-]+(?:\s+[\w-]+)*)",
        "target_object": r"target object is\s*['\"]?([\w-]+(?:\s+[\w-]+)*)",
        "tool": r"tool is\s*['\"]?([\w-]+(?:\s+[\w-]+)*)"
    }

    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, vlm_text, re.IGNORECASE)
        extracted[key] = match.group(1).lower() if match else "null"

    if extracted["action_verb"] == "null":
        reconstructed_primitive_task = "null"
    elif extracted["action_verb"] == "rotate":
        reconstructed_primitive_task = f"{extracted['action_verb']} the {extracted['manipulated_object']}"
    elif extracted["tool"] == "null":
        reconstructed_primitive_task = f"{extracted['action_verb']} the {extracted['manipulated_object']} onto the {extracted['target_object']}"
    else:
        reconstructed_primitive_task = f"{extracted['action_verb']} the {extracted['manipulated_object']} onto the {extracted['target_object']} using the {extracted['tool']}"
    
    primitive_task_exact = exact_match(vlm_text, PRIMITIVE_TASKS)

    if reconstructed_primitive_task == primitive_task_exact:
        extracted["primitive_task"] = reconstructed_primitive_task
    elif primitive_task_exact == None:
        extracted["primitive_task"] = reconstructed_primitive_task
    elif reconstructed_primitive_task == "null" and primitive_task_exact != "null":
        extracted["primitive_task"] = primitive_task_exact
    elif reconstructed_primitive_task != "null" and primitive_task_exact == "null":
        extracted["primitive_task"] = reconstructed_primitive_task
    else:
        extracted["primitive_task"] = primitive_task_exact

    return extracted

# Compute Semantic Similarity
def semantic_similarity(text1, text2):
    embeddings = sbert_model.encode([text1, text2])
    return util.cos_sim(embeddings[0], embeddings[1]).item()

def safe_divide(numerator, denominator):
    return numerator / denominator if denominator != 0 else 0.0

# Main evaluation workflow
def evaluate_vlm(video_folder, processor, llm, mapping_file_path, log_file_path, wrong_preds_path, txt_file_path, similarity_threshold=0.9):
    # Initialize counters and results storage
    total = 0
    correct_primitive_task = 0
    correct_action_verb = 0
    correct_manipulated_object = 0
    correct_target_object = 0
    correct_tool = 0
    results_log = []

    action_verb_mapping, object_mapping, tool_mapping, label_mapping = load_all_mappings(mapping_file_path)

    # Iterate through video files
    for filename in os.listdir(video_folder):
        if not filename.endswith(".mp4"):
            continue

        entry = {
            "filename": filename,
            "gt_label": None,
            "vlm_output": None,
            "primitive_task": None,
            "primitive_task_gt": None,
            "action_verb": None,
            "action_verb_gt": None,
            "manipulated_object": None,
            "manipulated_object_gt": None,
            "target_object": None,
            "target_object_gt": None,
            "tool": None,
            "tool_gt": None,
            "primitive_task_similarity": None,
            "action_verb_similarity": None,
            "manipulated_object_similarity": None,
            "target_object_similarity": None,
            "tool_similarity": None,
            "is_primitive_task_correct": False,
            "is_action_verb_correct": False,
            "is_manipulated_object_correct": False,
            "is_target_object_correct": False,
            "is_tool_correct": False
        }

        try:
            # Extract ground truth
            gt_label = extract_label(filename)
            entry["gt_label"] = gt_label
            action_elements_gt = parse_label(gt_label)
            
            # VLM inference
            video_path = os.path.join(video_folder, filename)
            messages = [{"role": "system", "content": " "},
                                {"role": "user", "content": [
                                    {"type": "text", "text": "What assembly primitive task did the worker's left hand perform in the video?"},
                                        {"type": "video", 
                                        "video": f"{video_path}",   #/workspace/LLaMA-Factory/data/CCFT_lh_de_513/S04A04I01M0_sshc1dh_16.mp4  /workspace/MiniCPM-o/assets/CCFT/S04A04I01M0_ibacb_2.mp4
                                        "total_pixels": 20480 * 28 * 28, "min_pixels": 16 * 28 * 28}
                                        ]
                                }]
            prompt = processor.apply_chat_template( messages,
                                                    tokenize=False,
                                                    add_generation_prompt=True,)

            image_inputs, video_inputs, video_kwargs = process_vision_info(messages, return_video_kwargs=True)

            mm_data = {}
            if image_inputs is not None:
                mm_data["image"] = image_inputs
            if video_inputs is not None:
                mm_data["video"] = video_inputs
            
            llm_inputs = {"prompt": prompt,
                        "multi_modal_data": mm_data,
                        # FPS will be returned in video_kwargs
                        "mm_processor_kwargs": video_kwargs,}

            outputs = llm.generate([llm_inputs], sampling_params=sampling_params)
            vlm_output = outputs[0].outputs[0].text

            entry["vlm_output"] = vlm_output

            # Parse VLM output
            extracted = parse_vlm_output(vlm_output)
            entry.update({
                "primitive_task": extracted["primitive_task"],
                "action_verb": extracted["action_verb"],
                "manipulated_object": extracted["manipulated_object"],
                "target_object": extracted["target_object"],
                "tool": extracted["tool"]
            })

            # Get ground truth mappings
            primitive_task_gt = map_label_with_semantics(gt_label, label_mapping)
            action_verb_gt = map_label_with_semantics(action_elements_gt[0], action_verb_mapping)
            manipulated_object_gt = map_label_with_semantics(action_elements_gt[1], object_mapping)
            target_object_gt = map_label_with_semantics(action_elements_gt[2], object_mapping)
            tool_gt = map_label_with_semantics(action_elements_gt[3], tool_mapping)

            entry.update({
                "primitive_task_gt": primitive_task_gt,
                "action_verb_gt": action_verb_gt,
                "manipulated_object_gt": manipulated_object_gt,
                "target_object_gt": target_object_gt,
                "tool_gt": tool_gt
            })

            # Calculate similarities
            primitive_task_sim = semantic_similarity(entry["primitive_task"], primitive_task_gt)
            action_verb_sim = semantic_similarity(entry["action_verb"], action_verb_gt)
            manipulated_object_sim = semantic_similarity(entry["manipulated_object"], manipulated_object_gt)
            target_object_sim = semantic_similarity(entry["target_object"], target_object_gt)
            tool_sim = semantic_similarity(entry["tool"], tool_gt)

            entry.update({
                "primitive_task_similarity": primitive_task_sim,
                "action_verb_similarity": action_verb_sim,
                "manipulated_object_similarity": manipulated_object_sim,
                "target_object_similarity": target_object_sim,
                "tool_similarity": tool_sim,
                "is_primitive_task_correct": primitive_task_sim >= similarity_threshold,
                "is_action_verb_correct": action_verb_sim >= similarity_threshold,
                "is_manipulated_object_correct": manipulated_object_sim >= similarity_threshold,
                "is_target_object_correct": target_object_sim >= similarity_threshold,
                "is_tool_correct": tool_sim >= similarity_threshold
            })

            # Update counters
            if entry["is_primitive_task_correct"]:
                correct_primitive_task += 1
            if entry["is_action_verb_correct"]:
                correct_action_verb += 1
            if entry["is_manipulated_object_correct"]:
                correct_manipulated_object += 1
            if entry["is_target_object_correct"]:
                correct_target_object += 1
            if entry["is_tool_correct"]:
                correct_tool += 1

            total += 1

        except Exception as e:
            entry["error"] = str(e)
            print(f"Error processing {filename}: {str(e)}")
        
        results_log.append(entry)

    # Calculate metrics
    metrics = {
        "total_samples": total,
        "primitive_task_acc": safe_divide(correct_primitive_task, total),
        "action_verb_acc": safe_divide(correct_action_verb, total),
        "manipulated_object_acc": safe_divide(correct_manipulated_object, total),
        "target_object_acc": safe_divide(correct_target_object, total),
        "tool_acc": safe_divide(correct_tool, total)
    }

    # Save log to file
    if log_file_path:
        try:
            full_df = pd.DataFrame(results_log)
            full_df.to_csv(log_file_path, index=False)
            print(f"Full results log saved to {log_file_path}")
            
            # Save wrong predictions
            if wrong_preds_path:
                wrong_preds = full_df[
                    (full_df["is_primitive_task_correct"] == False) |
                    (full_df["is_action_verb_correct"] == False) |
                    (full_df["is_manipulated_object_correct"] == False) |
                    (full_df["is_target_object_correct"] == False) |
                    (full_df["is_tool_correct"] == False)
                ]
                
                if not wrong_preds.empty:
                    wrong_preds.to_csv(wrong_preds_path, index=False)
                    print(f"Wrong predictions saved to {wrong_preds_path}")
                    print(f"Total wrong predictions: {len(wrong_preds)}/{total}")
                else:
                    print("No wrong predictions to save")
                    
        except Exception as e:
            print(f"Failed to save log files: {str(e)}")

    # Print summary
    print(f"Primitive Task-Wise Accuracy (Threshold={similarity_threshold}): {metrics['primitive_task_acc']:.2%}")
    print("Component-Wise Accuracy:")
    print(f"  Action Verb: {metrics['action_verb_acc']:.2%}")
    print(f"  Manipulated Object: {metrics['manipulated_object_acc']:.2%}")
    print(f"  Target Object: {metrics['target_object_acc']:.2%}")
    print(f"  Tool: {metrics['tool_acc']:.2%}")

    with open(txt_file_path, "w") as f:
        f.write(f"Primitive Task-Wise Accuracy (Threshold={similarity_threshold}): {metrics['primitive_task_acc']:.2%}\n")
        f.write("Component-Wise Accuracy:\n")
        f.write(f"  Action Verb: {metrics['action_verb_acc']:.2%}\n")
        f.write(f"  Manipulated Object: {metrics['manipulated_object_acc']:.2%}\n")
        f.write(f"  Target Object: {metrics['target_object_acc']:.2%}\n")
        f.write(f"  Tool: {metrics['tool_acc']:.2%}\n")

    return metrics, results_log

if __name__ == "__main__":
    # Load NLP and embedding models
    nlp = spacy.load("en_core_web_sm")
    sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load Qwen model
    MODEL_PATH = "/home/hao/CCFT/LLaMA-Factory/models/CCFT_havid_sub_videos_crop_lh_v0_simple/checkpoint-800"

    llm = LLM(
        model=MODEL_PATH,
        limit_mm_per_prompt={"image": 10, "video": 10},
    )

    sampling_params = SamplingParams(
        temperature=0.01,
        top_p=0.001,
        repetition_penalty=1.05,
        max_tokens=6144,
        stop_token_ids=[],
    )
    processor = AutoProcessor.from_pretrained(MODEL_PATH)

    # Evaluate
    # video_folder = "/home/hao/CCFT/LLaMA-Factory/data/havid_sub_videos_crop/lh_v0/test"
    # mapping_file_path = "./eval_utils/"
    # log_file_path="havid_sub_videos_crop_results.csv"
    
    metrics, detailed_log = evaluate_vlm(
                            video_folder="/home/hao/CCFT/LLaMA-Factory/data/havid_sub_videos_crop/lh_v0/test",
                            processor = processor,
                            llm = llm,
                            mapping_file_path="./eval_utils/",
                            log_file_path="eval_results/CCFT_havid_sub_videos_crop_lh_v0_simple_checkpoint-800.csv",
                            wrong_preds_path="eval_results/CCFT_havid_sub_videos_crop_lh_v0_simple_checkpoint-800_wrong_predictions.csv",
                            txt_file_path="eval_results/CCFT_havid_sub_videos_crop_balanced_lh_v0_simple_v5.txt",
                            similarity_threshold=0.95,
                            )
    
    # evaluate_vlm(video_folder, processor, llm, mapping_file_path, log_file_path)
