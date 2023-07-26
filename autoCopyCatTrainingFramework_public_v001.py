import os
import random
import nuke

# Point to a /xxxx/xxxx/jobs
root_directory = '/mnt/jobs'

# Number of read nodes to make for current data set
num_iterations = int(nuke.getInput('Number of Reads (use discretion)', '10'))
# Hardcoded Backup (useful for full automation) vvv
# num_iterations = 5  

# Define the allowed file extensions
ALLOWED_EXTENSIONS = ['.exr', '.png', '.jpg', '.jpeg', '.tif', '.dpx']

# Define the jobs and sequences that require the Rec.709 colorspace for EXR's
# Use the exact name of the job directory, list any sequences or use '*' for all sequences in a job
REC709_JOBS_SEQUENCES = [
    {'job': 'sample_job_123456', 'sequence': '*'},
    {'job': 'sample_job2_123456', 'sequence': '*'},
    # add more jobs and sequences as needed
]

# Creates the 'processed' channel set to be used later 
nuke.tcl("add_layer", "processed processed.red processed.green processed.blue")


##########################################################################


#Returns a random image path in a plates directory in whatever 'jobs' folder is provided
def get_random_image_path(root_directory):
    # List all jobs in the job directory
    job_directories = [job_dir for job_dir in os.listdir(root_directory) if os.path.isdir(os.path.join(root_directory, job_dir))]

    if not job_directories:
        return None

    # Randomly select a job from job_directories
    random_job = random.choice(job_directories)

    # Appends sequence directory to return jobs/xxxx/sequence
    sequence_directory = os.path.join(root_directory, random_job, 'sequence')

    # Try another job if sequence directory doesn't exist
    if not os.path.exists(sequence_directory):
        return get_random_image_path(root_directory)  

    # List all sequences in the sequence directory 
    sequence_directories = [seq_dir for seq_dir in os.listdir(sequence_directory) if os.path.isdir(os.path.join(sequence_directory, seq_dir))]

    # Try another job if no sequences found
    if not sequence_directories:
        return get_random_image_path(root_directory)  

    # Randomly select a sequence directory
    random_sequence = random.choice(sequence_directories)

    # Join the random seq choice to file path to return jobs/xxxx/sequence/yyyy
    shot_directory = os.path.join(sequence_directory, random_sequence)

    # Try another job if shot directory doesn't exist
    if not os.path.exists(shot_directory):
        return get_random_image_path(root_directory)  

    # List all shots in a sequence 
    shot_directories = [shot_dir for shot_dir in os.listdir(shot_directory) if os.path.isdir(os.path.join(shot_directory, shot_dir))]

    # Try another job if no shots found
    if not shot_directories:
        return get_random_image_path(root_directory)  

    # Randomly select a shot directory
    random_shot = random.choice(shot_directories)

    # Join the random shot path to return jobs/xxxx/sequence/yyyy/zzz###/elements/plates
    plates_directory = os.path.join(shot_directory, random_shot, 'elements', 'plates')

    # Try another job if plates directory doesn't exist
    if not os.path.exists(plates_directory):
        return get_random_image_path(root_directory)  

    # Dig one directory deeper to handle image sequences
    sequence_directories = [seq_dir for seq_dir in os.listdir(plates_directory) if os.path.isdir(os.path.join(plates_directory, seq_dir))]

    # Try another job if no sequence directories found
    if not sequence_directories:
        return get_random_image_path(root_directory)  

    # Randomly select a sequence directory (for image sequences)
    random_sequence = random.choice(sequence_directories)

    image_sequence_directory = os.path.join(plates_directory, random_sequence)

    # Lists all images in plate image sequence folder
    image_files = [file for file in os.listdir(image_sequence_directory) if any(file.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)]
    
    # Try another job if no image files found
    if not image_files:
        return get_random_image_path(root_directory)  

    # Selects a random image path 
    random_image = random.choice(image_files)

    # Appends the image to the file path to complete the image file path 
    image_path = os.path.join(image_sequence_directory, random_image)
    return image_path


##########################################################################


def create_read_node_with_image(image_path, x_pos, y_pos):
    read_node = nuke.createNode('Read')

    # Pass the file knob the random image path (if given in argument when called)
    read_node['file'].setValue(image_path)

    # ADJUST COLOR SPACE FOR DESIGNATED PROJECTS/SEQUENCES
    # Only adjust colorspace for .exr files
    if image_path.lower().endswith('.exr'):
        path_parts = image_path.split('/')
        job = path_parts[path_parts.index('jobs') + 1]
        sequence = path_parts[path_parts.index('sequence') + 1]

        # Check the job and sequence against the list of Rec.709 jobs and sequences
        for rec709 in REC709_JOBS_SEQUENCES:
            if rec709['job'] == job and (rec709['sequence'] == sequence or rec709['sequence'] == '*'):
                read_node['colorspace'].setValue('color_picking')
                break

    read_node.setXYpos(x_pos, y_pos)
    read_node['postage_stamp'].setValue(False)  # Disable the postage stamp
    read_node.hideControlPanel()
    return read_node


##########################################################################


def create_copy_node(input_node, read_node):
    # Create Copy node
    copy_node = nuke.createNode('Copy')
    copy_node.setInput(0, read_node)
    copy_node.setInput(1, input_node)
    copy_node['from0'].setValue('red')
    copy_node['to0'].setValue('processed.red')
    copy_node['from1'].setValue('green')
    copy_node['to1'].setValue('processed.green')
    copy_node['from2'].setValue('blue')
    copy_node['to2'].setValue('processed.blue')
    copy_node.hideControlPanel()  # Hide the control panel of the Copy node


