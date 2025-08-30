<template>
  <div v-if="show" class="avatar-cropper-modal" @click="handleModalClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>裁剪头像</h3>
        <button @click="close" class="btn-close">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="cropper-container">
          <canvas 
            ref="canvas" 
            :width="canvasSize" 
            :height="canvasSize"
            class="crop-canvas"
            @mousedown="startDrag"
            @mousemove="drag"
            @mouseup="endDrag"
            @wheel="zoom"
          ></canvas>
          
          <!-- 裁剪预览 -->
          <div class="crop-preview">
            <div class="preview-title">预览效果</div>
            <div class="preview-circle">
              <canvas 
                ref="previewCanvas" 
                width="120" 
                height="120"
                class="preview-canvas"
              ></canvas>
            </div>
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="crop-controls">
          <div class="control-group">
            <label>缩放：</label>
            <input 
              type="range" 
              v-model="scale" 
              min="0.1" 
              max="3" 
              step="0.1" 
              class="scale-slider"
              @input="updateCanvas"
            >
            <span class="scale-value">{{ scale }}x</span>
          </div>
          
          <div class="control-buttons">
            <button @click="resetPosition" class="btn btn-secondary">重置位置</button>
            <button @click="rotateImage" class="btn btn-secondary">旋转 90°</button>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="close" class="btn btn-secondary">取消</button>
        <button @click="confirmCrop" class="btn btn-primary" :disabled="uploading">
          {{ uploading ? '上传中...' : '确定裁剪' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { qiniuAPI } from '../api/qiniu.js';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  imageFile: {
    type: [File, Object], // 允许File或null/Object
    default: null
  }
});

const emit = defineEmits(['close', 'success', 'error']);

// 画布相关
const canvas = ref(null);
const previewCanvas = ref(null);
const canvasSize = 400;
const cropRadius = 150; // 裁剪圆形半径

// 图片和变换状态
const imageState = reactive({
  image: null,
  loaded: false,
  x: 0,
  y: 0,
  rotation: 0
});

const scale = ref(1);
const uploading = ref(false);

// 拖拽状态
const dragState = reactive({
  isDragging: false,
  startX: 0,
  startY: 0,
  initialX: 0,
  initialY: 0
});

// 监听图片文件变化
watch(() => props.imageFile, (newFile) => {
  if (newFile && newFile instanceof File) {
    loadImage(newFile);
  }
}, { immediate: true });

// 监听显示状态
watch(() => props.show, (show) => {
  if (show && props.imageFile && props.imageFile instanceof File) {
    nextTick(() => {
      loadImage(props.imageFile);
    });
  }
});

// 加载图片
const loadImage = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      imageState.image = img;
      imageState.loaded = true;
      resetPosition();
      updateCanvas();
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
};

// 重置位置和缩放
const resetPosition = () => {
  if (!imageState.image) return;
  
  const img = imageState.image;
  const centerX = canvasSize / 2;
  const centerY = canvasSize / 2;
  
  // 计算适合的初始缩放比例
  const scaleX = (cropRadius * 2) / img.width;
  const scaleY = (cropRadius * 2) / img.height;
  scale.value = Math.max(scaleX, scaleY);
  
  // 居中显示
  imageState.x = centerX - (img.width * scale.value) / 2;
  imageState.y = centerY - (img.height * scale.value) / 2;
  imageState.rotation = 0;
  
  updateCanvas();
};

// 旋转图片
const rotateImage = () => {
  imageState.rotation = (imageState.rotation + 90) % 360;
  updateCanvas();
};

// 更新画布
const updateCanvas = () => {
  if (!canvas.value || !imageState.image || !imageState.loaded) return;
  
  const ctx = canvas.value.getContext('2d');
  const img = imageState.image;
  
  // 清空画布
  ctx.clearRect(0, 0, canvasSize, canvasSize);
  
  // 保存当前状态
  ctx.save();
  
  // 设置旋转中心
  const centerX = imageState.x + (img.width * scale.value) / 2;
  const centerY = imageState.y + (img.height * scale.value) / 2;
  
  ctx.translate(centerX, centerY);
  ctx.rotate((imageState.rotation * Math.PI) / 180);
  ctx.translate(-centerX, -centerY);
  
  // 绘制图片
  ctx.drawImage(
    img,
    imageState.x,
    imageState.y,
    img.width * scale.value,
    img.height * scale.value
  );
  
  // 恢复状态
  ctx.restore();
  
  // 绘制裁剪区域遮罩
  drawCropMask(ctx);
  
  // 更新预览
  updatePreview();
};

