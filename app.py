import os
import uuid
import json
import cv2
from flask import Flask, request, render_template, jsonify, send_from_directory
from ultralytics import YOLO

# =======================
# Firebase setup
# =======================
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Load service account from Secret File (Render mounts it)
FIREBASE_KEY_FILE = "firebase-key.json"
cred = credentials.Certificate(FIREBASE_KEY_FILE)
firebase_admin.initialize_app(cred)
db = firestore.client()

# =======================
# Flask setup
# =======================
app = Flask(__name__, template_folder="ui", static_folder="ui", static_url_path="")

# =======================
# Load YOLO models
# =======================
models = {
    "cocotrees": YOLO("models/besttt0.pt"),  # tree detection model
    "coconuts": YOLO("models/best2.pt")      # coconut detection model
}

# =======================
# Utility function
# =======================
def run_inference(model_key, img_path, output_dir):
    model = models[model_key]
    results = model(img_path, conf=0.5)
    predictions = []

    for result in results:
        boxes = result.boxes
        img = result.orig_img.copy()

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]
            det_id = str(uuid.uuid4())

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text = f"{label} {conf:.2f}"
            cv2.putText(img, text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Save prediction
            predictions.append({
                "x": int((x1 + x2) / 2),
                "y": int((y1 + y2) / 2),
                "width": int(x2 - x1),
                "height": int(y2 - y1),
                "confidence": round(conf, 3),
                "class": label,
                "class_id": cls,
                "detection_id": det_id
            })

        # Save annotated image
        out_name = f"{uuid.uuid4().hex}.jpg"
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, out_name)
        cv2.imwrite(out_path, img)

        # Save predictions as JSON (optional)
        json_path = out_path.replace(".jpg", ".json")
        with open(json_path, "w") as f:
            json.dump({"predictions": predictions}, f, indent=4)

        # ✅ Store in Firestore
        db.collection(model_key).document().set({
            "filename": out_name,
            "predictions": predictions,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

    return out_name, predictions

# =======================
# Routes
# =======================
@app.route("/")
def home():
    return "<h2>Go to <a href='/cocotrees'>CocoTrees</a> or <a href='/coconuts'>Coconuts</a></h2>"

@app.route("/cocotrees")
def cocotrees_page():
    return render_template("cocotrees.html")

@app.route("/coconuts")
def coconuts_page():
    return render_template("coconuts.html")

@app.route("/detect/<project>", methods=["POST"])
def detect(project):
    if project not in models:
        return jsonify({"error": "Invalid project"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty file name"}), 400

    # Save temporarily
    tmp_path = os.path.join("ui", file.filename)
    file.save(tmp_path)

    # Run detection
    output_dir = f"{project}/outputs"
    out_name, preds = run_inference(project, tmp_path, output_dir)

    # Remove temp file
    os.remove(tmp_path)

    return jsonify({
        "output_image": f"/{project}/outputs/{out_name}",
        "predictions": preds
    })

@app.route("/<project>/outputs/<filename>")
def serve_output(project, filename):
    return send_from_directory(f"{project}/outputs", filename)

# =======================
# Main
# =======================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
