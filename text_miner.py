from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import re
import fitz
from PyPDF2 import PdfFileReader


test_pdf = "data/paper_pdf/2110.14553v1.pdf"
fp = open(test_pdf, 'rb')
pypdf_file = PdfFileReader(open(test_pdf, 'rb'))
if pypdf_file:
    print(pypdf_file.getPage(0).mediaBox)
    print()

rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
pages = PDFPage.get_pages(fp)
pattern = re.compile("^(Figure|Fig).? ?\d+")

MINX, MAXX = 10000, 0
MINY, MAXY = 10000, 0

for page in pages:
    # print('Processing next page...')
    interpreter.process_page(page)
    layout = device.get_result()
    for lobj in layout:
        # print(type(lobj).__name__)
        x, y = lobj.bbox[0], lobj.bbox[3]  ## 54, 593
        if isinstance(lobj, LTTextBox):
            x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
            # print('At %r is text: %s' % ((x, y), text))
            
            if re.match(pattern, text):

                x1, y1 = lobj.bbox[1], lobj.bbox[2]
                if (x1 - x) > 612 / 2 + 20:
                    column = 2
                else:
                    column = 1

                print(x, y, text)

        MINX, MAXX, MINY, MAXY = min(MINX, x), max(MAXX, x), min(MINY, y), max(MAXY, y)
print(MINX, MAXX, MINY, MAXY)