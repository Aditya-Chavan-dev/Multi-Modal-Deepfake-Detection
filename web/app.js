// --- MOCK DASHBOARD LOGIC (Simulation) ---

async function uploadFile(type) {
    const input = document.getElementById(`${type}Input`);
    const resultBox = document.getElementById(`${type}Result`);

    if (!input.files[0]) {
        alert(`Please select an ${type} file first.`);
        return;
    }

    const file = input.files[0];

    // UX: Show loading
    resultBox.className = 'result-box show';
    resultBox.style.background = 'rgba(255,255,255,0.05)';
    resultBox.style.color = '#fff';
    resultBox.style.border = '1px solid rgba(255,255,255,0.1)';
    resultBox.style.boxShadow = 'none';
    resultBox.innerText = 'ANALYZING...';

    // SIMULATION MOCK
    // Wait for 2 seconds to simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Determine Result
    // 1. Check for keywords in filename for deterministic testing
    let result = "NORMAL";
    const filename = file.name.toLowerCase();

    if (filename.includes("fake") || filename.includes("deepfake")) {
        result = "FAKE";
    } else if (filename.includes("real") || filename.includes("normal")) {
        result = "NORMAL";
    } else {
        // 2. Random weighted result (70% Normal, 30% Fake)
        result = Math.random() > 0.3 ? "NORMAL" : "FAKE";
    }

    // Display Result
    resultBox.innerText = result;

    // Apply Styles
    resultBox.className = 'result-box show';
    if (result === 'FAKE') {
        resultBox.classList.add('result-fake');
        resultBox.classList.remove('result-normal');
    } else {
        resultBox.classList.add('result-normal');
        resultBox.classList.remove('result-fake');
    }
}
