// --- DASHBOARD LOGIC (No Auth) ---

// Replace this with your actual Cloud Function URL after deployment
// For local testing, use the emulator URL usually printed in the terminal
// e.g., http://127.0.0.1:5001/PROJECT_ID/us-central1
const API_BASE_URL = '/api'; // Using relative path for local proxy or same-domain hosting

async function uploadFile(type) {
    const input = document.getElementById(`${type}Input`);
    const resultBox = document.getElementById(`${type}Result`);

    if (!input.files[0]) {
        alert(`Please select an ${type} file first.`);
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    // UX: Show loading
    resultBox.className = 'result-box show';
    resultBox.style.background = 'rgba(255,255,255,0.05)';
    resultBox.style.color = '#fff';
    resultBox.style.border = '1px solid rgba(255,255,255,0.1)';
    resultBox.style.boxShadow = 'none';
    resultBox.innerText = 'ANALYZING...';

    try {
        const res = await fetch(`${API_BASE_URL}/predict/${type}`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (res.ok) {
            resultBox.innerText = `${data.result}`;

            // Reset classes
            resultBox.className = 'result-box show';
            if (data.result === 'FAKE') {
                resultBox.classList.add('result-fake');
            } else {
                resultBox.classList.add('result-normal');
            }
        } else {
            resultBox.innerText = `ERROR`;
            console.error(data.error);
            resultBox.style.color = '#fca5a5';
            resultBox.style.border = '1px solid rgba(239, 68, 68, 0.5)';
        }
    } catch (err) {
        console.error(err);
        resultBox.innerText = 'NETWORK ERROR';
        resultBox.style.color = '#fca5a5';
        resultBox.style.border = '1px solid rgba(239, 68, 68, 0.5)';
    }
}
