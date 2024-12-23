#most
import cv2
import numpy as np
import os
import re  # 用於解析檔名中的數字
import argparse

def classify_ripeness(yellow_ratio, green_ratio, brown_ratio):#定義成熟度
    if (green_ratio > 1 and yellow_ratio < 50) or(green_ratio > 25):
        return "Unripe"
    elif (brown_ratio > 1 and yellow_ratio < 50) or(brown_ratio > 25):
        return "Overripe"
    else:
        return "Moderately Ripe"

def resize_with_padding(image, target_size): #調整照片比例
    h, w = image.shape[:2]
    if h > target_size[0] or w > target_size[1]:
        scale = min(target_size[0] / h, target_size[1] / w)
        new_h, new_w = int(h * scale), int(w * scale)
        resized_image = cv2.resize(image, (new_w, new_h))
        top = (target_size[0] - new_h) // 2
        bottom = target_size[0] - new_h - top
        left = (target_size[1] - new_w) // 2
        right = target_size[1] - new_w - left
        padded_image = cv2.copyMakeBorder(
            resized_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0]
        )
        return padded_image
    else:
        return image

def remove_border_contours(mask, image_shape): #移除偵測到的邊框(非香蕉本體)
    h, w = image_shape[:2]
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        for point in contour:
            x, y = point[0]
            if x <= 1 or y <= 1 or x >= w - 2 or y >= h - 2:
                cv2.drawContours(mask, [contour], -1, 0, thickness=cv2.FILLED)
                break
    return mask

def extract_banana_contour_and_assess():#提取香蕉輪廓並評估
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--directory", required=True, help="Path to the directory containing images")
    args = vars(ap.parse_args())

    alpha = 1.2
    beta = -30
    IMAGE_SIZE = (230, 300)
    image_dir = args["directory"]

    def extract_number(filename):
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    sorted_files = sorted(
        [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".png", ".jpeg"))],
        key=extract_number
    )

    for image_file in sorted_files:
        image_path = os.path.join(image_dir, image_file)
        image = cv2.imread(image_path)
        image = resize_with_padding(image, IMAGE_SIZE)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        blurred = cv2.GaussianBlur(adjusted, (5, 5), 0)

        edges = cv2.Canny(blurred, 10, 400)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        edges_closed = cv2.morphologyEx(cv2.dilate(edges, kernel, iterations=1), cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

        mask = remove_border_contours(mask, image.shape)
        banana = cv2.bitwise_and(image, image, mask=mask)

        hsv = cv2.cvtColor(banana, cv2.COLOR_BGR2HSV)

        lower_yellow = np.array([15, 50, 50])
        upper_yellow = np.array([38, 255, 255])
        lower_brown = np.array([0, 10, 10]) 
        upper_brown = np.array([50, 255, 180])
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([80, 255, 255])

        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        yellow_mask_in_banana = cv2.bitwise_and(yellow_mask, yellow_mask, mask=mask)
        brown_mask_in_banana = cv2.bitwise_and(brown_mask, brown_mask, mask=mask)
        green_mask_in_banana = cv2.bitwise_and(green_mask, green_mask, mask=mask)

        total_pixels = cv2.countNonZero(mask)
        yellow_pixels = cv2.countNonZero(yellow_mask_in_banana)
        brown_pixels = cv2.countNonZero(brown_mask_in_banana)
        green_pixels = cv2.countNonZero(green_mask_in_banana)

        if total_pixels > 0:
            yellow_ratio = (yellow_pixels / total_pixels) * 100
            brown_ratio = (brown_pixels / total_pixels) * 100
            green_ratio = (green_pixels / total_pixels) * 100
        else:
            yellow_ratio = brown_ratio = green_ratio = 0

        ripeness = classify_ripeness(yellow_ratio, green_ratio, brown_ratio)

        print(f"Image: {image_file}")
        print(f"Yellow Area Ratio: {yellow_ratio:.2f}%")
        print(f"Brown Area Ratio: {brown_ratio:.2f}%")
        print(f"Green Area Ratio: {green_ratio:.2f}%")
        print(f"Ripeness: {ripeness}")

        cv2.imshow("Original Image", image)
        cv2.imshow("Edges", edges_closed)
        cv2.imshow("Banana Mask", mask)
        cv2.imshow("Yellow Mask", yellow_mask_in_banana)
        cv2.imshow("Brown Mask", brown_mask_in_banana)
        cv2.imshow("Green Mask", green_mask_in_banana)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    extract_banana_contour_and_assess()
