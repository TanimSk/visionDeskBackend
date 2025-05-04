import cv2
import numpy as np
import random

def apply_random_status_heatmap(image_path, num_boxes=5, shrink_ratio=0.1):
    """
    Randomly generate bounding boxes and apply heatmap overlay based on status.

    :param image_path: Path to the input image.
    :param num_boxes: Number of random boxes to draw.
    :param shrink_ratio: Percentage to shrink each bounding box for the heatmap.
    :return: Image with heatmap overlay.
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    height, width, _ = image.shape

    overlay = image.copy()

    status_colors = {
        0: (0, 0, 255),     # Red - not available
        1: (0, 255, 0),     # Green - working
        2: (0, 255, 255)    # Yellow - idle
    }

    for _ in range(num_boxes):
        box_width = random.randint(60, 80)
        box_height = random.randint(60, 80)
        x1 = random.randint(0, width - box_width)
        y1 = random.randint(0, height - box_height)
        x2 = x1 + box_width
        y2 = y1 + box_height
        status = random.choice(list(status_colors.keys()))

        # Shrink box
        dw = int(box_width * shrink_ratio / 2)
        dh = int(box_height * shrink_ratio / 2)
        sx1, sy1 = x1 + dw, y1 + dh
        sx2, sy2 = x2 - dw, y2 - dh

        color = status_colors[status]
        cv2.rectangle(overlay, (sx1, sy1), (sx2, sy2), color, -1)

    alpha = 0.5
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    return image

# Example usage
if __name__ == "__main__":
    image_path = "./in.jpg"  # Replace with your actual image path
    result = apply_random_status_heatmap(image_path, num_boxes=6)
    cv2.imshow("Random Heatmap Overlay", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()