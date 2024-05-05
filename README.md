moticreader 
---
moticreader是一个读取由MOTIC扫描仪生成的.mds格式病理图像的python包，可以读取并保存图像至本地。  
moticreader is a Python package that allows viewing and saving whole slide images and microscopy data in the .mds format, which are generated by MOTIC scanners.

安装 Installation from source
---

```{python}
pip install moticreader
```

使用 How to use
--
读取.mds文件 Read the .mds file
```{python}
from moticreader import readfile
path = ".../*.mds"
pyramid = readfile(path)
```

获得第n层（level）的图像 Obtain the image of level n
```{python}
layer_image = pyramid.get_layer_image(level = n)
```

保存第n层（level）的图像 Save the image of level n
```{python}
layer_image.save(".../*.png", format='PNG')
```

整体保存为tiff格式图像 Save the entire image as tiff image
```{python}
pyramid.save_as_tiff(".../*.tiff")
```
