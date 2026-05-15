<template>
    <MdEditor 
      :modelValue="modelValue"
      @update:modelValue="handleUpdate"
      @onUploadImg="handleImageUpload"
      @onSave="onSave"
      :preview="true"
      :previewOnly="false"
      :editorId="editorId"
      :onPaste="handlePaste"
      :toolbars="toolbars"
      language="zh-CN"
      ref="editorRef"
    >
        <template #defToolbars>
            <Emoji>
                <template #trigger><el-icon><Star /></el-icon></template>
            </Emoji>
        </template>
    </MdEditor>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import '@vavt/cm-extension/dist/previewTheme/arknights.css';
// 引入公共库中的语言配置
import { Emoji } from '@vavt/v3-extension';
import '@vavt/v3-extension/lib/asset/Emoji.css';
// 添加turndown库用于HTML转Markdown
import TurndownService from 'turndown'
// 导入Element Plus消息组件
import { ElMessage } from 'element-plus'
import { uploadImages } from '../api/ImageMange.js'
// Removed unused imports: API_TOKEN, API_BASE_URL

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  editorId: {
    type: String,
    default: 'markdown-editor'
  }
})

// 自定义工具栏
const toolbars = [
  'bold',
  'underline',
  'italic',
  '-',
  'title',
  'strikeThrough',
  'sub',
  'sup',
  'quote',
  'unorderedList',
  'orderedList',
  'task',
  '-',
  'codeRow',
  'code',
  'link',
  0,
  'image',
  'table',
  'mermaid',
  'katex',
  '-',
  'revoke',
  'next',
  'save',
  '=',
  'pageFullscreen',
  'fullscreen',
  'preview',
  'previewOnly',
  'htmlPreview',
  'catalog',
  'github',
];


const emit = defineEmits(['update:modelValue', 'onUploadImg', 'onSave'])

// 自动保存相关变量
const autoSaveInterval = 60000 // 60秒自动保存一次
const lastSaveTime = ref(Date.now())
const hasUnsavedChanges = ref(false)
let autoSaveTimer = null

// 创建编辑器引用
const editorRef = ref(null)

// 创建turndown实例用于HTML到Markdown的转换
const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
  emDelimiter: '*'
})



const handleImageUpload = async (files, callback) => {
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  const invalidFiles = files.filter(file => !allowedTypes.includes(file.type))
  
  if (invalidFiles.length > 0) {
    ElMessage.error('只支持上传jpg、png、gif、webp格式的图片')
    callback([]) // 传递空数组给回调
    return
  }

  try {
    // 调用导入的 uploadImages 函数
    const results = await uploadImages(files)
    
    // 从结果中提取成功上传的图片 URL
    const successfulUploads = results.filter(res => res.status === 'success' && res.url)
    const urls = successfulUploads.map(res => res.url)

    // 处理上传结果
    if (urls.length > 0) {
      callback(urls) // 将成功上传的 URL 传递给编辑器回调
      if (urls.length === files.length) {
        ElMessage.success('所有图片上传成功')
      } else {
        ElMessage.warning(`成功上传 ${urls.length} 张图片，${files.length - urls.length} 张失败`)
        // 可以进一步处理失败的图片信息，例如打印错误日志
        const failedUploads = results.filter(res => res.status !== 'success');
        failedUploads.forEach(fail => console.error('上传失败:', fail.error || '未知错误'));
      }
    } else {
      ElMessage.error('所有图片上传失败')
      // 打印详细错误信息
      results.forEach(res => console.error('上传失败详情:', res.error || '未知错误'));
      callback([]) // 传递空数组给回调
    }
  } catch (error) {
    console.error('图片上传过程发生错误:', error)
    ElMessage.error('图片上传过程发生错误')
    callback([]) // 发生异常时传递空数组
  }
}

// 处理粘贴事件
const handlePaste = (event) => {
  // 获取剪贴板数据
  const clipboardData = event.clipboardData || window.clipboardData
  const html = clipboardData.getData('text/html')
  const text = clipboardData.getData('text/plain')
  
  if (html) {
    event.preventDefault()
    try {
      // 转换HTML为Markdown
      const markdown = turndownService.turndown(html)
      
      // 使用编辑器实例的insert方法在光标位置插入内容
      if (editorRef.value) {
        editorRef.value.insert(() => ({
          targetValue: markdown,
          select: true,
          deviationStart: 0,
          deviationEnd: 0
        }))
        // 阻止默认粘贴行为
        return true
      }
    } catch (error) {
      console.error('转换过程出错:', error)
      return false
    }
  }
  
  // 如果没有HTML内容，使用默认粘贴行为
  return false
}

// 添加更新处理函数
const handleUpdate = (value) => {
  emit('update:modelValue', value)
  hasUnsavedChanges.value = true
}

// 自动保存函数
const autoSave = async () => {
  const now = Date.now()
  if (hasUnsavedChanges.value && (now - lastSaveTime.value >= autoSaveInterval)) {
    try {
      emit('onSave')
      lastSaveTime.value = now
      hasUnsavedChanges.value = false
      // ElMessage.success('自动保存成功')
    } catch (error) {
      console.error('自动保存错误:', error)
      ElMessage.error('自动保存失败')
    }
  }
}

// 手动保存函数
const onSave = () => {
  autoSave()
}

// 组件挂载时启动自动保存
onMounted(() => {
  autoSaveTimer = setInterval(autoSave, autoSaveInterval)
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
  // 如果有未保存的更改，进行最后一次保存
  if (hasUnsavedChanges.value) {
    autoSave()
  }
})
</script>

<style scoped>
.md-editor {
  padding-top: 10px;
  height: 100%;
}

:deep(.md-editor-toolbar) {
  padding: 8px !important;
}

:deep(.md-editor-toolbar svg) {
  width: 1.5em !important;
  height: 1.5em !important;
}

:deep(.md-editor-toolbar button) {
  padding: 6px !important;
  margin: 0 2px !important;
}

:deep(.md-editor-input) {
  font-size: 16px !important;
}

:deep(.md-editor-preview) {
  font-size: 16px !important;
}
</style>