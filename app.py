from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import subprocess
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/models'
app.config['PREVIEW_FOLDER'] = 'static/previews'
model_path='final_obj_mapping_model.keras'
# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    obj_file = request.files['objFile']
    texture_file = request.files['textureFile']

    # Generate unique filename
    unique_id = str(uuid.uuid4())
    obj_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}.obj")
    texture_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}.jpg")
    
    # Save uploaded files
    obj_file.save(obj_path)
    texture_file.save(texture_path)

    # Process the model using model.py
    output_model_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_optimized.obj")
    compressed_texture_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_compressed.jpg")
    #model.exec(obj_path, texture_path, output_model_path, compressed_texture_path)
    try:

        # Run the processing script
        subprocess.run(['python', 'model.py', obj_path, texture_path, output_model_path, compressed_texture_path], check=True)

    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "optimized_model": f"/static/models/{unique_id}_optimized.obj",
        "compressed_texture": f"/static/models/{unique_id}_compressed.jpg"
    })

@app.route('/static/models/<path:filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
