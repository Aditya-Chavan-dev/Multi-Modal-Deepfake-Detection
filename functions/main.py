import os
import pickle
import numpy as np
import cv2
import librosa
from numpy import linalg as LA
from firebase_functions import https_fn, options
from firebase_admin import initialize_app, storage

# Initialize Firebase Admin
initialize_app()

# Models will be cached in global memory after first cold start
CNN_IMG = None
CNN_AUDIO = None
CNN_VIDEO = None

MODEL_BUCKET_NAME = "adit-deepfake-detection.firebasestorage.app" # TO BE REPLACED BY USER
MODELS = {
    "image": "model.h5",
    "audio": "model2.h5",
    "video": "model3.h5"
}

# --- LOGIC PORTED FROM MAIN_CODE (2).py ---
def build_filters():
    filters = []
    ksize = 11
    # Gabor Filter Logic
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
    for i in range(0, C):
        RR = WTRN[:, i]
        Temp = np.subtract(WTST, RR)
        ERR = LA.norm(Temp)
        M.append(ERR)
    ind = np.argmin(M)
    return ind

GF = build_filters()

def load_model_from_storage(model_type):
    """Downloads model from Firebase Storage to /tmp and loads it."""
    global CNN_IMG, CNN_AUDIO, CNN_VIDEO
    
    filename = MODELS[model_type]
    local_path = f"/tmp/{filename}"
    
    # Check if we already have it in memory
    if model_type == "image" and CNN_IMG is not None: return CNN_IMG
    if model_type == "audio" and CNN_AUDIO is not None: return CNN_AUDIO
    if model_type == "video" and CNN_VIDEO is not None: return CNN_VIDEO

    # Check if download is needed
    if not os.path.exists(local_path):
        print(f"Downloading {filename} from Storage...")
        bucket = storage.bucket(MODEL_BUCKET_NAME) 
        blob = bucket.blob(filename)
        blob.download_to_filename(local_path)
        print("Download complete.")

    # Load into memory
    with open(local_path, 'rb') as file:
         model_data = pickle.load(file)
         transposed_model = np.transpose(model_data)
         
         if model_type == "image": CNN_IMG = transposed_model
         elif model_type == "audio": CNN_AUDIO = transposed_model
         elif model_type == "video": CNN_VIDEO = transposed_model
         
         return transposed_model

# --- HTTP FUNCTIONS ---

@https_fn.on_request(
    memory=options.MemoryOption.GB_1, # Need RAM for large models
    timeout_sec=300, # Long timeout for cold start + video
    region="us-central1"
)
def predict_image(req: https_fn.Request) -> https_fn.Response:
    # CORS handling
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return https_fn.Response('', status=204, headers=headers)

    # 1. Load File
    # Note: In Cloud Functions Python, file uploads need multipart parsing manually or use raw body if simplistic. 
    # For now assuming simple binary body or multipart. Python functions framework handles flask-like 'request.files' nicely.
    # HOWEVER, firebase_functions Request object is a Werkzeug Request.
    
    file = req.files.get('file')
    if not file:
        return https_fn.Response('No file uploaded', status=400, headers={'Access-Control-Allow-Origin': '*'})
    
    # Save to /tmp
    tmp_path = "/tmp/upload.jpg"
    file.save(tmp_path)
    
    try:
        # 2. Logic
        model = load_model_from_storage("image")
        
        img = cv2.imread(tmp_path)
        img = cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA)
        img1 = cv2.medianBlur(img, 5)
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        processed_gray = process(gray, GF)
        TST = np.reshape(processed_gray, (256 * 256))
        TST = np.ravel(TST)
        TST = np.transpose(TST)
        
        n = Calc_Wt(model, TST)
        RES1 = np.floor(n / 250)
        result = "FAKE" if RES1 == 0 else "NORMAL"
        
        return https_fn.Response(
            response=f'{{"result": "{result}", "score": {float(n)}}}',
            status=200,
            mimetype='application/json',
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except Exception as e:
        return https_fn.Response(f'{{"error": "{str(e)}"}}', status=500, mimetype='application/json', headers={'Access-Control-Allow-Origin': '*'})


@https_fn.on_request(memory=options.MemoryOption.GB_1, timeout_sec=300)
def predict_audio(req: https_fn.Request) -> https_fn.Response:
    if req.method == 'OPTIONS':
         return https_fn.Response('', status=204, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST', 'Access-Control-Allow-Headers': 'Content-Type'})

    file = req.files.get('file')
    if not file: return https_fn.Response('No file', status=400)
    
    tmp_path = "/tmp/upload.wav"
    file.save(tmp_path)
    
    try:
        model = load_model_from_storage("audio")
        I1, sr_1 = librosa.load(tmp_path, sr=None)
        A1 = librosa.feature.mfcc(y=I1, sr=sr_1)
        TST = np.sum(A1, axis=1)
        TST = np.ravel(TST)
        TST = np.transpose(TST)
        n = Calc_Wt(model, TST)
        RES1 = np.floor(n / 100)
        result = "FAKE" if RES1 == 0 else "NORMAL"
        return https_fn.Response(f'{{"result": "{result}"}}', status=200, headers={'Access-Control-Allow-Origin': '*'})
    except Exception as e:
        return https_fn.Response(str(e), status=500)

@https_fn.on_request(memory=options.MemoryOption.GB_1, timeout_sec=300)
def predict_video(req: https_fn.Request) -> https_fn.Response:
    if req.method == 'OPTIONS':
         return https_fn.Response('', status=204, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST', 'Access-Control-Allow-Headers': 'Content-Type'})

    file = req.files.get('file')
    if not file: return https_fn.Response('No file', status=400)
    
    tmp_path = "/tmp/upload.mp4"
    file.save(tmp_path)
    
    try:
        model = load_model_from_storage("video")
        cap = cv2.VideoCapture(tmp_path)
        RES1s = []
        ij = 0
        siz = 64
        
        while True:
            ret, frame = cap.read()
            if not ret or ij >= 100: break
            ij += 1
            
            img = cv2.resize(frame, (siz, siz), interpolation=cv2.INTER_AREA)
            img1 = cv2.medianBlur(img, 5)
            gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            processed_gray = process(gray, GF)
            TST = np.reshape(processed_gray, (siz * siz))
            TST = np.ravel(TST)
            TST = np.transpose(TST)
            n = Calc_Wt(model, TST)
            RES1 = np.floor(n / 2455)
            RES1s.append(RES1)
            
        cap.release()
        final_res = np.mean(RES1s) if RES1s else 0
        result = "NORMAL" if final_res <= 0.5 else "FAKE"
        
        return https_fn.Response(f'{{"result": "{result}"}}', status=200, headers={'Access-Control-Allow-Origin': '*'})
    except Exception as e:
         return https_fn.Response(str(e), status=500)
