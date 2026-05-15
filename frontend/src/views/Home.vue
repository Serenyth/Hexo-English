<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const blogPath = ref('')
const statistics = ref({
  posts: 0,
  categories: 0,
  tags: 0
})
const loading = ref(false)
const isEditing = ref(false)
const tempPath = ref('')
const serverStatus = ref(false)
const serverLoading = ref(false)
const deployLoading = ref(false)

// 获取博客目录
const getBlogPath = async () => {
  try {
    const res = await api.get('/api/blog/current-directory')
    console.log('获取博客，',res)
    console.log('获取博客，',res.directory)
    blogPath.value = res.directory
    tempPath.value = res.directory
  } catch (error) {
    console.error('获取博客目录失败:', error)
  }
}

// 获取统计数据
const getStatistics = async () => {
  try {
    loading.value = true
    const [postsRes, structureRes] = await Promise.all([
      await api.get('/api/posts/list'),
      await api.get('/api/blog/structure'),
    ])
    
    // 统计文章数量
    statistics.value.posts = postsRes.length
    
    // 统计分类和标签
    const categories = new Set()
    const tags = new Set()
    postsRes.forEach(post => {
      post.categories?.forEach(cat => categories.add(cat))
      post.tags?.forEach(tag => tags.add(tag))
    })
    
    statistics.value.categories = categories.size
    statistics.value.tags = tags.size
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取服务器状态
const getServerStatus = async () => {
  try {
    const res = await api.get('/api/blog/server/status')
    serverStatus.value = res.running
  } catch (error) {
    console.error('获取服务器状态失败:', error)
  }
}

// 启动服务器
const startServer = async () => {
  try {
    serverLoading.value = true
    await api.post('/api/blog/server/start')
    ElMessage.success('服务器启动成功')
    await getServerStatus()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '启动服务器失败')
  } finally {
    serverLoading.value = false
  }
}

// 停止服务器
const stopServer = async () => {
  try {
    serverLoading.value = true
    await api.post('/api/blog/server/stop')
    ElMessage.success('服务器已停止')
    await getServerStatus()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '停止服务器失败')
  } finally {
    serverLoading.value = false
  }
}

// 部署博客
const deployBlog = async () => {
  try {
    deployLoading.value = true
    await api.post('/api/blog/deploy')
    ElMessage.success('博客部署已开始，请查看终端窗口了解进度')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '部署博客失败')
  } finally {
    deployLoading.value = false
  }
}

