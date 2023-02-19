# Copyright (c) 2023 Dimitri Mitchell. All rights reserved.
#
# Permission is hereby granted, free of charge, to use and modify this software for personal and non-commercial purposes only,
# provided that this notice is retained in its entirety.
#
# Any other use, reproduction, modification, distribution, or performance of this software without prior written consent or from the author is strictly prohibited.

import bpy
import os
import json

# Define the output file base name
output_filename_base = "my_output_file"

# get the directory of the .blend file
blend_dir = os.path.dirname(bpy.data.filepath)


# get the name of the .blend file
blend_name = bpy.path.basename(bpy.context.blend_data.filepath)

# get the version number of the .blend file
blend_version = bpy.data.version

# create a folder for the output if it doesn't exist
output_dir = os.path.join(blend_dir, "json")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# create a dictionary to store the data
data = {}

# create a root container
root = {}

# loop through all the objects in the scene
for obj in bpy.context.scene.objects:
    # check if the object's name contains one of the containing tags
    containing_tag = None
    for tag in ["EXT", "INT", "ACE", "PWT"]:
        if tag in obj.name:
            containing_tag = tag
            break
    # if the object has a containing tag, add it to the root container
    if containing_tag:
        # get the identifying parent name
        identifying_parent = obj.name.split("_")[0]
        # create a container for the object
        if identifying_parent not in root:
            root[identifying_parent] = {}
        # create a list to store the child objects
        children = []
        # loop through all the child objects of the containing object
        for child in obj.children:
            # add the name of the child object to the list
            children.append(child.name)
        # add the list of child object names to the container
        root[identifying_parent][obj.name] = children
    # if the object doesn't have a containing tag, add it to the root container only if it has children
    elif obj.children:
        # replace double underscores with single ones in the name
        name = obj.name.replace("__", "_")
        # add the object to the root container
        root[name] = {"children": []}
        # add the children of the object to the root container
        for child in obj.children:
            child_name = child.name.replace("__", "_")
            root[name]["children"].append(child_name)

# add the root container to the dictionary
data["root"] = root

# create a versioned filename for the output
output_filename = f"{output_filename_base}_V1.json"
output_path = os.path.join(output_dir, output_filename)

# write the data to a JSON file
with open(output_path, "w") as jsonfile:
    # write the data to the file in JSON format
    json.dump(data, jsonfile, indent=4)

print(f"Data exported to {output_path}")
