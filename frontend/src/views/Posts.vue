<template>
  <div class="posts-container">
    <div class="header">
      <div class="filters">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文章标题"
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="selectedStatus"
          placeholder="选择状态"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="草稿" value="draft">
            <div class="flex-center">
              <el-tag type="info" size="small" class="option-tag">草稿</el-tag>
            </div>
          </el-option>
          <el-option label="已发布" value="published">
            <div class="flex-center">
              <el-tag type="success" size="small" class="option-tag">已发布</el-tag>
            </div>
          </el-option>
        </el-select>

        <el-select
          v-model="selectedCategory"
          placeholder="选择分类"
          multiple
          clearable
          collapse-tags
          collapse-tags-tooltip
          class="filter-select"
          @change="handleFilter"
        >
          <el-option
            v-for="category in categories"
            :key="category"
            :label="category"
            :value="category"
          >
            <div class="flex-center">
              <el-tag size="small" class="option-tag">{{ category }}</el-tag>
            </div>
          </el-option>
        </el-select>
        
        <el-select
          v-model="selectedTag"
          placeholder="选择标签"
          multiple
          clearable
          collapse-tags
          collapse-tags-tooltip
          class="filter-select"
          @change="handleFilter"
        >
          <el-option
            v-for="tag in tags"
            :key="tag"
            :label="tag"
            :value="tag"
          >
            <div class="flex-center">
              <el-tag type="info" size="small" class="option-tag">{{ tag }}</el-tag>
            </div>
          </el-option>
        </el-select>
      </div>

      <div class="actions">
        <el-radio-group v-model="viewMode" size="large">
          <el-radio-button label="list">
            <el-icon><List /></el-icon>
          </el-radio-button>
          <el-radio-button label="card">
            <el-icon><Grid /></el-icon>
          </el-radio-button>
          <el-radio-button label="timeline">
            <el-icon><Timer /></el-icon>
          </el-radio-button>
        </el-radio-group>

        <el-button type="primary" @click="handleNewPost">
          <el-icon><Plus /></el-icon>新建文章
        </el-button>
      </div>
    </div>

    <PostList
      v-if="viewMode === 'list'"
      :posts="filteredPosts"
      :loading="loading"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <PostCard
      v-else-if="viewMode === 'card'"
      :posts="filteredPosts"
      :loading="loading"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <PostTimeline
      v-else
      :posts="filteredPosts"
      :loading="loading"
      @edit="handleEdit"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus, List, Grid, Timer } from '@element-plus/icons-vue'
// import axios from 'axios' // Removed direct axios import
import { getPostList, deletePost } from '../api/posts' // Import API functions
import { ElMessage, ElMessageBox } from 'element-plus'
import PostList from '../components/PostList.vue'
import PostCard from '../components/PostCard.vue'
import PostTimeline from '../components/PostTimeline.vue'

const router = useRouter()
const posts = ref([])
const categories = ref([])
const tags = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref([])
const selectedTag = ref([])
const viewMode = ref('list') // 默认列表视图

// 获取所有文章列表
const fetchPosts = async () => {
  try {
    loading.value = true
    // Use imported API function
    const response = await getPostList()
    posts.value = response // Assuming response structure is { data: [...] } based on api/index.js interceptor
    
    // 提取所有分类和标签
    const categorySet = new Set()
    const tagSet = new Set()
    
    posts.value.forEach(post => {
      post.categories?.forEach(category => categorySet.add(category))
      post.tags?.forEach(tag => tagSet.add(tag))
    })
    
    categories.value = Array.from(categorySet)
    tags.value = Array.from(tagSet)
  } catch (error) {
    ElMessage.error('获取文章列表失败')
    console.error('获取文章列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 过滤文章列表
const selectedStatus = ref('')

// 修改 filteredPosts 计算属性
const filteredPosts = computed(() => {
  return posts.value.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value.length === 0 || 
      post.categories?.some(category => selectedCategory.value.includes(category))
    const matchesTag = selectedTag.value.length === 0 || 
      post.tags?.some(tag => selectedTag.value.includes(tag))
    const matchesStatus = !selectedStatus.value || post.status === selectedStatus.value
    return matchesSearch && matchesCategory && matchesTag && matchesStatus
  })
})

// 搜索处理
const handleSearch = () => {
  // 搜索已通过计算属性自动处理
}

// 筛选处理
const handleFilter = () => {
  // 筛选已通过计算属性自动处理
}

// 新建文章
const handleNewPost = () => {
  router.push('/posts/new')
}

// 编辑文章
const handleEdit = (post) => {
  router.push(`/posts/edit/${post.filename}`)
}

// 删除文章
const handleDelete = async (post) => {
  try {
    // Use the post title in the confirmation message for clarity
    await ElMessageBox.confirm(`确定要删除文章 "${post.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // Use imported API function
    await deletePost(post.filename) // Use filename as identifier based on original code
    ElMessage.success('文章删除成功')
    await fetchPosts() // 重新获取文章列表
  } catch (error) {
    if (error !== 'cancel') {
      // Use error message from response if available, otherwise provide a generic message
      const message = error?.response?.data?.message || '删除文章失败'
      ElMessage.error(message)
      console.error('删除文章失败:', error)
    }
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.posts-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 16px;
  padding: 16px 6px;
}

.search-input {
  width: 300px;
}

.actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.filter-select {
  min-width: 200px;
}

.flex-center {
  display: flex;
  align-items: center;
}

.option-tag {
  margin-right: 8px;
}
</style>