export async function simulateAnalysis(file) {
    return new Promise((resolve) => {
        // Simulate network/processing latency
        setTimeout(() => {
            const name = file.name.toLowerCase();
            let result = 'NORMAL';
            let confidence = (Math.random() * (99 - 85) + 85).toFixed(1);

            if (name.includes('fake') || name.includes('deepfake')) {
                result = 'FAKE';
                confidence = (Math.random() * (99.9 - 95) + 95).toFixed(1);
            } else if (name.includes('real') || name.includes('normal')) {
                result = 'NORMAL';
            } else {
                // Random fallback
                result = Math.random() > 0.3 ? 'NORMAL' : 'FAKE';
            }

            resolve({
                status: result,
                confidence: confidence,
                details: result === 'FAKE'
                    ? 'Anomalies detected in high-frequency spectrum.'
                    : 'No manipulation artifacts found.'
            });
        }, 2500); // 2.5s delay
    });
}