// 绘制裁剪遮罩
const drawCropMask = (ctx) => {
  const centerX = canvasSize / 2;
  const centerY = canvasSize / 2;
  
  // 绘制半透明遮罩
  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(0, 0, canvasSize, canvasSize);
  
  // 清除圆形区域
  ctx.globalCompositeOperation = 'destination-out';
  ctx.beginPath();
  ctx.arc(centerX, centerY, cropRadius, 0, 2 * Math.PI);
  ctx.fill();
  
  // 重置合成操作
  ctx.globalCompositeOperation = 'source-over';
  
  // 绘制圆形边框
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(centerX, centerY, cropRadius, 0, 2 * Math.PI);
  ctx.stroke();
};

// 更新预览
const updatePreview = () => {
  if (!previewCanvas.value || !imageState.image || !imageState.loaded) return;
  
  const previewCtx = previewCanvas.value.getContext('2d');
  const previewSize = 120;
  
  // 清空预览画布
  previewCtx.clearRect(0, 0, previewSize, previewSize);
  
  // 创建圆形裁剪路径
  previewCtx.save();
  previewCtx.beginPath();
  previewCtx.arc(previewSize / 2, previewSize / 2, previewSize / 2, 0, 2 * Math.PI);
  previewCtx.clip();
  
  // 计算预览缩放比例
  const previewScale = previewSize / (cropRadius * 2);
  const centerX = canvasSize / 2;
  const centerY = canvasSize / 2;
  
  // 计算图片在预览中的位置
  const previewX = (imageState.x - (centerX - cropRadius)) * previewScale;
  const previewY = (imageState.y - (centerY - cropRadius)) * previewScale;
  const previewWidth = imageState.image.width * scale.value * previewScale;
  const previewHeight = imageState.image.height * scale.value * previewScale;
  
  // 设置旋转
  const previewCenterX = previewX + previewWidth / 2;
  const previewCenterY = previewY + previewHeight / 2;
  
  previewCtx.translate(previewCenterX, previewCenterY);
  previewCtx.rotate((imageState.rotation * Math.PI) / 180);
  previewCtx.translate(-previewCenterX, -previewCenterY);
  
  // 绘制预览图片
  previewCtx.drawImage(imageState.image, previewX, previewY, previewWidth, previewHeight);
  
  previewCtx.restore();
};

// 鼠标拖拽事件
const startDrag = (e) => {
  dragState.isDragging = true;
  dragState.startX = e.clientX;
  dragState.startY = e.clientY;
  dragState.initialX = imageState.x;
  dragState.initialY = imageState.y;
};

const drag = (e) => {
  if (!dragState.isDragging) return;
  
  const deltaX = e.clientX - dragState.startX;
  const deltaY = e.clientY - dragState.startY;
  
  imageState.x = dragState.initialX + deltaX;
  imageState.y = dragState.initialY + deltaY;
  
  updateCanvas();
};

const endDrag = () => {
  dragState.isDragging = false;
};

// 缩放事件
const zoom = (e) => {
  e.preventDefault();
  const delta = e.deltaY > 0 ? -0.1 : 0.1;
  const newScale = Math.max(0.1, Math.min(3, scale.value + delta));
  scale.value = newScale;
  updateCanvas();
};

// 获取裁剪后的图片
const getCroppedImage = () => {
  const cropCanvas = document.createElement('canvas');
  const cropCtx = cropCanvas.getContext('2d');
  const size = 300; // 输出尺寸
  
  cropCanvas.width = size;
  cropCanvas.height = size;
  
  // 创建圆形裁剪路径
  cropCtx.beginPath();
  cropCtx.arc(size / 2, size / 2, size / 2, 0, 2 * Math.PI);
  cropCtx.clip();
  
  // 计算裁剪区域的缩放比例
  const outputScale = size / (cropRadius * 2);
  const centerX = canvasSize / 2;
  const centerY = canvasSize / 2;
  
  // 计算图片在输出画布中的位置
  const outputX = (imageState.x - (centerX - cropRadius)) * outputScale;
  const outputY = (imageState.y - (centerY - cropRadius)) * outputScale;
  const outputWidth = imageState.image.width * scale.value * outputScale;
  const outputHeight = imageState.image.height * scale.value * outputScale;
  
  // 设置旋转
  const outputCenterX = outputX + outputWidth / 2;
  const outputCenterY = outputY + outputHeight / 2;
  
  cropCtx.translate(outputCenterX, outputCenterY);
  cropCtx.rotate((imageState.rotation * Math.PI) / 180);
  cropCtx.translate(-outputCenterX, -outputCenterY);
  
  // 绘制裁剪后的图片
  cropCtx.drawImage(imageState.image, outputX, outputY, outputWidth, outputHeight);
  
  return new Promise((resolve) => {
    cropCanvas.toBlob(resolve, 'image/jpeg', 0.9);
  });
};

