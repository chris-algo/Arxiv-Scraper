from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import re
import fitz
from PyPDF2 import PdfFileReader, pdf
from PIL import Image
import os
import numpy as np
from pdfminer.pdfparser import PDFParser
import json


class Figure:
    def __init__(self, image_title, pdf_id, image_path,
                 page_index, figure_index, x_left, x_right, y_top, y_bottom, image_zoom) -> None:
        self.image_title = image_title
        self.image_path = image_path
        self.page_index = page_index
        self.figure_index = figure_index
        self.x_left = x_left
        self.x_right = x_right
        self.y_top = y_top
        self.y_bottom = y_bottom
        self.image_zoom = image_zoom

    def to_dict(self):
        data = {
            "image_title": self.image_title,
            "image_path": self.image_path,
            "page_index": self.page_index,
            "figure_index": self.figure_index,
            "x_left": self.x_left,
            "x_right": self.x_right,
            "y_top": self.y_top,
            "y_bottom": self.y_bottom,
            "image_zoom": self.image_zoom
        }
        return data


class PDFProcessor:
    def __init__(self, pdf_path, img_zoom, img_save_dir, json_save_dir):
        self.pdf_path = pdf_path
        self.pdf_id = os.path.split(self.pdf_path)[-1][:-4]
        self.img_zoom = img_zoom
        self.pdf_binary = open(self.pdf_path, 'rb')
        self.fitz_mat = fitz.Matrix(self.img_zoom, self.img_zoom)
        self.fitz_doc = fitz.open(self.pdf_path)

        self.img_save_dir = os.path.join(
            img_save_dir, os.path.split(pdf_path)[-1][:-4])

        if not os.path.exists(self.img_save_dir):
            os.makedirs(self.img_save_dir)

        self.tmp_page_path_root = "./temp/temp.png"
        self.tmp_page_path = None
        self.pattern = re.compile("^(Figure|Fig).? ?\d+")
        self.margin_cut = 40
        self.img_x, self.img_y = 0, 0

        # pdf miner
        self.rsrcmgr = PDFResourceManager()
        self.laparams = LAParams()
        self.device = PDFPageAggregator(self.rsrcmgr, laparams=self.laparams)
        self.miner_pages = [
            page for page in PDFPage.get_pages(self.pdf_binary)]
        self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)
        self.figure_dict = {}
        self.json_path = os.path.join(json_save_dir, self.pdf_id) + '.json'

    def text_process(self, text: str):
        text = text.replace('\n', ' ').strip()
        return text

    def page_to_png(self, page, page_index):
        pix = page.get_pixmap(matrix=self.fitz_mat)
        self.tmp_page_path = self.tmp_page_path_root[:-4] + str(
            page_index) + self.tmp_page_path_root[-4:]
        pix.save(self.tmp_page_path)

    def get_text(self, miner_page):
        self.interpreter.process_page(miner_page)
        page_layout = self.device.get_result()
        for lobj in page_layout:
            x, y = lobj.bbox[0], lobj.bbox[3]  # 54, 593
            if isinstance(lobj, LTTextBox):
                text = lobj.get_text()
                # print('At %r is text: %s' % ((x, y), text))

                if re.match(self.pattern, text):

                    x1, y1 = lobj.bbox[2], lobj.bbox[1]
                    if x < self.img_y / 2 and x1 > self.img_y / 2:
                        column = 2
                    else:
                        column = 1

                    # print(x, y, text)
                    yield (x, y, text, column)

    def save_figure_one(self, pix, x, y, text, column, image_path):
        x, y = int(y), int(x)
        x = 792 - x

        def black_white(pix, white_thresh=250, black_thresh=5):
            r, g, b = pix
            # print(pix)
            if r >= white_thresh and g >= white_thresh and b >= white_thresh:
                return "white"
            elif r <= black_thresh and g <= black_thresh and b <= black_thresh:
                return "black"
            return "others"

        y_index_left = 0 + self.margin_cut
        y_index_right = self.img_y - self.margin_cut
        if column == 2:
            y_range = range(self.img_y)
        else:
            if y < self.img_y / 2:
                y_range = range(self.img_y // 2)
                y_index_right = self.img_y // 2
            else:
                y_range = range(self.img_y // 2, self.img_y)
                y_index_left = self.img_y // 2

        for index_x in range(x, 1, -1):
            for index_y in y_range:
                current_y = index_y * self.img_zoom
                current_x = index_x * self.img_zoom
                if black_white(pix[current_x, current_y]) is "others":
                    bottom = index_x
                    break

        white_count = 0
        for index_x in range(bottom - 1, 0, -1):
            all_white = True
            for index_y in y_range:
                current_y = index_y * self.img_zoom
                current_x = index_x * self.img_zoom
                # print(index_x, index_y)
                color = black_white(pix[current_x, current_y])
                if color is "others" or color is "black":
                    all_white = False
                    break
            if all_white:
                white_count += 1
            else:
                white_count = 0
            if white_count >= 4:
                top = index_x
                break

        bottom = x
        top, bottom = top * self.img_zoom, bottom * self.img_zoom
        y_index_left, y_index_right = y_index_left * \
            self.img_zoom, y_index_right * self.img_zoom
        # print(top, bottom, y_index_left, y_index_right)
        img = Image.fromarray(pix[top:bottom, y_index_left:y_index_right, :])
        img.save(image_path)
        return top, bottom, y_index_left, y_index_right

    def save_figure(self):
        figure_count = 1
        for page_index, page in enumerate(self.fitz_doc):
            self.page_to_png(page, page_index)
            img = Image.open(self.tmp_page_path)
            pix = np.array(img)
            self.img_x, self.img_y = pix.shape[0] // self.img_zoom, pix.shape[1] // self.img_zoom

            miner_page = self.miner_pages[page_index]
            for (x, y, text, column) in self.get_text(miner_page):
                image_path = f"{self.img_save_dir}/page{page_index}-figure{figure_count}.png"
                top, bottom, y_index_left, y_index_right = self.save_figure_one(
                    pix, x, y, text, column, image_path)
                text = self.text_process(text)
                self.figure_dict[figure_count] = Figure(
                    text, self.pdf_id, image_path, page_index, figure_count, top, bottom, y_index_left, y_index_right, self.img_zoom).to_dict()
                figure_count += 1
        json_str = json.dumps(self.figure_dict, indent=4)
        with open(self.json_path, 'w') as json_file:
            print(json_str, file=json_file)


def test():
    pdfparser = PDFProcessor(
        "data/paper_pdf/2107.03721v2.pdf", 8, "data/paper_imgs", "data/images_json")
    pdfparser.save_figure()

    pdfparser = PDFProcessor(
        "data/paper_pdf/2107.03851v1.pdf", 8, "data/paper_imgs", "data/images_json")
    pdfparser.save_figure()

    pdfparser = PDFProcessor(
        "data/paper_pdf/2107.03961v2.pdf", 8, "data/paper_imgs", "data/images_json")
    pdfparser.save_figure()

    pdfparser = PDFProcessor(
        "data/paper_pdf/2107.04086v2.pdf", 8, "data/paper_imgs", "data/images_json")
    pdfparser.save_figure()

    pdfparser = PDFProcessor(
        "data/paper_pdf/2107.04169v1.pdf", 8, "data/paper_imgs", "data/images_json")
    pdfparser.save_figure()

if __name__ == "__main__":
    test()
