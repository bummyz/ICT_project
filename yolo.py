import torch
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from yolov5 import YOLOv5

model = YOLOv5('yolov5s.pt')  # YOLOv5s 모델을 로드합니다.


def preprocess_image(image_path):
    # 이미지를 로드합니다.
    img = Image.open(image_path)

    # 전처리 과정을 정의합니다.
    preprocess = transforms.Compose([
        transforms.Resize((640, 640)),  # YOLOv5 입력 크기
        transforms.ToTensor(),  # 텐서로 변환
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # 정규화
    ])

    img = preprocess(img)
    img = img.unsqueeze(0)  # 배치 차원 추가
    return img


image_path = 'path_to_your_image.jpg'
input_img = preprocess_image(image_path)


def detect_objects(model, input_img):
    # 모델에 이미지를 입력하여 탐지 결과를 얻습니다.
    results = model(input_img)

    # 결과를 디코딩합니다.
    predictions = results.pred[0]
    return predictions


predictions = detect_objects(model, input_img)


def visualize_detections(image_path, predictions, threshold=0.5):
    img = cv2.imread(image_path)
    for pred in predictions:
        if pred[4] > threshold:  # confidence score threshold
            x1, y1, x2, y2 = int(pred[0]), int(pred[1]), int(pred[2]), int(pred[3])
            label = int(pred[5])
            confidence = pred[4].item()

            # 바운딩 박스를 그립니다.
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f'Class: {label}, Conf: {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (0, 255, 0), 2)

    # 이미지를 출력합니다.
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()


visualize_detections(image_path, predictions)
