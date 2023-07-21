import nuke

def select_and_repath_read_nodes():
    read_nodes = [node for node in nuke.allNodes() if node.Class() == 'Read']
    for node in read_nodes:
        file_path = node['file'].getValue()
        split_path = file_path.split('/')
        if len(split_path) >= 3:
            split_path.insert(2, 'jobs')
            split_path.insert(3, 'glacier-restore')
            new_path = '/'.join(split_path)
            node['file'].setValue(new_path)

def select_and_repath_readgeo_nodes():
    readgeo_nodes = [node for node in nuke.allNodes() if node.Class() == 'ReadGeo2']
    for node in readgeo_nodes:
        file_path = node['file'].getValue()
        split_path = file_path.split('/')
        if len(split_path) >= 3:
            split_path.insert(2, 'jobs')
            split_path.insert(3, 'glacier-restore')
            new_path = '/'.join(split_path)
            node['file'].setValue(new_path)

#UNTESTED - NO CURRENT RESTORE JOBS WITH CAMERAS TO TEST            
'''
def select_and_repath_camera_nodes():
    camera_nodes = [node for node in nuke.allNodes() if node.Class().startswith('Camera')]
    for node in camera_nodes:
        #CHECKING FIRST TO SEE IF THE CAMERA NODE IS READING FROM FILE, OTHERWISE CAN CRASH 
        if node.knob('read_from_file').getValue() == '0.0':
            pass
        else:
            file_path = node['filek'].getValue()
            split_path = file_path.split('/')
            if len(split_path) >= 3:
                split_path.insert(2, 'jobs')
                split_path.insert(3, 'glacier-restore')
                new_path = '/'.join(split_path)
                node['file'].setValue(new_path)
'''

select_and_repath_read_nodes()
select_and_repath_readgeo_nodes()
#select_and_repath_camera_nodes()
