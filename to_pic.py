import fitz
from PIL import Image
import numpy as np

input_pdf = "data/paper_pdf/2110.14553v1.pdf"
output_name = "output.png"

zoom = 8
mat = fitz.Matrix(zoom, zoom)

doc = fitz.open(input_pdf)

page = doc[2]
pix = page.get_pixmap(matrix=mat)
pix.save(output_name)

img = Image.open(output_name)
pix = np.array(img)
print(pix.shape)