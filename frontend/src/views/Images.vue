<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, Delete, CopyDocument } from '@element-plus/icons-vue'
import { loadCachedImages, fetchImages, uploadImages, deleteImage, copyUrl } from '../api/ImageMange'

const imageList = ref([])
const isLoading = ref(false)
const retryLoadImage = ref({})

const handleFetchImages = async () => {
  // 如果有最近的缓存数据，直接使用
  const cachedResult = loadCachedImages()
  if (!isLoading.value && cachedResult.success) {
    imageList.value = cachedResult.data
    return
  }

  isLoading.value = true
  try {
    const result = await fetchImages()
    if (result.success) {
      imageList.value = result.data
    } else {
      ElMessage.error(result.error)
    }
  } finally {
    isLoading.value = false
  }
}

const handleImageUpload = async ({ file }) => {
  isLoading.value = true
  try {
    const result = await uploadImages([file])
    if (result.success) {
      ElMessage.success(`成功上传${result.count}张图片`)
      await handleFetchImages()
    } else {
      ElMessage.error(result.error)
    }
  } finally {
    isLoading.value = false
  }
}

const handleCopyUrl = async (url) => {
  const result = await copyUrl(url)
  if (result.success) {
    ElMessage.success('URL已复制到剪贴板')
  } else {
    ElMessage.error(result.error)
  }
}

const handleDeleteImage = async (imageId) => {
  try {
    await ElMessageBox.confirm('确定要删除这张图片吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    isLoading.value = true
    const result = await deleteImage(imageId)
    if (result.success) {
      ElMessage.success('图片删除成功')
      await handleFetchImages()
    } else {
      ElMessage.error(result.error)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message)
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  handleFetchImages()
})

// 当组件被keep-alive激活时，检查是否需要更新数据
onActivated(() => {
  const cachedResult = loadCachedImages()
  if (!cachedResult.success) {
    handleFetchImages()
  }
})
</script>

<template>
  <div class="images-container" v-loading="isLoading">
    <el-card class="upload-card">
      <el-upload
        action=""
        :multiple="true"
        :show-file-list="false"
        :http-request="handleImageUpload"
        accept="image/jpeg,image/png,image/gif,image/webp"
      >
        <el-button type="primary" :icon="Picture">上传图片</el-button>
      </el-upload>
    </el-card>

    <el-card class="images-list">
      <div>图片列表长度: {{ imageList.length }}</div>
      <div class="image-grid">
        <template v-if="imageList.length > 0">
          <div v-for="image in imageList" :key="image.key" class="image-item">
            <el-skeleton v-if="!image.loaded" :loading="true" animated>
              <template #template>
                <div class="skeleton-content">
                  <el-skeleton-item variant="image" style="width: 100%; height: 200px" />
                  <div style="padding: 8px">
                    <el-skeleton-item variant="text" style="width: 60%" />
                  </div>
                </div>
              </template>
            </el-skeleton>
            <el-image 
              v-show="image.loaded"
              :src="image.links.url" 
              fit="cover" 
              class="image-preview"
              @load="() => image.loaded = true"
              @error="() => retryLoadImage[image.key] = Date.now()"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                  <span>加载失败，点击重试</span>
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="retryLoadImage[image.key] = Date.now()"
                    class="retry-button"
                  >
                    重试
                  </el-button>
                </div>
              </template>
              <template #placeholder>
                <div class="image-loading">
                  <el-icon class="is-loading"><Picture /></el-icon>
                  <span>加载中</span>
                </div>
              </template>
            </el-image>
            <div class="image-info">
              <span class="image-name">{{ image.origin_name }}</span>
              <span class="image-size" v-if="image.size">{{ Number(image.size).toFixed(2) }}KB</span>
            </div>
            <div class="image-actions">
              <el-button
                type="primary"
                :icon="CopyDocument"
                @click="handleCopyUrl(image.links.url)"
                circle
              />
              <el-button
                type="danger"
                :icon="Delete"
                @click="handleDeleteImage(image.key)"
                circle
              />
            </div>
          </div>
        </template>
        <el-empty v-else description="暂无图片" />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.skeleton-content {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}
.images-container {
  padding: 20px;
}

.upload-card {
  margin-bottom: 20px;
}

.images-list {
  width: 100%;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.image-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: #fff;
  transition: transform 0.2s;
}

.image-item:hover {
  transform: translateY(-5px);
}

.image-preview {
  width: 100%;
  height: 200px;
  display: block;
  object-fit: cover;
}

.image-info {
  padding: 8px;
  background: rgba(255, 255, 255, 0.9);
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.image-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 70%;
}

.image-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-error,
.image-loading {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
  background-color: #f5f7fa;
}

.image-error .el-icon,
.image-loading .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.retry-button {
  margin-top: 8px;
}

.image-error {
  cursor: pointer;
}

.image-item:hover .image-actions {
  opacity: 1;
}
</style>