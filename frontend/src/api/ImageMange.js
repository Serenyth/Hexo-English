import { ElMessage } from 'element-plus'

export const API_TOKEN = '1743|SRfZ9HMQXdQqKLwqM3BMm9wcke3JwWgB5y8DSgtw'
export const API_BASE_URL = 'https://7bu.top/api/v1'

// 从本地存储加载缓存的图片列表
export const loadCachedImages = () => {
  const cachedData = localStorage.getItem('cachedImageList')
  if (cachedData) {
    try {
      const { data, timestamp } = JSON.parse(cachedData)
      // 检查缓存是否在5分钟内
      if (Date.now() - timestamp < 0.5 * 60 * 1000) {
        return { success: true, data }
      }
    } catch (error) {
      console.error('Failed to parse cached data:', error)
    }
  }
  return { success: false }
}

// 缓存图片列表到本地存储
export const cacheImages = (data) => {
  try {
    localStorage.setItem('cachedImageList', JSON.stringify({
      data,
      timestamp: Date.now()
    }))
  } catch (error) {
    console.error('Failed to cache images:', error)
  }
}

// 获取图片列表
export const fetchImages = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/images`, {
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Accept': 'application/json'
      }
    })
    const responseData = await response.json()
    if (response.ok && responseData.status) {
      const imagesData = responseData.data.data || []
      const filteredData = imagesData.filter(item => item && item.key)
      // 缓存新的图片列表
      cacheImages(filteredData)
      return { success: true, data: filteredData }
    } else {
      throw new Error(responseData.message || '获取图片列表失败')
    }
  } catch (error) {
    return { success: false, error: error.message }
  }
}

// 上传图片
export const uploadImages = async (files) => {
  const uploadPromises = files.map(async file => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
          'Accept': 'application/json'
        },
        body: formData
      })

      const result = await response.json()

      if (response.ok && result.status && result.data && result.data.links && result.data.links.url) {
        return {
          status: 'success',
          url: result.data.links.url
        }
      } else {
        // 如果API返回了错误消息，使用它，否则提供通用错误
        const errorMessage = result.message || `上传失败: ${response.status}`;
        return {
          status: 'error',
          error: errorMessage,
          fileName: file.name // 包含文件名以方便调试
        }
      }
    } catch (error) {
      // 网络错误或其他异常
      return {
        status: 'error',
        error: error.message || '网络错误或上传异常',
        fileName: file.name
      }
    }
  })

  // 等待所有上传完成
  return Promise.all(uploadPromises)
}

// 删除图片
export const deleteImage = async (imageId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/images/${imageId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Accept': 'application/json'
      }
    })

    const data = await response.json()
    if (response.ok) {
      return { success: true }
    } else {
      throw new Error(data.message || '图片删除失败')
    }
  } catch (error) {
    return { success: false, error: error.message }
  }
}

// 复制URL到剪贴板
export const copyUrl = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    return { success: true }
  } catch (error) {
    return { success: false, error: '复制URL失败' }
  }
}