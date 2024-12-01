from flask import Flask, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # This allows the API to be called from any origin

@app.route('/audio/<filename>')
def serve_audio(filename):
    # Find the actual audio file that ends with this filename
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith(filename):
                return send_file(os.path.join(root, file))
    return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 