import os
import sqlite3
import cv2
import numpy as np
import pickle
import librosa
from numpy import linalg as LA
from flask import Flask, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__, static_folder='web', static_url_path='')
app.secret_key = 'super_secret_key_change_this_in_production'
CORS(app)

# --- CONFIGURATION ---
DB_NAME = "multiD.db"
MODEL_IMG_PATH = "model.h5"
MODEL_AUDIO_PATH = "model2.h5"
MODEL_VIDEO_PATH = "model3.h5"
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- LOGIC PORTED FROM MAIN_CODE (2).py ---

def build_filters():
    filters = []
    ksize = 11
    for theta in np.arange(0, np.pi, np.pi / 16):
        kern = cv2.getGaborKernel((ksize, ksize), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
        kern /= 1.5 * kern.sum()
        filters.append(kern)
    return filters

def process(img, filters):
    accum = np.zeros_like(img)
    for kern in filters:
        fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
        np.maximum(accum, fimg, accum)
    return accum

def Calc_Wt(TRR, TST):
    WTRN = TRR
    R, C = np.shape(WTRN)
    M = []
    WTST = TST
    # Ensure dimensions match for broadcast or loop
    for i in range(0, C):
        RR = WTRN[:, i]
        Temp = np.subtract(WTST, RR)
        ERR = LA.norm(Temp)
        M.append(ERR)
    ind = np.argmin(M)
    return ind

# Global Filters (Init once)
GF = build_filters()

# Load Models (Init once to avoid lag)
def load_model(path):
    if not os.path.exists(path):
        print(f"WARNING: Model not found at {path}")
        return None
    try:
        with open(path, 'rb') as file:
            model = pickle.load(file)
            return np.transpose(model) # Transpose as per original code
    except Exception as e:
        print(f"ERROR loading model {path}: {e}")
        return None

CNN_IMG = load_model(MODEL_IMG_PATH)
CNN_AUDIO = load_model(MODEL_AUDIO_PATH)
CNN_VIDEO = load_model(MODEL_VIDEO_PATH) # Assuming video uses same format? Original says model3.h5

# --- DB HELPERS ---

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Ensure table exists (based on login.py/signup.py)
    conn = get_db_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS userdetails (
                username TEXT,
                email TEXT,
                mob TEXT,
                password TEXT
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")
    finally:
        conn.close()

init_db()

# --- API ENDPOINTS ---

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/dashboard')
def dashboard():
    return app.send_static_file('dashboard.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    # SECURE: Use parameterized queries
    user = conn.execute('SELECT * FROM userdetails WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()

    if user:
        session['user'] = username
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    mob = data.get('mob')
    password = data.get('password')

    if not all([username, email, mob, password]):
         return jsonify({'status': 'error', 'message': 'Missing fields'}), 400

    conn = get_db_connection()
    try:
        # SECURE: Use parameterized queries
        conn.execute('INSERT INTO userdetails (username, email, mob, password) VALUES (?, ?, ?, ?)',
                     (username, email, mob, password))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Registration successful'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/predict/image', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Logic from show1 in MAIN_CODE (2).py
        img = cv2.imread(filepath)
        img = cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA) # Added explicit interpolation
        img1 = cv2.medianBlur(img, 5)
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        
        # Gabor Process
        processed_gray = process(gray, GF)
        
        TST = np.reshape(processed_gray, (256 * 256))
        TST = np.ravel(TST)
        TST = np.transpose(TST)

        if CNN_IMG is None:
             return jsonify({'error': 'Model not loaded'}), 500

        n = Calc_Wt(CNN_IMG, TST)
        # Original logic: RES1=np.floor(n/250)
        RES1 = np.floor(n / 250)
        
        result = "FAKE" if RES1 == 0 else "NORMAL"
        return jsonify({'result': result, 'score': float(n)})

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/audio', methods=['POST'])
def predict_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Logic from show2 in MAIN_CODE (2).py
        I1, sr_1 = librosa.load(filepath, sr=None)
        A1 = librosa.feature.mfcc(y=I1, sr=sr_1) # Updated librosa call signature if needed, but keeping simple
        TST = np.sum(A1, axis=1)
        TST = np.ravel(TST)
        TST = np.transpose(TST)

        if CNN_AUDIO is None:
             return jsonify({'error': 'Audio Model not loaded'}), 500

        n = Calc_Wt(CNN_AUDIO, TST)
        # Original logic: RES1=np.floor(n/100)
        RES1 = np.floor(n / 100)

        result = "FAKE" if RES1 == 0 else "NORMAL"
        return jsonify({'result': result, 'score': float(n)})

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/video', methods=['POST'])
def predict_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Logic from show4 in MAIN_CODE (2).py
        if CNN_VIDEO is None:
             return jsonify({'error': 'Video Model not loaded'}), 500

        cap = cv2.VideoCapture(filepath)
        RES1s = []
        siz = 64
        ij = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            ij += 1
            img = cv2.resize(frame, (siz, siz), interpolation=cv2.INTER_AREA)
            img1 = cv2.medianBlur(img, 5)
            img_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            
            processed_gray = process(img_gray, GF)
            
            TST = np.reshape(processed_gray, (siz * siz))
            TST = np.ravel(TST)
            TST = np.transpose(TST)
            
            n = Calc_Wt(CNN_VIDEO, TST)
            # Original: RES1=np.floor(n/2455)
            RES1 = np.floor(n / 2455)
            RES1s.append(RES1)
            
            if ij >= 100: # Limit to 100 frames as per original
                break
        
        cap.release()
        
        if not RES1s:
             return jsonify({'error': 'Could not process video frames'}), 500

        final_res = np.mean(RES1s)
        
        # Original logic: 0 -> NORMAL, 1 -> FAKE (Note: This is swapped compared to Audio/Image in original code!)
        # show4: if RES1==0: Dis='NORMAL' elif RES1==1: Dis='FAKE'
        
        # Let's double check show4 logic in original file.
        # Line 429: if RES1==0: Dis='NORMAL'
        # Line 431: elif RES1==1: Dis='FAKE'
        # Wait, show1 says: if RES1==0: Dis='FAKE' (Line 324)
        # This inconsistency is in the original code. I will PRESERVE it.
        
        result = "NORMAL" if final_res <= 0.5 else "FAKE" # Using threshold 0.5 for mean
        
        return jsonify({'result': result, 'score': float(final_res)})

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
