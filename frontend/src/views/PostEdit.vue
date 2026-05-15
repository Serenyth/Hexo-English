<template>
    <div class="header">
      <div class="title-section">
        <!-- 修改按钮图标的使用方式 -->
        <el-button 
          class="toggle-btn"
          @click="toggleFrontMatter"
          circle
          plain
        >
          <el-icon>
            <component :is="frontMatterVisible ? ArrowRight : ArrowLeft" />
          </el-icon>
        </el-button>
      </div>

      <div class="actions" style="">
          <el-button @click="handleCancel">返回</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          <el-button type="success" @click="handlePublish" :loading="publishing">发布</el-button>
        </div>
    </div>

    <div class="main-content">
      <div 
        class="front-matter-drawer"
        :class="{ 'drawer-visible': frontMatterVisible }"
      >
      <div class="tools">
        <div class="title-section">
          <h4>{{ isNewPost ? '新建文章' : '编辑文章' }}</h4>
        </div>
        <div class="actions">
          <el-button @click="handleCancel">返回</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          <el-button type="success" @click="handlePublish" :loading="publishing">发布</el-button>
        </div>
      </div>
        <!-- 文件头部信息 -->
        <FrontMatter
          v-model:title="post.title"
          v-model:date="post.date"
          v-model:updated="post.updated"
          v-model:categories="post.categories"
          v-model:tags="post.tags"
          v-model:status="post.status"
          v-model:cover="post.cover"
        />
      </div>
      
      <div class="editor-section" :class="{ 'full-width': !frontMatterVisible }">
        <div class="md-editor-wrapper">
          <!-- 文章编辑器导入 -->
          <MarkdownEditor
            v-model="post.content"
            :editorId="'post-editor'"
            @update:modelValue="() => hasUnsavedChanges = true"
          />
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
// 添加图标导入
import { ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPostDetail, createPost, updatePost } from '../api/posts'
import FrontMatter from '../components/FrontMatter.vue'
import MarkdownEditor from '../components/MarkdownEditor.vue'

// 用于跟踪未保存的更改
const hasUnsavedChanges = ref(false)

const route = useRoute()
const router = useRouter()

const isNewPost = computed(() => !route.params.id)

const post = ref({
  title: '',
  date: new Date().toISOString().split('T')[0],
  updated: new Date().toISOString().split('T')[0],
  categories: [],
  tags: [],
  content: '',
  status: 'draft',
  cover: '' // 确保初始化包含cover属性
})

// 删除这个版本的 fetchPost
// const fetchPost = async () => {
//   if (!isNewPost.value) {
//     try {
//       const response = await getPostDetail(route.params.id)
//       post.value = {
//         ...response.data,
//         date: response.data.date || new Date().toISOString().split('T')[0],
//         updated: response.data.updated || new Date().toISOString().split('T')[0]
//       }
//     } catch (error) {
//       ElMessage.error('获取文章失败')
//       console.error('获取文章失败:', error)
//     }
//   }
// }

const saving = ref(false)
const publishing = ref(false)
const frontMatterVisible = ref(true)

const toggleFrontMatter = () => {
  frontMatterVisible.value = !frontMatterVisible.value
}

const validatePost = () => {
  if (!post.value.title.trim()) {
    ElMessage.warning('请输入文章标题')
    return false
  }
  // if (!post.value.content.trim()) {
  //   ElMessage.warning('请输入文章内容')
  //   return false
  // }
  return true
}

// 如果是编辑模式，获取文章数据
const fetchPost = async () => {
  if (!isNewPost.value) {
    try {
      const response = await getPostDetail(route.params.id)
      console.log('Fetched post:', response);
      console.log('API返回的cover值:', response.cover);
      post.value = {
        ...response,
        date: response.date || new Date().toISOString().split('T')[0],
        updated: response.updated || new Date().toISOString().split('T')[0],
        cover: response.cover || '' // 确保cover属性被正确赋值
      }
      console.log('更新后的post对象:', post.value);
    } catch (error) {
      ElMessage.error('获取文章失败')
      console.error('获取文章失败:', error)
    }
  }
}

// const handleContentChange = (content) => {
//   post.value.content = content
// }

const handleSave = async () => {
  if (!validatePost()) return
  
  try {
    saving.value = true

    // 添加日志记录
    console.log('Saving content:', JSON.stringify(post.value.content));

    if (isNewPost.value) {
      const response = await createPost(post.value)
      ElMessage.success('创建成功')
      // 如果是新文章，保存后需要更新路由以反映新的文章ID
      if (isNewPost.value && response && response.id) {
        router.replace(`/edit/${response.id}`)
      }
    } else {
      await updatePost(route.params.id, post.value)
      ElMessage.success('保存成功')
    }
    
    // 移除这行代码，不再跳转到文章列表
    // router.push('/posts')
    
    // 标记没有未保存的更改
    hasUnsavedChanges.value = false
  } catch (error) {
    ElMessage.error(error.response?.message || '保存失败')
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const handlePublish = async () => {
  if (!validatePost()) return
  
  try {
    publishing.value = true
    post.value.status = 'published'

    // 添加日志记录
    console.log('Publishing content:', JSON.stringify(post.value.content));
    
    if (isNewPost.value) {
      await createPost(post.value)
      ElMessage.success('发布成功')
    } else {
      await updatePost(route.params.id, post.value)
      ElMessage.success('发布成功')
    }
    
    // 发布后返回文章列表
    router.push('/posts')
  } catch (error) {
    ElMessage.error(error.response?.message || '发布失败')
    console.error('发布失败:', error)
  } finally {
    publishing.value = false
  }
}

const handleCancel = async () => {
  if (hasUnsavedChanges.value) {
    const { ElMessageBox } = await import('element-plus')
    try {
      const action = await ElMessageBox.confirm(
        '有未保存的更改，是否保存？',
        '提示',
        {
          confirmButtonText: '保存',
          cancelButtonText: '不保存',
          type: 'warning',
          distinguishCancelAndClose: true,
          showClose: true,
        }
      )
      if (action === 'confirm') {
        await handleSave()
      }
    } catch (action) {
      if (action !== 'cancel') {
        return
      }
    }
  }
  router.push('/posts')
}

onMounted(() => {
  fetchPost()
})


</script>

<style scoped>
.header {
  padding: 6px 16px;
  display: flex; 
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color-light);
}

.tools {
  display: flex;
  flex-direction: column;
  align-items: start;
  margin-bottom: 20px;
  padding: 6px 16px;
}

.header h4{
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  padding-bottom: 6px;
}

.title-section {
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 12px;
}

.toggle-btn {
  transition: transform 0.3s ease;
}

.actions {
  display: flex;
  gap: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  position: relative;
  min-height: 0;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  overflow: hidden;
}

.front-matter-drawer {
  width: 300px;
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1;
}

.drawer-visible {
  transform: translateX(0);
}

.editor-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

.editor-section.full-width {
  margin-left: 0;
}

.md-editor-wrapper {
  flex: 1;
  height: 100vh;
}

</style>