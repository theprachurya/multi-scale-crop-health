document.addEventListener('DOMContentLoaded', () => {
    const zones = ['leaf', 'uav', 'satellite'];
    const files = { leaf: null, uav: null, satellite: null };
    
    const btn = document.getElementById('analyze-btn');
    const resultsPanel = document.getElementById('results-panel');
    const errorMsg = document.getElementById('error-msg');
    
    zones.forEach(zone => {
        const dropZone = document.getElementById(`zone-${zone}`);
        const input = document.getElementById(`input-${zone}`);
        const preview = document.getElementById(`preview-${zone}`);
        const fileNameEl = document.getElementById(`name-${zone}`);
        
        dropZone.addEventListener('click', () => input.click());
        dropZone.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                input.click();
            }
        });
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                handleFile(zone, e.dataTransfer.files[0], preview, dropZone, fileNameEl);
            }
        });
        
        input.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleFile(zone, e.target.files[0], preview, dropZone, fileNameEl);
            }
        });
    });
    
    function handleFile(zone, file, previewEl, zoneEl, fileNameEl) {
        files[zone] = file;
        zoneEl.classList.add('has-file');
        fileNameEl.textContent = file.name;

        const reader = new FileReader();
        reader.onload = (e) => {
            previewEl.src = e.target.result;
            previewEl.style.opacity = '1';
        };
        reader.readAsDataURL(file);
        checkReady();
    }
    
    function checkReady() {
        if (files.leaf && files.uav && files.satellite) {
            btn.disabled = false;
        }
    }
    
    btn.addEventListener('click', async () => {
        errorMsg.textContent = '';
        resultsPanel.classList.add('hidden');
        resetBars();
        btn.disabled = true;
        document.querySelector('.btn-text').style.display = 'none';
        document.querySelector('.spinner').style.display = 'inline-block';
        
        const fd = new FormData();
        fd.append('leaf', files.leaf);
        fd.append('uav', files.uav);
        fd.append('satellite', files.satellite);
        
        try {
            const res = await fetch('/predict', {
                method: 'POST',
                body: fd
            });
            const data = await res.json();
            
            if (!res.ok) throw new Error(data.error || 'Server error');
            
            showResults(data);
        } catch (err) {
            errorMsg.textContent = err.message;
        } finally {
            btn.disabled = false;
            document.querySelector('.btn-text').style.display = 'inline';
            document.querySelector('.spinner').style.display = 'none';
        }
    });
    
    function showResults(data) {
        resultsPanel.classList.remove('hidden');
        
        const labelEl = document.getElementById('pred-label');
        labelEl.textContent = data.prediction;
        
        labelEl.className = 'prediction-large'; // reset
        if(data.prediction === 'Healthy') labelEl.classList.add('pred-healthy');
        if(data.prediction === 'Stressed') labelEl.classList.add('pred-stressed');
        if(data.prediction === 'Diseased') labelEl.classList.add('pred-diseased');
        
        document.getElementById('conf-val').textContent = data.confidence.toFixed(1);

        const metaMoisture = document.getElementById('meta-moisture');
        const metaPriority = document.getElementById('meta-priority');
        const metaMap = {
            Healthy: { moisture: 'Optimal', priority: 'Low' },
            Stressed: { moisture: 'Variable', priority: 'Medium' },
            Diseased: { moisture: 'Critical', priority: 'High' }
        };
        const fallbackMeta = { moisture: 'Pending', priority: 'Pending' };
        const selectedMeta = metaMap[data.prediction] || fallbackMeta;
        metaMoisture.textContent = selectedMeta.moisture;
        metaPriority.textContent = selectedMeta.priority;
        
        // Animate bars
        setTimeout(() => {
            document.getElementById('bar-healthy').style.width = `${data.probabilities.Healthy * 100}%`;
            document.getElementById('val-healthy').textContent = `${(data.probabilities.Healthy * 100).toFixed(1)}%`;
            
            document.getElementById('bar-stressed').style.width = `${data.probabilities.Stressed * 100}%`;
            document.getElementById('val-stressed').textContent = `${(data.probabilities.Stressed * 100).toFixed(1)}%`;
            
            document.getElementById('bar-diseased').style.width = `${data.probabilities.Diseased * 100}%`;
            document.getElementById('val-diseased').textContent = `${(data.probabilities.Diseased * 100).toFixed(1)}%`;
        }, 100);
    }

    function resetBars() {
        document.getElementById('bar-healthy').style.width = '0%';
        document.getElementById('bar-stressed').style.width = '0%';
        document.getElementById('bar-diseased').style.width = '0%';

        document.getElementById('val-healthy').textContent = '0%';
        document.getElementById('val-stressed').textContent = '0%';
        document.getElementById('val-diseased').textContent = '0%';
    }
});