##########################################################################


def create_and_connect_nodes(read_node):
    
    # PLACE ALL IMAGE PROCESSING YOU WANT TO TRAIN ON INSIDE VVVVV
    ################################################
    # PROCESSING - Create Reformat node
    reformat_node1 = nuke.createNode('Reformat')
    reformat_node1['type'].setValue('2.0')
    reformat_node1['scale'].setValue(0.8)
    reformat_node1.hideControlPanel()

    # PROCESSING - Create Clamp node
    clamp_node = nuke.createNode('Clamp')
    clamp_node['maximum'].setValue(.7)
    clamp_node.hideControlPanel()

    # PROCESSING - Create final Reformat node
    reformat_node2 = nuke.createNode('Reformat')
    reformat_node2['type'].setValue('2.0')
    reformat_node2['scale'].setValue(1.25)
    reformat_node2.hideControlPanel()
    ################################################

    # Connect the nodes in sequence
    read_node['selected'].setValue(False)  # Deselect the Read node
    reformat_node1.setInput(0, read_node)
    clamp_node.setInput(0, reformat_node1)
    reformat_node2.setInput(0, clamp_node)

    # Create Copy node to copy the last Reformat node into the original Read node
    # First argument should be the last processed node it connects to 
    create_copy_node(reformat_node2, read_node)

    return reformat_node1, clamp_node, reformat_node2


##########################################################################


def create_append_clip_node(copy_nodes, x_pos, y_pos):
    # Create AppendClip node
    append_clip_node = nuke.createNode('AppendClip')

    # Adjust y position
    append_clip_node.setXYpos(x_pos, y_pos + 200)  

    # Connect all Copy nodes to the inputs of the AppendClip node by saying for # of copy nodes, set index input
    for index, copy_node in enumerate(copy_nodes):
        append_clip_node.setInput(index, copy_node)

    append_clip_node.hideControlPanel()

    # Create a Dot node after AppendClip
    dot_node = nuke.createNode('Dot')
    dot_node.setInput(0, append_clip_node)
    dot_node.setXYpos(x_pos + 35, y_pos + 300)  # Adjust y position
    dot_node.hideControlPanel()

    # Create a Dot node to the left for rgb 
    dot_node2 = nuke.createNode('Dot')
    dot_node2.setInput(0, dot_node)
    dot_node2.setXYpos(x_pos - 75, y_pos + 300)  # Adjust xy position
    dot_node2.hideControlPanel()

    # Create a Shuffle node to the right set 'in' knob to 'processed'
    shuffle_node = nuke.createNode('Shuffle')
    shuffle_node.setInput(0, dot_node)
    shuffle_node['in'].setValue('processed')
    shuffle_node.setXYpos(x_pos + 125, y_pos + 290)  # Adjust xy positions
    shuffle_node.hideControlPanel()

    # Create a Remove node to keep only rgb for left stream
    remove_nodeL = nuke.createNode('Remove')
    remove_nodeL.setInput(0, dot_node2)
    remove_nodeL['operation'].setValue('keep')
    remove_nodeL['channels'].setValue('rgb')
    remove_nodeL.setXYpos(x_pos - 110, y_pos + 350)  # Adjust xy position
    remove_nodeL.hideControlPanel()

    # Create a Remove node to keep only rgb for right stream
    remove_nodeR = nuke.createNode('Remove')
    remove_nodeR.setInput(0, shuffle_node)
    remove_nodeR['operation'].setValue('keep')
    remove_nodeR['channels'].setValue('rgb')
    remove_nodeR.setXYpos(x_pos + 125, y_pos + 350)  # Adjust xy position
    remove_nodeR.hideControlPanel()

    # Create a copyCat node and connect its inputs to rgb/proccessed 
    copyCat_node = nuke.createNode('CopyCat')
    copyCat_node.setInput(1, remove_nodeL)
    copyCat_node.setInput(0, remove_nodeR)
    copyCat_node['checkpointInterval'].setValue(100)
    copyCat_node['imageInterval'].setValue(50)
    copyCat_node.setXYpos(x_pos, y_pos + 500)
    copyCat_node.hideControlPanel()


if __name__ == "__main__":
    x_offset = 300  # Adjust this value to set the horizontal spacing between read nodes
    y_offset = 0  # Adjust this value to set the vertical spacing between read nodes

    x_pos = 0
    y_pos = 0
    copy_nodes = []  # List to store all the created Copy nodes

    for _ in range(num_iterations):
        random_image_path = get_random_image_path(root_directory)
        if random_image_path:
            read_node = create_read_node_with_image(random_image_path, x_pos, y_pos)
            print(f"Created a Read node in Nuke with the file path: {random_image_path}")

            # Increment the position for the next read node
            x_pos += x_offset
            y_pos += y_offset

            # Create and connect the additional nodes for each Read node
            reformat_node1, clamp_node, reformat_node2 = create_and_connect_nodes(read_node)

            # Store the created Copy node in the list
            copy_nodes.append(nuke.toNode('Copy{}'.format(len(copy_nodes) + 1)))

        else:
            print("No image found.")

    append_x_pos = x_pos // 2  # Centrally position append node
    append_y_pos = y_pos + 500  # Lower append node

    # Create the AppendClip node and connect all the Copy nodes to it
    create_append_clip_node(copy_nodes, append_x_pos, append_y_pos)
