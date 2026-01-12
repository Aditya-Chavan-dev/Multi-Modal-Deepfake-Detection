# Deep Fake Detection System - Comprehensive Technical Reference

## 1. Project Identity
*   **Project Name**: Multi-Modal Deep Fake Detection System.
*   **Core Objective**: Authenticate digital media (Image, Audio, Video) using forensic feature analysis to detect AI-generated artifacts.
*   **Evolution**: Migrated from a Local Desktop Client to a Serverless Cloud Architecture.

---

## 2. Legacy System (The "Real" Engine)

This section describes the actual Python-based detection engine originally built (`MAIN_CODE (2).py`).

### A. Technical Stack
*   **Language**: Python 3.x.
*   **GUI Framework**: `PyQt5` (Primary), `TKinter` (File Dialogs).
*   **Computer Vision**: `OpenCV` (cv2), `numpy`.
*   **Audio Processing**: `Librosa`.
*   **Deep Learning Context**: `TensorFlow`/`Keras` (Architectural definitions present, but inference optimized via distance metrics).

### B. The Machine Learning Architecture
The system employs a **Hybrid Forensic Approach** rather than a simple "Black Box" classifier. It relies on the principle that AI generation leaves specific statistical fingerprints in frequency and texture domains.

#### 1. Image Forensics (`model.h5`)
*   **Algorithm**: **Texture Analysis via Gabor Filter Banks**.
*   **Why**: Deepfakes (GANs) often struggle with high-frequency texture details (skin pores, hair), leaving "smoothing" artifacts.
*   **Mechanism**:
    1.  **Preprocessing**: Resize to 256x256 $\rightarrow$ Median Blur (Noise Reduction) $\rightarrow$ Grayscale.
    2.  **Feature Engineering**: A bank of **Gabor Filters** is constructed at multiple orientations ($0, \pi/16, ..., \pi$).
        *   *Code Reference*: `build_filters()` generates these kernels.
        *   *Process*: `cv2.filter2D` convolves the image with these kernels to highlight texture anomalies.
    3.  **Classification**:
        *   The system loads `model.h5` (a binary Pickle file containing reference feature vectors of known "Real" and "Fake" datasets).
        *   It computes the **Euclidean Distance (L2 Norm)** between the Uploaded Image's features and the Reference vectors.
        *   **Decision**: `argmin(Distance)` determines if it is closer to the "Fake" or "Real" cluster.

#### 2. Audio Biometrics (`model2.h5`)
*   **Algorithm**: **Spectral Consistency Analysis via MFCC**.
*   **Why**: Synthetic voices (TTS/VC) lack the subtle organic spectral variance of human vocal cords.
*   **Mechanism**:
    1.  **Ingestion**: Load audio via `librosa`.
    2.  **Feature Extraction**: Compute **Mel-frequency Cepstral Coefficients (MFCCs)**.
        *   This captures the "timbre" or "color" of the audio signal.
    3.  **Classification**:
        *   Sum and Transpose the coefficient matrix.
        *   Compare against `model2.h5` signature database using the same Euclidean Distance metric.

#### 3. Video Integrity (`model3.h5`)
*   **Algorithm**: **Temporal Frame Analysis**.
*   **Why**: Deepfakes often flicker or lose coherence between frames.
*   **Mechanism**:
    1.  **Sampling**: Extracts the first **100 frames** of the video.
    2.  **Frame Analysis**: Each frame is treated as an independent Image Forensic task (Gabor Filters).
    3.  **Aggregation**: A temporal average of the "Fake Scores" is calculated.
    4.  **Thresholding**: If the mean fake score exceeds a specific threshold, the entire video is flagged.

### C. Build Process (How Models Was Created)
The `.h5` files are not standard Keras weights but rather **Serialized Feature Stores**.
1.  **Training Phase**:
    *   A dataset of Real and Fake media was passed through the Feature Extractors (Gabor/MFCC).
    *   The resulting feature vectors were aggregated.
    *   `pickle.dump()` was used to save these reference matrices into `model.h5`, `model2.h5`, and `model3.h5`.
2.  **Inference Phase**:
    *   The app loads these matrices into memory.
    *   Incoming data is projected into the same feature space and compared.

---

## 3. Modern Web Architecture (The Present)

To demonstrate this capability to recruiters without requiring them to install 5GB of Python libraries, we migrated to a **Serverless Web Mock**.

### Modern System (The "After")
*   **Platform**: Serverless Web Application.
*   **Framework**: **React 18** (Vite), **TailwindCSS**, Framer Motion.
*   **Hosting**: Firebase Hosting (CDN).
*   **User Interface**: 
    *   **Aesthetic**: "Forensic Dashboard" theme. Bento-grid layout, high-contrast monochrome.
    *   **UX**: Drag-and-drop zones, real-time scanning animations, and deterministic simulation.
    *   **Performance**: Production-optimized build (Vite).

---

## 3. Technology Stack

### Frontend (Client-Side)
*   **Core**: React 18, Vite.
*   **Styling**: TailwindCSS (Utility-first), Framer Motion (Animations).
*   **Icons**: Lucide React.
*   **Language**: JavaScript (ES6+).
### B. Simulation Logic
Since the "Real Engine" requires heavy local computation or expensive GPU cloud servers:
*   **The Interface**: Replicates the exact workflow of the desktop app (File Selection $\rightarrow$ Analysis $\rightarrow$ Result).
*   **The Backend**: Replaced by a deterministic Client-Side Simulation.
    *   **Latency**: We inject a 2-second delay to realistically mimic the Gabor Filter convolution time.
    *   **Result Generation**:
        *   We scan filenames for "keywords" (fake/real) to allow you to demonstrate both Start States reliably.
        *   This provides a 100% stable demo environment.

---

## 4. Comparison Summary

| Feature | Legacy Desktop App | Modern Web App |
| :--- | :--- | :--- |
| **Accessibility** | Requires Installation | Instant (URL) |
| **Compute** | Heavy Local CPU/RAM | Zero (Client-Side) |
| **UI/UX** | Basic, Blocking | Fluid, Responsive, Premium |
| **Codebase** | Python/Qt | JS/HTML/CSS |
| **Detection** | Real (Gabor/MFCC) | Simulated (Mock) |

---
