document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('essay-file');
    const fileNameDisplay = document.getElementById('file-name');
    const evaluateBtn = document.getElementById('evaluate-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const resultsSection = document.getElementById('results-section');
    const essayText = document.getElementById('essay-text');

    // Tab Switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // File Upload Handling
    dropArea.addEventListener('click', () => fileInput.click());

    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('dragover');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('dragover');
    });

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });

    function handleFile(file) {
        if (file.type === 'application/pdf') {
            fileNameDisplay.textContent = `Selected: ${file.name}`;
        } else {
            alert('Please upload a PDF file.');
            fileInput.value = '';
            fileNameDisplay.textContent = '';
        }
    }

    // Evaluate Button Click
    evaluateBtn.addEventListener('click', async () => {
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
        const formData = new FormData();

        if (activeTab === 'text-input') {
            const text = essayText.value.trim();
            if (!text) {
                alert('Please enter some text.');
                return;
            }
            formData.append('essay_text', text);
        } else {
            if (fileInput.files.length === 0) {
                alert('Please select a PDF file.');
                return;
            }
            formData.append('file', fileInput.files[0]);
        }

        // Show Loading
        loadingOverlay.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/evaluate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }

            displayResults(data);

        } catch (error) {
            alert(error.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });

    function displayResults(data) {
        resultsSection.classList.remove('hidden');

        // Animate Score Circle
        const score = data.avg_score;
        const maxScore = 10;
        const circumference = 440; // 2 * pi * r (r=70)
        const offset = circumference - (score / maxScore) * circumference;
        
        document.getElementById('avg-score').textContent = score.toFixed(1);
        
        // Reset animation
        const circle = document.getElementById('score-progress');
        circle.style.strokeDashoffset = circumference;
        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
        }, 100);

        // Update Feedback Cards
        document.getElementById('lang-score').textContent = `Score: ${data.individual_scores[0]}/10`;
        document.getElementById('lang-feedback').textContent = data.language_feedback;

        document.getElementById('analysis-score').textContent = `Score: ${data.individual_scores[1]}/10`;
        document.getElementById('analysis-feedback').textContent = data.analysis_feedback;

        document.getElementById('clarity-score').textContent = `Score: ${data.individual_scores[2]}/10`;
        document.getElementById('clarity-feedback').textContent = data.clarity_feedback;

        // Update Overall Feedback (Simple Markdown Parsing)
        const overallContent = document.getElementById('overall-feedback-content');
        overallContent.innerHTML = parseMarkdown(data.overall_feedback);
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function parseMarkdown(text) {
        if (!text) return '';
        
        // Simple markdown parser for basic formatting
        let html = text
            // Headers
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            // Lists
            .replace(/^\s*-\s+(.*)/gim, '<li>$1</li>')
            // Line breaks
            .replace(/\n/gim, '<br>');
            
        // Wrap lists in ul
        // This is a very basic implementation, might need refinement for complex nested lists
        // but sufficient for simple feedback
        
        return html;
    }
});
