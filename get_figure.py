from PIL import Image
import numpy as np

img_path = "output.png"
zoom = 8
x, y = 593, 54
x = 792 - x


img = Image.open(img_path)
pix = np.array(img)
print(pix.shape)


def black_white(pix, white_thresh=200, black_thresh=50):
    r, g, b = pix
    # print(pix)
    if r >= white_thresh and g >= white_thresh and b >= white_thresh:
        return "white"
    elif r <= black_thresh and g <= black_thresh and b <= black_thresh:
        return "black"
    return "others"


for index_x in range(x, 1, -1):
    # print(index_y)
    for index_y in range(pix.shape[1] // zoom):
        current_y = index_y * zoom
        current_x = index_x * zoom
        if black_white(pix[current_x, current_y]) is "others":
            bottom = index_x * zoom
            # print(bottom)
            break

print(bottom)

top = None
for index_x in range(bottom - 1, 0, -1):
    # print("---", index_x)
    all_white = True
    for index_y in range(pix.shape[1] // zoom):
        current_y = index_y * zoom
        current_x = index_x * zoom
        color = black_white(pix[current_x, current_y])
        if color is "others" or color is "black":
            all_white = False
            break
    if all_white:
        top = index_x * zoom
        break
top -= 5

bottom = 792 - 593
print(x, y, top, bottom)
Image.fromarray(pix[top:bottom, :, :]).save("output_1.png")
