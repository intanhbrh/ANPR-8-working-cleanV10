from easyocr import Reader

reader = Reader(['en'], gpu=True)


def read_text(image, x1, y1, x2, y2):
    return reader.readtext(image[y1:y2, x1:x2], paragraph=True)

'''def read_text(image):
    return reader.readtext(image, paragraph=True)
'''

