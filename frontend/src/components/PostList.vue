<template>
  <div class="post-list-container">
    <div class="filter-buttons">
      <el-button @click="resetDateFilter">重置日期筛选</el-button>
      <el-button @click="clearFilter">重置所有筛选</el-button>
    </div>
    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="posts"
      class="post-list"
    >
    <el-table-column
        prop="date"
        label="日期"
        sortable
        width="180"
        column-key="date"
        :filter-method="filterHandler"
      />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag
            :type="row.status === 'published' ? 'success' : 'info'"
            size="small"
          >
            {{ row.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="200">
        <template #default="{ row }">
          <div class="post-title">
            <span>{{ row.title }}</span>
          </div>
        </template>
      </el-table-column>
      
    <el-table-column
        prop="categories"
        label="分类"
        width="120"
        :filters="categoryFilters"
        :filter-method="filterCategory"
        filter-placement="bottom-end"
      >
        <template #default="{ row }">
          <el-tag
            v-for="category in row.categories"
            :key="category"
            size="small"
            class="mx-1"
          >
            {{ category }}
          </el-tag>
        </template>
      </el-table-column>
    <el-table-column
        prop="tags"
        label="标签"
        width="200"
        :filters="tagFilters"
        :filter-method="filterTags"
        filter-placement="bottom-end"
      >
        <template #default="{ row }">
          <el-tag
            v-for="tag in row.tags"
            :key="tag"
            type="info"
            size="small"
            class="mx-1"
          >
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
    <el-table-column label="操作" width="200" fixed="right">
      <template #default="{ row }">
        <el-button-group>
          <el-button
            size="small"
            type="primary"
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </el-button-group>
      </template>
    </el-table-column>
  </el-table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const tableRef = ref()
const props = defineProps({
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

const categoryFilters = computed(() => {
  const categories = new Set()
  props.posts.forEach(post => {
    post.categories.forEach(category => categories.add(category))
  })
  return Array.from(categories).map(category => ({
    text: category,
    value: category
  }))
})

const tagFilters = computed(() => {
  const tags = new Set()
  props.posts.forEach(post => {
    post.tags.forEach(tag => tags.add(tag))
  })
  return Array.from(tags).map(tag => ({
    text: tag,
    value: tag
  }))
})

const resetDateFilter = () => {
  tableRef.value?.clearFilter(['date'])
}

const clearFilter = () => {
  tableRef.value?.clearFilter()
}

const filterHandler = (value, row) => {
  return row.date === value
}

const filterCategory = (value, row) => {
  return row.categories.includes(value)
}

const filterTags = (value, row) => {
  return row.tags.includes(value)
}

const handleEdit = (post) => {
  emit('edit', post)
}

const handleDelete = (post) => {
  emit('delete', post)
}
</script>

<style scoped>
.post-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
}

.filter-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.post-list {
  background: var(--bg-primary);
  border: 1px solid var(--text-primary);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 var(--shadow-color);
}

:deep(.el-table) {
  color: var(--text-primary);
}



.post-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.9em;
}

.el-tag {
  margin: 2px;
}

.el-button-group {
  display: flex;
  gap: 8px;
}
</style>