// 保存目录设置
const saveBlogPath = async () => {
  try {
    await api.post('/api/blog/select-directory', {
      directory_path: tempPath.value
    })
    blogPath.value = tempPath.value
    isEditing.value = false
    ElMessage.success('博客目录设置成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '设置目录失败')
  }
}

// 选择目录
const selectDirectory = async () => {
  try {
    const res = await api.get('/api/file-dialog/select_directory')
    if (res.data.error) {
      ElMessage.error('打开文件选择对话框失败：' + res.data.error)
      return
    }
    if (res.data.cancelled) {
      return
    }
    if (res.data.directory) {
      tempPath.value = res.data.directory
      await saveBlogPath()
    }
  } catch (error) {
    ElMessage.error('选择目录失败：' + error.message)
  }
}

// 页面跳转
const navigateTo = (path) => {
  router.push(path)
}

onMounted(() => {
  getBlogPath()
  getStatistics()
  getServerStatus()
})
</script>

<template>
  <div class="home-container">
    <el-row :gutter="20">
      <!-- 博客目录卡片 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
        <el-card class="blog-path-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Folder /></el-icon> 博客目录</span>
              <div class="header-actions">
                <el-button type="primary" size="small" @click="selectDirectory">
                  <el-icon><FolderOpened /></el-icon> 选择目录
                </el-button>
                <el-button v-if="!isEditing" type="primary" size="small" @click="isEditing = true">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
              </div>
            </div>
          </template>
          <!-- 博客路径选择 -->
          <div class="blog-path-content">
            <template v-if="isEditing">
              <el-input
                v-model="tempPath"
                placeholder="请输入博客目录路径"
                size="small"
                class="path-input"
              >
                <template #append>
                    <el-button-group>
                    <el-button type="primary" @click="saveBlogPath">保存</el-button>
                    <el-button @click="isEditing = false">取消</el-button>
                    </el-button-group>
                </template>
              </el-input>
            </template>
            <div v-else class="blog-path">{{ blogPath || '未设置博客目录' }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- 统计数据卡片 -->
      <el-col :xs="24" :sm="8" :md="8" :lg="8" :xl="8">
        <el-card class="stat-card" shadow="hover" v-loading="loading">
          <div class="stat-item">
            <el-icon class="stat-icon"><Document /></el-icon>
            <div class="stat-content">
              <div class="stat-title">文章数量</div>
              <div class="stat-value">{{ statistics.posts }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8" :md="8" :lg="8" :xl="8">
        <el-card class="stat-card" shadow="hover" v-loading="loading">
          <div class="stat-item">
            <el-icon class="stat-icon"><Collection /></el-icon>
            <div class="stat-content">
              <div class="stat-title">分类数量</div>
              <div class="stat-value">{{ statistics.categories }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8" :md="8" :lg="8" :xl="8">
        <el-card class="stat-card" shadow="hover" v-loading="loading">
          <div class="stat-item">
            <el-icon class="stat-icon"><PriceTag /></el-icon>
            <div class="stat-content">
              <div class="stat-title">标签数量</div>
              <div class="stat-value">{{ statistics.tags }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 快捷操作卡片 -->
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="action-card" shadow="hover" @click="navigateTo('/posts/new')">
          <el-icon class="action-icon"><EditPen /></el-icon>
          <div class="action-text">写文章</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="action-card" shadow="hover" @click="navigateTo('/posts')">
          <el-icon class="action-icon"><Document /></el-icon>
          <div class="action-text">文章管理</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="action-card" shadow="hover" @click="navigateTo('/images')">
          <el-icon class="action-icon"><Picture /></el-icon>
          <div class="action-text">图片管理</div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="action-card" shadow="hover" @click="navigateTo('/settings')">
          <el-icon class="action-icon"><Setting /></el-icon>
          <div class="action-text">系统设置</div>
        </el-card>
      </el-col>

      <!-- 服务器管理卡片 -->
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="action-card" shadow="hover" v-loading="serverLoading">
          <el-icon class="action-icon" :class="{ 'running': serverStatus }"><Monitor /></el-icon>
          <div class="action-text">服务器管理</div>
          <el-button 
            :type="serverStatus ? 'danger' : 'success'"
            size="small"
            class="server-button"
            @click="serverStatus ? stopServer() : startServer()"
          >
            {{ serverStatus ? '停止服务器' : '启动服务器' }}
          </el-button>
        </el-card>
      </el-col>

      <!-- 博客部署卡片 -->
      <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card class="action-card" shadow="hover" v-loading="deployLoading" @click="deployBlog">
          <el-icon class="action-icon"><Upload /></el-icon>
          <div class="action-text">部署博客</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home-container {
  padding: 20px;
}

/* 统计数据卡片调整 */
.stat-card .stat-item{
 transform: translateY(-10%); 
}

/* 目录选择路径 */
.blog-path-card {
  margin-bottom: 25px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .el-icon {
  margin-right: 5px;
}

.blog-path {
  font-family: monospace;
  padding: 12px;
  border-radius: 4px;
  word-break: break-all;
}

.stat-card {
  margin-bottom: 25px;
  border-radius: 8px;
  height: 100px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  font-size: 36px;
  margin-right: 15px;
  padding: 10px;
  border-radius: 8px;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.action-card {
  margin-bottom: 25px;
  cursor: pointer;
  text-align: center;
  padding: 25px 15px;
  border-radius: 8px;
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px var(--shadow-color);
}

.action-icon {
  font-size: 16px;
  margin-bottom: 15px;
  padding: 12px;
  border-radius: 12px;
  box-sizing: content-box;
}

.action-text {
  font-size: 16px;
  font-weight: 500;
}

/* 服务器状态样式 */
.action-icon.running {
  color: #67C23A;
}

.server-button {
  margin-top: 10px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .home-container {
    padding: 15px;
  }
  
  .stat-card {
    margin-bottom: 15px;
  }
  
  .action-card {
    margin-bottom: 15px;
    height: 120px;
    padding: 15px;
  }
  
  .action-icon {
    font-size: 30px;
    padding: 10px;
  }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.blog-path-content {
  display: flex;
  flex-direction: column;
}

.path-input {
  width: 100%;
}

.path-input :deep(.el-input-group__append) {
  display: flex;
  gap: 8px;
}
</style>
