import cv2
import numpy as np


def generate_status_heatmap(image: np.ndarray, box_status_logs: list) -> np.ndarray:
    """
    Generates a heatmap overlay on the input image based on status activity in bounding boxes.

    Args:
        image (np.ndarray): The original image (BGR format).
        box_status_logs (list): List of tuples in the form ((x1, y1, x2, y2), status)

    Returns:
        np.ndarray: Image with heatmap overlay (BGR format).
    """
    height, width = image.shape[:2]
    print(box_status_logs)

    # Status weights
    status_weights = {
        "EMPTY": 0.2,
        "IDLE": 0.6,
        "WORKING": 2.0,
    }

    # Initialize heatmap
    heatmap = np.zeros((height, width), dtype=np.float32)

    # Accumulate weighted values into heatmap
    for (x1, y1, x2, y2), status in box_status_logs:
        weight = status_weights.get(status, 0.0)
        print(f"Adding weight {weight} to box ({x1}, {y1}, {x2}, {y2})")
        heatmap[y1:y2, x1:x2] += weight

    # Smooth the heatmap
    heatmap = cv2.GaussianBlur(heatmap, (45, 45), 0)

    # Normalize heatmap
    if heatmap.max() > 0:
        heatmap_norm = np.clip(heatmap / heatmap.max(), 0, 1)
    else:
        heatmap_norm = heatmap

    heatmap_uint8 = (heatmap_norm * 255).astype(np.uint8)

    # Apply color map
    colored_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

    # Blend with original image
    overlay = cv2.addWeighted(image, 0.6, colored_heatmap, 0.4, 0)

    return overlay


if __name__ == "__main__":
    # Example usage
    image = cv2.imread("./in.jpg")
    box_status_logs = [
        ((165, 456, 349, 713), "WORKING"),
        ((255, 356, 449, 813), "WORKING"),
        
    ]

    heatmap_image = generate_status_heatmap(image, box_status_logs)
    cv2.imshow("Heatmap", heatmap_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
