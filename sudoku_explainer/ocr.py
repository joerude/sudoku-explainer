import cv2
import numpy as np


def preprocess_image(image_bytes):
    """Reads image bytes and preprocesses for grid detection."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    return img, gray, thresh


def find_grid_contour(thresh):
    """Finds the largest contour which is likely the Sudoku grid."""
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            return approx
    return None


def order_points(pts):
    """Orders points: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(image, pts):
    """Warps perspective to get a top-down view of the grid."""
    rect = order_points(pts.reshape(4, 2))
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
        dtype="float32",
    )

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


# Template matching fallback
TEMPLATES = {}


def generate_templates():
    """Generates digit templates using OpenCV fonts."""
    global TEMPLATES
    if TEMPLATES:
        return

    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(1, 10):
        template = np.zeros((50, 50), dtype=np.uint8)
        text = str(i)
        (w, h), _ = cv2.getTextSize(text, font, 1.5, 2)
        x = (50 - w) // 2
        y = (50 + h) // 2
        cv2.putText(template, text, (x, y), font, 1.5, 255, 2)

        coords = cv2.findNonZero(template)
        x, y, w, h = cv2.boundingRect(coords)
        template = template[y : y + h, x : x + w]
        TEMPLATES[i] = template


def extract_digit(cell, debug=False):
    """Extracts digit from a cell using Template Matching."""
    thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    h, w = thresh.shape
    thresh = thresh[5 : h - 5, 5 : w - 5]

    if cv2.countNonZero(thresh) < 20:
        return 0

    coords = cv2.findNonZero(thresh)
    if coords is None:
        return 0
    x, y, w, h = cv2.boundingRect(coords)
    roi = thresh[y : y + h, x : x + w]

    target_h = 30
    scale = target_h / h
    target_w = int(w * scale)
    if target_w <= 0 or target_h <= 0:
        return 0

    roi_resized = cv2.resize(roi, (target_w, target_h))

    generate_templates()

    best_score = -1
    # Special handling for '1' which is often thin and misidentified
    # We can try multiple fonts or weights if needed, but for now let's just
    # ensure we have a good template.
    # Also, '1' has a very small area compared to other digits.

    scores = []
    for digit, template in TEMPLATES.items():
        # Resize template to match cell roi
        # We resize the template to the ROI size
        try:
            resized_template = cv2.resize(template, (roi.shape[1], roi.shape[0]))

            # Match
            res = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            # Boost score for '1' if it's a strong match but maybe slightly lower than others due to thinness
            if digit == 1:
                if max_val > 0.6:  # Lower threshold for 1
                    scores.append((max_val * 1.1, digit))  # Boost it
                else:
                    scores.append((max_val, digit))
            else:
                scores.append((max_val, digit))
        except Exception:
            pass

    if not scores:
        return 0

    best_score, best_digit = max(scores, key=lambda x: x[0])

    # Threshold - if best match is too low, it's empty
    # '1' might still be tricky.
    if best_score > 0.5:  # Lowered threshold slightly
        return best_digit
    else:
        return 0


def process_sudoku_image(image_bytes):
    """Main pipeline: Image -> Grid -> Digits -> String."""
    try:
        print(f"[OCR] Processing image: {len(image_bytes)} bytes")
        img, gray, thresh = preprocess_image(image_bytes)
        contour = find_grid_contour(thresh)

        if contour is None:
            print("[OCR] No grid found")
            return None, "Could not find Sudoku grid."

        warped = four_point_transform(gray, contour)

        cells = []
        h, w = warped.shape
        cell_h, cell_w = h // 9, w // 9

        print(f"[OCR] Grid found: {w}x{h}")

        puzzle_str = ""
        for r in range(9):
            for c in range(9):
                y1, y2 = r * cell_h, (r + 1) * cell_h
                x1, x2 = c * cell_w, (c + 1) * cell_w
                cell = warped[y1:y2, x1:x2]
                digit = extract_digit(cell)
                puzzle_str += str(digit)

        print(f"[OCR] Result: {puzzle_str}")
        return puzzle_str, None
    except Exception as e:
        print(f"[OCR] Error: {e}")
        return None, str(e)
