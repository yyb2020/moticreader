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

#olenn = olefile.OleFileIO("/home/Yangyb/data5/yunxing/deeplearning/3dnew/yssj/lung/1-1/1.mds")
#streamnn = olenn.openstream(['DSI0', '0.017803', '0000_0000'])
#image_datann = streamnn.read()
#imagenn = Image.open(io.BytesIO(image_datann))


def extract_scale_value(xml_data):
    """
    Extract the value of the Scale attribute from the XML data.
    :param xml_data: A string containing the XML data.
    :return: The extracted Scale value as a string, or None if not found.
    """
    # 按照 "/>" 分割
    parts = xml_data.split('/>')

    for part in parts:
        if '<Scale' in part:
            # 查找 value 的起始位置
            start_idx = part.find('value="') + len('value="')
            # 查找 value 的结束位置
            end_idx = part.find('"', start_idx)
            # 提取 Scale 值
            scale_value = part[start_idx:end_idx]
            return scale_value

    # 如果找不到 Scale 标签，返回 None
    return None
    
def parse_tile_position(tile_name):
    row, col = map(int, tile_name.split('_'))
    return row, col

def organize_into_grid(tiles):
    # 提取所有行和列的坐标
    rows = []
    cols = []
    for tile in tiles:
        row, col = parse_tile_position(tile[2])
        rows.append(row)
        cols.append(col)

    # 计算最大行和列
    max_row = max(rows)
    max_col = max(cols)

    # 创建一个空的二维列表来表示表格
    grid = [[None for _ in range(max_col + 1)] for _ in range(max_row + 1)]

    # 填充表格
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
	
	# 对组按照第二个元素从大到小进行排序
	sorted_group_keys = sorted(grouped_data.keys(), key=float, reverse=True)
	
	# 为每个组分配一个整数索引，0对应值为1的组，逐渐减少为整数增加
	group_index = {}
	for index, key in enumerate(sorted_group_keys):
	    group_index[key] = index
	maxlevel = max(group_index.values())

	streamnn = ole.openstream(['Property'])
	datann = streamnn.read()
	# 解码UTF-16编码的数据
	decoded_datann = datann.decode('utf-16')
	scale_value = extract_scale_value(decoded_datann)
	# 创建 ImagePyramid 实例
	micrometres_per_pixel_x =scale_value  # 可根据实际情况修改
	micrometres_per_pixel_y =scale_value # 可根据实际情况修改
	pyramid = ImagePyramid(micrometres_per_pixel_x, micrometres_per_pixel_y,ole)

	
	for level in  group_index.values():
	
		tiles = get_tiles_for_level(level,group_index, grouped_data)
		# 使用openstream打开指定路径的流
		stream = ole.openstream(tiles[0])
		
		# 将二进制数据转换为图像
		image_data = stream.read()
		image = Image.open(io.BytesIO(image_data))
		
		# 获取图像的宽度和高度
		tilewidth, tileheight = image.size
		grid , max_row , max_col = organize_into_grid(tiles)
		pyramid.add_layer(level, grid, tilewidth, tileheight)
	
	return pyramid
	
	
	

























