<template>
  <div class="post-timeline" v-loading="loading">
    <el-timeline>
      <el-timeline-item
        v-for="post in posts"
        :key="post.id"
        :timestamp="post.date"
        placement="top"
      >
        <el-card class="timeline-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <h3>{{ post.title }}</h3>
                <el-tag 
                  :type="post.status === 'published' ? 'success' : 'info'"
                  size="small"
                >
                  {{ post.status === 'published' ? '已发布' : '草稿' }}
                </el-tag>
              </div>
              <div class="card-actions">
                <el-button-group>
                  <el-button size="small" type="primary" @click="handleEdit(post)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button size="small" type="danger" @click="handleDelete(post)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
            </div>
          </template>
          <div class="card-content">
            <div class="card-tags">
              <div class="categories">
                <el-tag
                  v-for="category in post.categories"
                  :key="category"
                  size="small"
                  class="mx-1"
                >
                  {{ category }}
                </el-tag>
              </div>
              <div class="tags">
                <el-tag
                  v-for="tag in post.tags"
                  :key="tag"
                  type="info"
                  size="small"
                  class="mx-1"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup>
import { Edit, Delete } from '@element-plus/icons-vue'

defineProps({
  posts: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete'])

const handleEdit = (post) => {
  emit('edit', post)
}

const handleDelete = (post) => {
  emit('delete', post)
}
</script>

<style scoped>
.post-timeline {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 1.1em;
  flex: 1;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.categories,
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.el-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.el-button-group {
  display: flex;
  gap: 8px;
}

</style>