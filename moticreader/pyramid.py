# pyramid.py
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from PIL import Image, TiffTags, TiffImagePlugin
import io
import numpy as np
import tifffile
class PyramidLayer:
    def __init__(self, level, rows, cols, tile_width, tile_height, grid, parent_pyramid):
       self.level = level
       self.rows = rows
       self.cols = cols
       self.tile_width = tile_width
       self.tile_height = tile_height
       self.grid = grid
       self.parent_pyramid = parent_pyramid

    def process_tile(self, task):
        row, col, tile_name, tile_width, tile_height = task
        try:
            stream = self.parent_pyramid.ole.openstream(tile_name)
            image_data = stream.read()
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            return row, col, image
        except Exception as e:
            print(f"Error loading tile {tile_name} from layer {self.level}: {e}")
            return row, col, None


    def get_tile_image(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            tile_name = self.grid[row][col]
            if tile_name:
                try:
                    stream = self.parent_pyramid.ole.openstream(tile_name)
                    image_data = stream.read()
                    image = Image.open(io.BytesIO(image_data))
                    return image
                except Exception as e:
                    print(f"Error loading tile {tile_name} from layer {self.level}: {e}")
        return None

    def get_layer_image(self):
       layer_width = self.cols * self.tile_width
       layer_height = self.rows * self.tile_height
       layer_image = Image.new('RGB', (layer_width, layer_height))
    
       for row in range(self.rows):
           for col in range(self.cols):
               tile_image = self.get_tile_image(row, col)
               if tile_image:
                   x_offset = col * self.tile_width
                   y_offset = row * self.tile_height
                   layer_image.paste(tile_image, (x_offset, y_offset))
    
       return layer_image

    def get_layer_image_multprocess(self, num_threads=None):
        layer_width = self.cols * self.tile_width
        layer_height = self.rows * self.tile_height
        layer_image = Image.new('RGB', (layer_width, layer_height))

        tasks = [(row, col, self.grid[row][col], self.tile_width, self.tile_height)
                 for row in range(self.rows) for col in range(self.cols) if self.grid[row][col]]
        max_threads = num_threads
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(self.process_tile, task) for task in tasks]
            for future in as_completed(futures):
                row, col, tile_image = future.result()
                if tile_image is not None:
                    x_offset = col * self.tile_width
                    y_offset = row * self.tile_height
                    layer_image.paste(tile_image, (x_offset, y_offset))

        return layer_image





class ImagePyramid:
    def __init__(self, micrometres_per_pixel_x, micrometres_per_pixel_y,ole):
        self.layers = []
        self.micrometres_per_pixel_x = micrometres_per_pixel_x
        self.micrometres_per_pixel_y = micrometres_per_pixel_y
        self.ole = ole

    def add_layer(self, level, grid, tile_width, tile_height):
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        layer = PyramidLayer(level, rows, cols, tile_width, tile_height, grid, self)
        self.layers.append(layer)

    def get_tile_image(self, level, row, col):
        layer = self.get_layer(level)
        if layer:
            return layer.get_tile_image(row, col)
        return None

    def get_layer(self, level):
        for layer in self.layers:
            if layer.level == level:
                return layer
        return None
    def get_layer_image(self, level):
        layer = self.get_layer(level)
        if layer:
            return layer.get_layer_image()
        return None

    def get_layer_image_multprocess(self, level, num_threads=None):
        layer = self.get_layer(level)
        if layer:
            return layer.get_layer_image_multprocess(num_threads=num_threads)
        return None

    def save_as_tiff(self, filename):
  
        layers = [self.get_layer_image(level) for level in range(len(self.layers))]

        base_image = layers[0]

        info = TiffImagePlugin.ImageFileDirectory_v2()

        
        info = TiffImagePlugin.ImageFileDirectory_v2()

        
        info[282] = (self.micrometres_per_pixel_x, 1)  # 282 is the tag for X_RESOLUTION
        info[283] = (self.micrometres_per_pixel_y, 1)  # 283 is the tag for Y_RESOLUTION
        info[296] = 3  # 296 is the tag for RESOLUTION_UNIT, 3

       
        info[270] = "Layer 0 Resolution: {}x{}".format(  # 270 is the tag for IMAGE_DESCRIPTION
            self.micrometres_per_pixel_x, self.micrometres_per_pixel_y
        )
    
        base_image.save(
            filename,
            save_all=True,
            append_images=layers[1:],
            compression="tiff_deflate",
            bigtiff=True,
            tiffinfo=info            
        )


    def __str__(self):
        return f"Pyramid with {self.total_layers} layers, " \
               f"width: {self.width} micrometres, height: {self.height} micrometres"

