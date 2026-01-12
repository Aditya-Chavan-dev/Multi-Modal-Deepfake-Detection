# Deep Fake Detection System - Technical Documentation

## 1. Project Overview
The **Deep Fake Detection System** is a multi-modal forensic tool designed to identify manipulated digital media. It analyzes **Images**, **Audio**, and **Video** files to detect abnormalities consistent with AI-generated content (Deepfakes). 

Originally built as a standalone desktop application, it has been modernized into a cloud-native Web Application to improve accessibility, user experience, and deployment scalability.

---

## 2. System Evolution

### Legacy System (The "Before")
*   **Platform**: Desktop Application (Windows Executable).
*   **Framework**: Python `PyQt5` + `Tkinter` (Hybrid UI).
*   **User Interface**: 
    *   Basic windowed interface with standard buttons.
    *   Static background images (`A1.png`, `y.png`).
    *   Blocking operations (App froze while processing video).
    *   Required local libraries (`tensorflow`, `opencv`, `pyqt5`) installed on the user's machine.
*   **Authentication**: Custom SQLite implementation vulnerable to SQL Injection.

### Modern System (The "After")
*   **Platform**: Serverless Web Application.
*   **Framework**: HTML5, Vanilla JavaScript, CSS3.
*   **Hosting**: Firebase Hosting (Google Cloud Network).
*   **User Interface**: 
    *   **Aesthetic**: "Cyberpunk/AI Forensic" theme. Dark mode (`#030014`) with Aurora gradients.
    *   **UX**: Glassmorphism cards, micro-animations, and drag-and-drop file support.
    *   **Responsiveness**: Fully responsive grid layout working on Mobile and Desktop.
    *   **Performance**: Non-blocking asynchronous simulations.

---

## 3. Technology Stack

### Frontend (Client-Side)
*   **Core**: Semantic HTML5.
*   **Styling**: Vanilla CSS3 (Custom Variables, Flexbox/Grid, Keyframe Animations).
    *   *Design System*: custom "Glass UI" with blur filters and glowing borders.
*   **Logic**: Vanilla JavaScript (ES6+).
    *   Handles file input events.
    *   Simulates asynchronous processing states.
    *   DOM manipulation for dynamic result rendering.

### Infrastructure
*   **Platform**: Firebase.
*   **Service**: Firebase Hosting (Static Asset Delivery).
*   **CI/CD**: Manual deployment via Firebase CLI.

---

## 4. The Core Intelligence (ML Models & Algorithms)

Unlike generic "black box" deep learning models, this system uses a **Feature Extraction & Distance Metric** approach to ensure explainability and speed.

### A. Image Forensics (`model.h5`)
*   **Input**: RGB Images (Resized to 256x256).
*   **Preprocessing**:
    1.  **Median Blur**: Applied to reduce salt-and-pepper noise (ksize=5).
    2.  **Grayscale Conversion**: Reduces dimensionality.
*   **Feature Extraction**: **Gabor Filters**.
    *   The system generates a bank of **Gabor Kernels** at various orientations ($0, \pi/16, ..., \pi$).
    *   These filters are excellent at detecting **texture abnormalities** and **edge artifacts** often left behind by GANs (Generative Adversarial Networks) during face synthesis.
*   **Classification Logic**:
    *   The features of the uploaded image are flattened.
    *   **Euclidean Distance (L2 Norm)** is calculated against the cached feature set in `model.h5`.
    *   Lower distance = High similarity to "Learned" Fake fingerprints.

### B. Audio Biometrics (`model2.h5`)
*   **Input**: WAV Audio files.
*   **Feature Extraction**: **MFCC (Mel-frequency cepstral coefficients)**.
    *   Uses `librosa` to extract the short-term power spectrum of the sound.
    *   MFCCs accurately represent the "timbre" of a voice.
    *   AI-generated voices often lack subtle high-frequency imperfections present in organic human speech.
*   **Logic**:
    *   Features are summed and transposed.
    *   Distance metric comparison against the specific audio signatures stored in `model2.h5`.

### C. Video Forensics (`model3.h5`)
*   **Input**: MP4 Video files.
*   **Methodology**: **Frame-by-Frame Temporal Analysis**.
    *   The video is treated as a sequence of images.
    *   The system analyzes the first **100 frames**.
*   **Logic**:
    *   Each frame undergoes the same Gabor Filter analysis as the Image module.
    *   Scores are aggregated across frames to compute a **Mean Fake Score**.
    *   This temporal averaging helps filter out single-frame artifacts (compression noise) vs. persistent generation artifacts (deepfake faces).

---

## 5. Implementation Deployment (Mock Mode)

To facilitate immediate recruiter demonstration without incurring cloud compute costs (GPU/Python usage), the current live deployment operates in **Simulation Mode**:

1.  **Input**: User selects a file.
2.  **Processing**: The frontend initiates a deterministic simulation.
    *   **Latency Simulation**: A 2-second artificial delay mimics the inference time of the Gabor filter bank.
    *   **Determination Logic**:
        *   File names containing "fake" $\rightarrow$ Trigger `FAKE` result.
        *   File names containing "real" $\rightarrow$ Trigger `NORMAL` result.
        *   Randomized probabilistic fallback for generic files.
3.  **Output**: Renders the result using the high-contrast warning (Red) or success (Green) UI tokens.

This architecture ensures high availability (99.9% uptime on CDN) and zero "Cold Start" latency, providing a seamless review experience.
