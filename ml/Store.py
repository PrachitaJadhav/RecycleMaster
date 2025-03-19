import cv2
import sqlite3
from ultralytics import YOLO
import collections

# Load YOLOv8 Model
model = YOLO("yolov8n.pt")  # Replace with "best.pt" if using a trained model

# Open webcam
cap = cv2.VideoCapture(0)

# Connect to SQLite database (or create it)
conn = sqlite3.connect("recycle_materia.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material TEXT,
        count INTEGER
    )
""")

# Dictionary to store detected object counts
object_counts = collections.defaultdict(int)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Perform object detection
    results = model(frame)

    # Get detected class names
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])  # Class index
            class_name = model.names[class_id]  # Class name

            # Count detected objects
            object_counts[class_name] += 1

    # Store data in the SQLite database
    for material, count in object_counts.items():
        cursor.execute("INSERT INTO materials (material, count) VALUES (?, ?)", (material, count))

    conn.commit()  # Save changes to database

    # Display frame
    annotated_frame = results[0].plot()
    cv2.imshow("YOLOv8 Object Counting", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()  # Close database connection

print("Data saved to SQLite database!")
