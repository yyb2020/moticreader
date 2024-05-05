# trans.py


import olefile
from collections import defaultdict
from .pyramid import ImagePyramid, PyramidLayer		
from PIL import Image
import io
def is_conforming(item):
    return len(item) == 3 and '_' in item[2]

def get_tiles_for_level(level, group_index, grouped_data):
    for key, index in group_index.items():
        if index == level:
            return grouped_data[key]
    return None




def extract_scale_value(xml_data):

    parts = xml_data.split('/>')

    for part in parts:
        if '<Scale' in part:
            
            start_idx = part.find('value="') + len('value="')
          
            end_idx = part.find('"', start_idx)
            scale_value = part[start_idx:end_idx]
            return scale_value

 
    return None
    
def parse_tile_position(tile_name):
    row, col = map(int, tile_name.split('_'))
    return row, col

def organize_into_grid(tiles):
    
    rows = []
    cols = []
    for tile in tiles:
        row, col = parse_tile_position(tile[2])
        rows.append(row)
        cols.append(col)

    max_row = max(rows)
    max_col = max(cols)

  
    grid = [[None for _ in range(max_col + 1)] for _ in range(max_row + 1)]

    for tile in tiles:
        row, col = parse_tile_position(tile[2])
        grid[row][col] = tile

    return grid , max_row , max_col

def readfile(path):
	
	ole = olefile.OleFileIO(path)
	ole_content = ole.listdir()
	
	conforming_elements = [item for item in ole_content if is_conforming(item)]
	non_conforming_elements = [item for item in ole_content if not is_conforming(item)]
	
	
	grouped_data = defaultdict(list)
	
	for item in conforming_elements:
	    grouped_data[item[1]].append(item)
	
	
	sorted_group_keys = sorted(grouped_data.keys(), key=float, reverse=True)
	
	
	group_index = {}
	for index, key in enumerate(sorted_group_keys):
	    group_index[key] = index
	maxlevel = max(group_index.values())

	streamnn = ole.openstream(['Property'])
	datann = streamnn.read()


	decoded_datann = datann.decode('utf-16')
	scale_value = extract_scale_value(decoded_datann)


	micrometres_per_pixel_x =scale_value  
	micrometres_per_pixel_y =scale_value 
	pyramid = ImagePyramid(micrometres_per_pixel_x, micrometres_per_pixel_y,ole)

	
	for level in  group_index.values():
	
		tiles = get_tiles_for_level(level,group_index, grouped_data)
	
		stream = ole.openstream(tiles[0])
		
		
		image_data = stream.read()
		image = Image.open(io.BytesIO(image_data))
		
		
		tilewidth, tileheight = image.size
		grid , max_row , max_col = organize_into_grid(tiles)
		pyramid.add_layer(level, grid, tilewidth, tileheight)
	
	return pyramid
	
	
	

























