import api from './index.js'

// 创建FormData对象的工具函数
const createPostFormData = (data) => {
  const formData = new FormData()
  formData.append('title', data.title)
  formData.append('content', data.content || '')
  formData.append('date', data.date ? new Date(data.date).toISOString() : new Date().toISOString())
  formData.append('updated', new Date().toISOString())
  formData.append('status', data.status || 'draft')
  
  // 处理数组类型的数据
  if (data.tags && data.tags.length > 0) {
    formData.append('tags', Array.isArray(data.tags) ? data.tags.join(',') : data.tags)
  }
  
  if (data.categories && data.categories.length > 0) {
    formData.append('categories', Array.isArray(data.categories) ? data.categories.join(',') : data.categories)
  }
  
  // 添加其他可选字段
  const optionalFields = [
    'cover', 'author', 'layout', 'description', 'keywords'
  ]
  
  optionalFields.forEach(field => {
    if (data[field]) formData.append(field, data[field])
  })
  
  // 添加布尔值字段
  formData.append('comments', data.comments ?? true)
  formData.append('top', data.top ?? false)
  
  // 添加自定义字段
  if (data.customFields) {
    formData.append('customFields', JSON.stringify(data.customFields))
  }
  
  return formData
}

// 获取文章列表
export const getPostList = () => {
  return api.get('/api/posts/list')
}

// 获取文章详情
export const getPostDetail = (filename) => {
  return api.get(`/api/posts/detail/${filename}`)
}

// 创建新文章
export const createPost = (data) => {
  const formData = createPostFormData(data)
  return api.post('/api/posts/create', formData)
}

// 更新文章
export const updatePost = (filename, data) => {
  const formData = createPostFormData(data)
  return api.put(`/api/posts/update/${filename}`, formData)
}

// 删除文章
export const deletePost = (filename) => {
  return api.delete(`/api/posts/delete/${filename}`)
}