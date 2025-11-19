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
        # Create a black image
        template = np.zeros((50, 50), dtype=np.uint8)
        # Draw digit centered
        text = str(i)
        (w, h), _ = cv2.getTextSize(text, font, 1.5, 2)
        x = (50 - w) // 2
        y = (50 + h) // 2
        cv2.putText(template, text, (x, y), font, 1.5, 255, 2)

        # Crop to bounding box
        coords = cv2.findNonZero(template)
        x, y, w, h = cv2.boundingRect(coords)
        template = template[y : y + h, x : x + w]
        TEMPLATES[i] = template


def extract_digit(cell, debug=False):
    """Extracts digit from a cell using Template Matching."""
    # Preprocess cell
    thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Clear borders to remove grid lines
    h, w = thresh.shape
    thresh = thresh[5 : h - 5, 5 : w - 5]

    # Check if empty
    if cv2.countNonZero(thresh) < 20:  # Threshold for noise
        return 0

    # Find bounding box of the digit in the cell
    coords = cv2.findNonZero(thresh)
    if coords is None:
        return 0
    x, y, w, h = cv2.boundingRect(coords)
    roi = thresh[y : y + h, x : x + w]

    # Resize ROI to a standard height for comparison, maintaining aspect ratio
    target_h = 30
    scale = target_h / h
    target_w = int(w * scale)
    if target_w <= 0 or target_h <= 0:
        return 0

    roi_resized = cv2.resize(roi, (target_w, target_h))

    # Generate templates if needed
    generate_templates()

    best_score = -1
    best_digit = 0

    for digit, template in TEMPLATES.items():
        # Resize template to match ROI height
        t_h, t_w = template.shape
        if t_h == 0 or t_w == 0:
            continue

        scale_t = target_h / t_h
        t_w_new = int(t_w * scale_t)
        template_resized = cv2.resize(template, (t_w_new, target_h))

        # Match shapes must be similar
        if abs(t_w_new - target_w) > 10:
            continue

        # Resize template to exactly match ROI for simple subtraction/correlation
        try:
            template_matched = cv2.resize(template, (target_w, target_h))

            # Simple correlation
            score = cv2.matchTemplate(
                roi_resized, template_matched, cv2.TM_CCOEFF_NORMED
            )[0][0]

            if score > best_score:
                best_score = score
                best_digit = digit
        except:
            continue

    if best_score > 0.4:  # Confidence threshold
        return best_digit
    return 0


def process_sudoku_image(image_bytes):
    """Main pipeline: Image -> Grid -> Digits -> String."""
    try:
        img, gray, thresh = preprocess_image(image_bytes)
        contour = find_grid_contour(thresh)

        if contour is None:
            return None, "Could not find Sudoku grid."

        warped = four_point_transform(gray, contour)

        # Split into 81 cells
        cells = []
        h, w = warped.shape
        cell_h, cell_w = h // 9, w // 9

        puzzle_str = ""
        for r in range(9):
            for c in range(9):
                y1, y2 = r * cell_h, (r + 1) * cell_h
                x1, x2 = c * cell_w, (c + 1) * cell_w
                cell = warped[y1:y2, x1:x2]
                digit = extract_digit(cell)
                puzzle_str += str(digit)

        return puzzle_str, None
    except Exception as e:
        return None, str(e)
