from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)


UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_audio_info(audio_file_path):
    
    cmd = ["sox", "--i", audio_file_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip().split("\n")

        sample_rate, samples = None, None

        for line in output:
            if line.startswith("Sample Rate"):
                sample_rate = float(line.split(":")[1].strip().split()[0])
            elif line.startswith("Duration"):
                duration_str = line.split("=")[1].strip()
                samples = int(duration_str.split()[0])
        samples /= sample_rate
        return sample_rate, samples

    except subprocess.CalledProcessError as e:
        return None, None



@app.route("/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No file part"})

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "No selected file"})

    if audio_file:
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_file.filename)

       
        audio_file.save(file_path)

        sample_rate, duration = get_audio_info(file_path)
        print(sample_rate,duration)

        if sample_rate is not None and duration is not None:
            return jsonify({"message": "File uploaded successfully", "Sample Rate": sample_rate, "Duration": duration})
        else:
            return jsonify({"error": "Failed to get audio info"})

if __name__ == "__main__":
    app.run(debug=True)

