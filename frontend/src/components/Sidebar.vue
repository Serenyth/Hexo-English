<script setup>
// 导入所需的 Vue 功能
import { ref, inject } from 'vue'  // 增加 inject 导入
import { useRouter, useRoute } from 'vue-router'  // 用于路由导航
import { watch } from 'vue'

// 导入 Element Plus 的图标组件
import {
  HomeFilled,
  Document,
  Picture,
  Setting,
  Moon,
  Sunny
} from '@element-plus/icons-vue'
// @element-plus/icons-vue 是 Element Plus 提供的图标库

// 接收父组件传递的折叠状态
const props = defineProps({
  isCollapse: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emit = defineEmits(['toggleCollapse'])

const router = useRouter()
const route = useRoute()
const activeMenu = ref('/')

// 注入暗黑模式变量和切换函数
const isDark = inject('isDark', ref(false))
const toggleDark = inject('toggleDark', () => {})

// 监听路由变化，更新激活菜单
watch(() => route.path, (newPath) => {
  activeMenu.value = newPath
}, { immediate: true })

// 菜单项点击处理函数
const handleSelect = (path) => {
  router.push(path) // 路由跳转到对应页面
}

// 折叠按钮处理函数
const toggleCollapse = () => {
  emit('toggleCollapse')
}
</script>

<template>
  <el-menu
    class="sidebar-menu"
    :default-active="activeMenu"  
    :collapse="isCollapse"
    @select="handleSelect"
    :text-color="isDark ? '#e5e7eb' : '#303133'"
    :active-text-color="isDark ? '#60a5fa' : '#409EFF'"
  >


    <!-- 首页菜单项 -->
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <template #title>首页</template>
    </el-menu-item>

    <!-- 文章管理菜单项 -->
    <el-menu-item index="/posts">
      <el-icon><Document /></el-icon>
      <template #title>文章管理</template>
    </el-menu-item>

    <!-- 图片管理菜单项 -->
    <el-menu-item index="/images">
      <el-icon><Picture /></el-icon>
      <template #title>图片管理</template>
    </el-menu-item>
    
    <!-- 设置菜单项 -->
    <el-menu-item index="/settings">
      <el-icon><Setting /></el-icon>
      <template #title>设置</template>
    </el-menu-item>
    
    <!-- 黑暗模式切换 -->
    <div class="theme-switch" :class="{ 'collapsed': isCollapse, 'dark': isDark }">
      <el-tooltip :content="isDark ? '切换到亮色模式' : '切换到暗色模式'" placement="right" :disabled="!isCollapse">
        <div class="switch-btn" @click="toggleDark()">
          <el-icon v-if="isDark"><Sunny /></el-icon>
          <el-icon v-else><Moon /></el-icon>
          <span v-if="!isCollapse">{{ isDark ? '亮色模式' : '暗色模式' }}</span>
        </div>
      </el-tooltip>
    </div>
  </el-menu>
</template>

<style scoped>
.sidebar-menu {
  height: 100vh;
  border-right: none;
  transition: all 0.3s;
  overflow: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  border-bottom: 1px solid #f2f2f2;
  transition: all 0.3s;
}

.logo-small {
  height: 30px;
  transition: all 0.3s;
}

.el-menu-item {
  border-left: 3px solid transparent;
}

.theme-switch {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  padding: 0 20px;
  transition: all 0.3s;
}

.theme-switch.collapsed {
  padding: 0 20px;
  display: flex;
  justify-content: center;
}

.theme-switch.dark {
  color: #e5e7eb;
}

.switch-btn {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  border-radius: 6px;
  transition: all 0.3s;
}


.switch-btn .el-icon {
  margin-right: 10px;
  font-size: 18px;
}

.theme-switch.collapsed .switch-btn .el-icon {
  margin-right: 0;
}
</style>