import nuke

def add_directories_after_jobs():
    read_nodes = [node for node in nuke.allNodes() if node.Class() == 'Read']
    for node in read_nodes:
        node.setSelected(True)
    for node in read_nodes:
        file_path = node['file'].getValue()
        split_path = file_path.split('/')
        if len(split_path) >= 3:
            split_path.insert(2, 'jobs')
            split_path.insert(3, 'glacier-restore')
            new_path = '/'.join(split_path)
            node['file'].setValue(new_path)

add_directories_after_jobs()
