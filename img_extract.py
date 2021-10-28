# STEP 1
# import libraries
import fitz
import io
from PIL import Image

# STEP 2
# file path you want to extract images from
file = "/Users/lixj/Project/Arxiv-Scraper/data/paper_pdf/2110.14553v1.pdf"

# open the file
pdf_file = fitz.open(file)

# STEP 3
# iterate over PDF pages
for page_index in range(len(pdf_file)):

    # get the page itself
    page = pdf_file[page_index]
    image_list = page.get_images()

    text = page.get_text()
    lines = text.split('\n')
    lines = [line[:-1] if line.endswith('-') else line for line in lines]
    print(" ".join(lines))

    # printing number of images found in this page
    if image_list:
        print(
            f"[+] Found a total of {len(image_list)} images in page {page_index}")
    else:
        print("[!] No images found on page", page_index)
    for image_index, img in enumerate(page.get_images(), start=1):

        # get the XREF of the image
        xref = img[0]
        pix = fitz.Pixmap(pdf_file, xref)

        # extract the image bytes
        base_image = pdf_file.extractImage(xref)
        image_bytes = base_image["image"]

        # get the image extension
        image_ext = base_image["ext"]

        if pix.n < 5:       # this is GRAY or RGB
            pix.writePNG("p%s-%s.png" % (page_index, xref))
        else:               # CMYK: convert to RGB first
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            pix1.writePNG("p%s-%s.png" % (page_index, xref))
            pix1 = None
