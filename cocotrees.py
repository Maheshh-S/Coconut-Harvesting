from ultralytics import YOLO
import cv2
import json
import uuid

# ===============================
# Load trained YOLO model
# ===============================
model = YOLO("models/besttt0.pt")   # <- use your trained weights

# ===============================
# Input / Output paths
# ===============================
img_path = "test/000108_jpg.rf.329d058a2d867ea688e8608024a02716.jpg"
output_img = "output.jpg"
output_json = "output.json"

# ===============================
# Run inference
# ===============================
results = model(img_path, conf=0.5)

final_output = {"predictions": []}

# Work on original image
for result in results:
    boxes = result.boxes
    img = result.orig_img.copy()

    for box in boxes:
        # Convert to int/float values
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = model.names[cls]

        # Convert to width/height style (like Roboflow JSON)
        width = x2 - x1
        height = y2 - y1
        x_center = x1 + width / 2
        y_center = y1 + height / 2

        # Draw rectangle + confidence
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        text = f"{label} {conf:.2f}"
        cv2.putText(img, text, (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Append to JSON with detection_id
        final_output["predictions"].append({
            "x": round(x_center, 1),
            "y": round(y_center, 1),
            "width": round(width, 1),
            "height": round(height, 1),
            "confidence": round(conf, 3),
            "class": label,
            "class_id": cls,
            "detection_id": str(uuid.uuid4())  # unique ID
        })

# Save annotated image
cv2.imwrite(output_img, img)

# Save JSON
with open(output_json, "w") as f:
    json.dump(final_output, f, indent=2)

print(f"✅ Detection complete!\n- Image saved at: {output_img}\n- JSON saved at: {output_json}")
