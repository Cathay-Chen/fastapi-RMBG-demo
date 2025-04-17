// 当文档加载完成时执行
document.addEventListener("DOMContentLoaded", function() {
    // 初始化表单设置
    initializeForm();

    // 设置图片预览
    setupImagePreview();
});

// 初始化表单设置
function initializeForm() {
    // 触发背景选项显示/隐藏
    toggleBackgroundOptions();

    // 初始化颜色预览
    updateColorPreview();
}

// 背景选项切换
function toggleBackgroundOptions() {
    var bgType = document.getElementById('bg_type').value;
    var colorOptions = document.getElementById('color-options');

    if (bgType === 'color') {
        colorOptions.style.display = 'block';
    } else {
        colorOptions.style.display = 'none';
    }
}

// 更新色彩值
function updateColor() {
    var colorPicker = document.getElementById('color_picker').value;
    var alphaValue = document.getElementById('alpha_slider').value;
    var alphaHex = parseInt(alphaValue).toString(16).padStart(2, '0');

    // 更新隐藏的背景颜色输入框
    document.getElementById('bg_color').value = colorPicker + alphaHex;

    // 更新预览
    updateColorPreview();
}

// 更新透明度
function updateAlpha() {
    var alphaSlider = document.getElementById('alpha_slider');
    var alphaValue = alphaSlider.value;
    var alphaPercent = Math.round((alphaValue / 255) * 100);

    // 更新显示的百分比
    document.getElementById('alpha_value').textContent = alphaPercent + '%';

    // 更新颜色值
    updateColor();
}

// 更新颜色预览
function updateColorPreview() {
    var colorValue = document.getElementById('bg_color').value;
    var preview = document.getElementById('color_preview');

    // 设置预览背景色
    if (colorValue === '#00000000') {
        // 完全透明，显示透明背景样式
        preview.className = 'color-preview transparent-preview';
        preview.style.backgroundColor = '';
    } else {
        preview.className = 'color-preview';
        preview.style.backgroundColor = colorValue;
    }
}

// 选择预设颜色
function selectPresetColor(color) {
    if (color === 'transparent') {
        // 设置为完全透明
        document.getElementById('color_picker').value = '#000000';
        document.getElementById('alpha_slider').value = 0;
        document.getElementById('bg_color').value = '#00000000';
        document.getElementById('alpha_value').textContent = '0%';
    } else {
        // 设置为选择的颜色，完全不透明
        document.getElementById('color_picker').value = color;
        document.getElementById('alpha_slider').value = 255;
        document.getElementById('bg_color').value = color + 'FF';
        document.getElementById('alpha_value').textContent = '100%';
    }

    // 更新预览
    updateColorPreview();
}

// 设置图片预览
function setupImagePreview() {
    const fileInput = document.getElementById('file');
    const previewContainer = document.getElementById('image-preview');

    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';

            const file = this.files[0];
            if (file) {
                // 检查是否是图片
                if (!file.type.startsWith('image/')) {
                    previewContainer.innerHTML = '<p class="error">请选择图片文件</p>';
                    return;
                }

                // 创建预览
                const img = document.createElement('img');
                img.file = file;
                previewContainer.appendChild(img);

                // 读取文件并显示预览
                const reader = new FileReader();
                reader.onload = (function(aImg) {
                    return function(e) {
                        aImg.src = e.target.result;
                    };
                })(img);
                reader.readAsDataURL(file);
            }
        });
    }
}