// 确认裁剪并上传
const confirmCrop = async () => {
  if (!imageState.image || uploading.value) return;
  
  uploading.value = true;
  
  try {
    // 获取裁剪后的图片
    const croppedBlob = await getCroppedImage();
    
    // 生成文件key
    const timestamp = Date.now();
    const fileKey = qiniuAPI.generateFileKey('avatars', `avatar_${timestamp}.jpg`);
    
    // 获取bucket信息和上传token
    const [tokenResponse, bucketResponse] = await Promise.all([
      qiniuAPI.getUploadToken(fileKey, '头像上传'),
      qiniuAPI.getBucketInfo()
    ]);
    
    console.log('Token response:', tokenResponse.data);
    console.log('Bucket response:', bucketResponse.data);
    
    // 根据实际响应结构提取token和上传域名
    let token, uploadDomain;
    if (tokenResponse.data.code === 201) {
      token = tokenResponse.data.data.token;
    } else {
      throw new Error('获取上传token失败');
    }
    
    if (bucketResponse.data.code === 200) {
      uploadDomain = bucketResponse.data.data.upload_domain;
    } else {
      throw new Error('获取bucket信息失败');
    }
    
    console.log('Using upload domain:', uploadDomain);
    
    // 上传到七牛云
    const uploadResult = await qiniuAPI.uploadFile(
      croppedBlob,
      token,
      fileKey,
      uploadDomain
    );
    
    // 构建图片URL - 使用七牛云的访问域名
    const imageUrl = `http://oss.fossradar.cn/${fileKey}`;
    console.log('Generated image URL:', imageUrl);
    
    emit('success', imageUrl);
    close();
  } catch (error) {
    console.error('上传头像失败:', error);
    emit('error', '上传失败，请重试');
  } finally {
    uploading.value = false;
  }
};

// 清理资源
const cleanup = () => {
  // 清理canvas上下文
  if (canvas.value) {
    const ctx = canvas.value.getContext('2d');
    if (ctx) {
      ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
    }
  }
  if (previewCanvas.value) {
    const ctx = previewCanvas.value.getContext('2d');
    if (ctx) {
      ctx.clearRect(0, 0, previewCanvas.value.width, previewCanvas.value.height);
    }
  }
  // 重置状态
  image.value = null;
  scale.value = 1;
  position.x = 0;
  position.y = 0;
  dragging.isDragging = false;
};

// 组件销毁时清理
onUnmounted(() => {
  cleanup();
});

// 关闭模态框
const close = () => {
  cleanup();
  emit('close');
};

// 点击模态框背景关闭
const handleModalClick = (e) => {
  if (e.target === e.currentTarget) {
    close();
  }
};

// 监听缩放滑块变化
watch(scale, () => {
  updateCanvas();
});
</script>

<style scoped>
.avatar-cropper-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #dc3545;
}

.modal-body {
  padding: 30px;
}

.cropper-container {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.crop-canvas {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: grab;
  display: block;
}

.crop-canvas:active {
  cursor: grabbing;
}

.crop-preview {
  flex-shrink: 0;
  text-align: center;
}

.preview-title {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 15px;
}

.preview-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e9ecef;
  background: #f8f9fa;
}

.preview-canvas {
  display: block;
}

.crop-controls {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.control-group label {
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.scale-slider {
  flex: 1;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.scale-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: #545ae7;
  border-radius: 50%;
  cursor: pointer;
}

.scale-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #545ae7;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.scale-value {
  font-weight: 600;
  color: #495057;
  min-width: 40px;
  text-align: right;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #545ae7 0%, #6c5ce7 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(84, 90, 231, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 15px;
  }
  
  .cropper-container {
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  
  .crop-canvas {
    width: 300px;
    height: 300px;
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>