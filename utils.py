import cv2 as cv
import numpy as np


def read_image(img_path: str) -> np.ndarray:
    """
    Read and convert an image to BGRA format.

    :param img_path: Path to the image file.
    :return: BGRA formatted image.
    """
    img = cv.imread(img_path, cv.IMREAD_UNCHANGED)
    return cv.cvtColor(img, cv.COLOR_BGR2BGRA)


def write_image(img: np.ndarray, output_path: str):
    """
    Save the rendered image to a file.

    :param img: Image to save.
    :param output_path: Path to save the image.
    """
    cv.imwrite(output_path, img)
