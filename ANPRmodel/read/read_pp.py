import paddleocr
ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang="en", use_gpu=True)
def read_text(image, x1, y1, x2, y2):
    return ocr.ocr(image[y1:y2, x1:x2])

'''def read_text(image):
    return ocr.ocr(image)[0][0][-1][0]'''