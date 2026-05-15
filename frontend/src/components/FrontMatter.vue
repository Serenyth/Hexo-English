<template>
  <div class="front-matter">
    <el-form label-position="top" :model="formData" :rules="rules" ref="formRef">
      <el-form-item label="标题">
        <el-input
          v-model="formData.title"
          placeholder="请输入文章标题"
          @input="handleTitleChange"
        />
      </el-form-item>

      <el-form-item label="发布日期">
        <el-date-picker 
          v-model="formData.date" 
          type="date" 
          placeholder="选择发布日期" 
          style="width: 100%"
          value-format="YYYY-MM-DD" 
          format="YYYY-MM-DD"
          @change="handleDateChange"
        />
      </el-form-item>

      <el-form-item label="更新日期">
        <el-date-picker 
          v-model="formData.updated" 
          type="date" 
          placeholder="选择更新日期" 
          style="width: 100%"
          value-format="YYYY-MM-DD" 
          format="YYYY-MM-DD"
          @change="handleUpdatedChange"
        />
      </el-form-item>

      <el-form-item label="封面">
        <div class="cover-upload">
          <el-input 
            v-model="formData.cover" 
            placeholder="请输入封面图片URL" 
            clearable
            @input="handleCoverChange"
          >
            <template #prefix>
              <el-icon>
                <Picture />
              </el-icon>
            </template>
          </el-input>
          <div v-if="formData.cover" class="cover-preview">
            <el-image :src="formData.cover" fit="cover" class="cover-image" />
            <el-button type="danger" link @click="clearCover">删除</el-button>
          </div>
        </div>
      </el-form-item>

      <!-- 其他表单项保持不变 -->
      <el-form-item label="分类">
        <el-select
          v-model="formData.categories"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="请选择或创建分类"
          @change="handleCategoriesChange"
        >
          <el-option
            v-for="item in categoryOptions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="标签">
        <el-select
          v-model="formData.tags"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="请选择或创建标签"
          @change="handleTagsChange"
        >
          <el-option
            v-for="item in tagOptions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="状态">
        <el-radio-group 
          v-model="formData.status" 
          size="large"
          @change="handleStatusChange"
        >
          <el-radio-button label="draft">草稿</el-radio-button>
          <el-radio-button label="published">发布</el-radio-button>
        </el-radio-group>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import api from '../api/index' // 导入配置好的axios实例
import { Picture } from '@element-plus/icons-vue'

const formRef = ref(null)

const rules = {
  title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
  date: [{ required: true, message: '请选择发布日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择文章状态', trigger: 'change' }]
}

// 本地状态
const categoryOptions = ref([])
const tagOptions = ref([])

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  date: {
    type: String,
    required: true
  },
  updated: {
    type: String,
    default: ''
  },
  categories: {
    type: Array,
    required: true
  },
  tags: {
    type: Array,
    required: true
  },
  status: {
    type: String,
    required: true
  },
  cover: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'update:title',
  'update:date',
  'update:updated',
  'update:categories',
  'update:tags',
  'update:status',
  'update:cover'
])

// 表单数据对象
const formData = ref({
  title: '',
  date: '',
  updated: '',
  categories: [],
  tags: [],
  status: '',
  cover: ''
})

// 初始化表单数据
const initFormData = () => {
  formData.value = {
    title: props.title,
    date: props.date,
    updated: props.updated,
    categories: props.categories,
    tags: props.tags,
    status: props.status,
    cover: props.cover
  }
}

// 修改监听逻辑
watch(() => ({
  title: props.title,
  date: props.date,
  updated: props.updated,
  categories: props.categories,
  tags: props.tags,
  status: props.status,
  cover: props.cover
}), (newProps) => {
  console.log('FrontMatter props变化，cover值:', props.cover)
  formData.value = { ...newProps }
  console.log('formData更新后，cover值:', formData.value.cover)
}, { immediate: true, deep: true })

// 事件处理函数
const handleTitleChange = (value) => {
  emit('update:title', value)
}

const handleDateChange = (value) => {
  emit('update:date', value)
}

const handleUpdatedChange = (value) => {
  emit('update:updated', value)
}

const handleCoverChange = (value) => {
  console.log('封面URL变更:', value)
  emit('update:cover', value)
}

const clearCover = () => {
  formData.value.cover = ''
  emit('update:cover', '')
  console.log('封面已清除')
}

const handleCategoriesChange = (value) => {
  emit('update:categories', value)
}

const handleTagsChange = (value) => {
  emit('update:tags', value)
}

const handleStatusChange = (value) => {
  emit('update:status', value)
}

// 获取所有分类和标签选项
const fetchOptions = async () => {
  try {
    // 使用配置好的api实例发起请求
    const response = await api.get('/api/posts/list')
    const posts = response

    if (!posts || !Array.isArray(posts)) {
      console.error('获取分类和标签选项失败: posts数据无效')
      return
    }
    
    const categorySet = new Set()
    const tagSet = new Set()

    posts.forEach(post => {
      post.categories?.forEach(category => categorySet.add(category))
      post.tags?.forEach(tag => tagSet.add(tag))
    })

    categoryOptions.value = Array.from(categorySet)
    tagOptions.value = Array.from(tagSet)
  } catch (error) {
    console.error('获取分类和标签选项失败:', error)
  }
}

// 监听props变化，更新表单数据
watch(props, (newProps) => {
  console.log('props变化:', newProps);
  console.log('props.cover值:', props.cover);
  initFormData();
}, { deep: true, immediate: true })

// 移除onMounted中的initFormData调用，因为watch的immediate:true会确保组件挂载时执行
onMounted(() => {
  console.log('FrontMatter组件挂载，初始props:', props);
  console.log('FrontMatter组件挂载，初始formData:', formData.value);
  fetchOptions()
})
</script>

<style scoped>
.front-matter {
  height: 100%;
  padding: 16px;
  overflow-y: auto;
  background-color: var(--el-bg-color);
}

.el-form-item {
  margin-bottom: 16px;
}

:deep(.el-form-item__label) {
  padding-bottom: 4px;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-date-picker) {
  width: 100%;
}

.cover-upload {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cover-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.cover-image {
  width: 100%;
  height: 150px;
  border-radius: 4px;
  object-fit: cover;
}
</style>
