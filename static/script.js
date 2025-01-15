function initializeFileUpload(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const fileInputs = container.querySelectorAll('input[type="file"]');
    fileInputs.forEach(fileInput => {
        const preview = fileInput.nextElementSibling.querySelector('img') || fileInput.nextElementSibling.nextElementSibling;
        const info = fileInput.nextElementSibling;
        const dropZone = fileInput.closest('.preview-box');

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                handleFileSelection(fileInput, preview, info);
            }
        });

        fileInput.addEventListener('change', () => {
            handleFileSelection(fileInput, preview, info);
        });
    });
}

function handleFileSelection(input, preview, info) {
    const files = input.files;
    if (!files.length) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'text/html'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (input.hasAttribute('multiple')) {
        handleMultipleFiles(files, preview, info, validTypes, maxSize);
    } else {
        handleSingleFile(files[0], preview, info, validTypes, maxSize);
    }
}

function handleMultipleFiles(files, preview, info, validTypes, maxSize) {
    let validFiles = 0;
    let errorMessages = [];

    Array.from(files).forEach(file => {
        if (!validTypes.includes(file.type)) {
            errorMessages.push(`Invalid file type: ${file.name}`);
        } else if (file.size > maxSize) {
            errorMessages.push(`File too large: ${file.name}`);
        } else {
            validFiles++;
        }
    });

    if (errorMessages.length) {
        showError(info, errorMessages.join('\n'));
    }

    info.innerHTML = `
        <div class="file-info-content">
            <span class="file-count">${validFiles} valid files selected</span>
        </div>
    `;
}

function handleSingleFile(file, preview, info, validTypes, maxSize) {
    if (!validTypes.includes(file.type)) {
        showError(info, 'Invalid file type. Please upload an image or HTML file.');
        input.value = '';
        return;
    }

    if (file.size > maxSize) {
        showError(info, 'File too large. Maximum size is 5MB.');
        input.value = '';
        return;
    }

    showFilePreview(file, preview, info);
}

function showFilePreview(file, preview, info) {
    const reader = new FileReader();
    info.innerHTML = `
        <div class="file-info-content">
            <span class="file-name">${file.name}</span>
            <span class="file-size">(${formatFileSize(file.size)})</span>
            <span class="file-type ${file.type === 'text/html' ? 'html' : 'image'}">${file.type === 'text/html' ? 'HTML' : 'Image'}</span>
        </div>
    `;

    if (file.type === 'text/html') {
        preview.style.display = 'none';
        info.innerHTML += '<div class="convert-notice">Will be converted to image</div>';
    } else {
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

function showError(element, message) {
    element.innerHTML = `<div class="error-message">${message}</div>`;
    element.classList.add('show-error');
    setTimeout(() => {
        element.classList.remove('show-error');
    }, 3000);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
}

function showForm(formId) {
    const forms = document.querySelectorAll('.form-container');
    forms.forEach(form => {
        form.classList.remove('show');
        setTimeout(() => form.style.display = 'none', 300);
    });

    const selectedForm = document.getElementById(formId);
    setTimeout(() => {
        selectedForm.style.display = 'block';
        setTimeout(() => selectedForm.classList.add('show'), 50);
    }, 300);
}

// Initialize forms when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeFileUpload('single-comparison');
    initializeFileUpload('html-comparison');
});

function showLoadingOverlay() {
    const loadingOverlay = document.getElementById('loading-overlay');
    const progress = document.getElementById('progress');
    const percentage = document.getElementById('percentage');
    loadingOverlay.style.display = 'flex';
    progress.style.width = '0';
    percentage.textContent = '0%';

    let width = 0;
    const interval = setInterval(() => {
        if (width >= 100) {
            clearInterval(interval);
        } else {
            width += 1;
            progress.style.width = width + '%';
            percentage.textContent = width + '%';
        }
    }, 100);
}