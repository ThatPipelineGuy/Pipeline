# Copyright (c) 2023 Dimitri Mitchell. All rights reserved.
#
# Permission is hereby granted, free of charge, to use and modify this software for personal and non-commercial purposes only,
# provided that this notice is retained in its entirety.
#
# Any other use, reproduction, modification, distribution, or performance of this software without prior written consent or from the author is strictly prohibited.

import bpy
import os
import json
import re

# Define tags for identifying objects
TAGS = ["XXXX", "XXX", "XX", "X"]

# Get the directory and name of the blend file
blend_dir = os.path.dirname(bpy.data.filepath)
blend_name = bpy.path.basename(bpy.context.blend_data.filepath)

# Extract the base name without the extension and version number
match = re.match(r"(.+)_V\d+", blend_name)
if match:
    base_name = match.group(1)
else:
    base_name = os.path.splitext(blend_name)[0]

# Create a folder for the output if it doesn't exist
output_dir = os.path.join(blend_dir, "json")
os.makedirs(output_dir, exist_ok=True)

# Create a dictionary to store the data
data = {}

# Create a root container
root = {}

# Loop through all the objects in the scene
for obj in bpy.context.scene.objects:
    # Check if the object's name contains one of the containing tags
    containing_tag = None
    for tag in TAGS:
        if tag in obj.name:
            containing_tag = tag
            print(f"{obj.name} has tag {tag}")
            break

    # If the object has a containing tag, add it to the root container
    if containing_tag:
        identifying_parent = obj.name.split("_")[0]
        if identifying_parent not in root:
            root[identifying_parent] = {}
        root[identifying_parent][obj.name] = {}

        # Add attributes for the child objects (assets)
        for child in obj.children:
            child_name = child.name.replace("__", "_")
            material_name = ""
            if child.data.materials:
                material_name = child.data.materials[0].name
            root[identifying_parent][obj.name][child_name] = {
                "Mesh Name": child_name,
                "Mesh Asset": f"{child_name}.uasset",
                "Material": f"{material_name}.uasset"
            }

    # If the object doesn't have a containing tag, add it to the root container only if its parent has a containing tag and it has children
    elif obj.parent and any(tag in obj.parent.name for tag in TAGS) and obj.children:
        identifying_parent = obj.parent.name.split("_")[0]
        if identifying_parent not in root:
            root[identifying_parent] = {}
        root[identifying_parent][obj.parent.name] = {}

        # Add attributes for the child objects (assets)
        for child in obj.children:
            child_name = child.name.replace("__", "_")
            material_name = ""
            if child.data.materials:
                material_name = child.data.materials[0].name
            root[identifying_parent][obj.parent.name][child_name] = {
                "Mesh Name": child_name,
                "Mesh Asset": f"{child_name}.uasset",
                "Material": f"{material_name}.uasset"
            }

# Add the root container to the dictionary
data["root"] = root

# Create a versioned filename for the output
version_num = 1
output_base_name = f"{base_name}_V"
output_ext = ".json"
output_filename = f"{output_base_name}{version_num:02d}{output_ext}"
output_path = os.path.join(output_dir, output_filename)

while os.path.exists(output_path):
    version_num += 1
    output_filename = f"{output_base_name}{version_num:02d}{output_ext}"
    output_path = os.path.join(output_dir, output_filename)

# Write the data to a JSON file
with open(output_path, "w") as jsonfile:
    json.dump(data, jsonfile, indent=4)

print(f"Data exported to {output_path}")
