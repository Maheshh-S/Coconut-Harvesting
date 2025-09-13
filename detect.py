from ultralytics import YOLO
import cv2

# Load model
model = YOLO("models/best2.pt")

# Run inference (conf=0.5 means ignore weak predictions)
results = model("ui/IMG_9602_JPG.rf.f03f6d85a855678ce0fc7cb7b31b374e.jpg", conf=0.5)

# Loop over detections
for result in results:
    boxes = result.boxes
    img = result.orig_img.copy()

    for box in boxes:
        # Get coordinates
        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = model.names[cls]

        # Draw box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)

        # Put label + confidence
        text = f"{label} {conf:.2f}"
        cv2.putText(img, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.9, (0,255,0), 2)

    # Save output image
    cv2.imwrite("output.jpg", img)

print("✅ Detection done! Check output.jpg")
