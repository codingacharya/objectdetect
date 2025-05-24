CREATE DATABASE detections;

CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    object_label VARCHAR(255) NOT NULL,
    action_label VARCHAR(255) NOT NULL,
    confidence FLOAT,
    bbox_xmin INT,
    bbox_ymin INT,
    bbox_xmax INT,
    bbox_ymax INT
);
