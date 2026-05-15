<script setup>
import Sidebar from './components/Sidebar.vue';
import './style.css'
import { ref, onMounted, onUnmounted, provide } from 'vue'

// 控制侧边栏折叠状态
const isCollapse = ref(false)
// 判断是否为移动设备
const isMobile = ref(true)
//自动控制 ture 折叠 false 展开

// 检测设备类型和窗口大小
const checkDevice = () => {
  // isMobile.value = window.innerWidth < 768
  isCollapse.value = isMobile.value
}

// 组件挂载时添加窗口大小变化监听
onMounted(() => {
  checkDevice()
  window.addEventListener('resize', checkDevice)
})

// 组件卸载时移除监听器
onUnmounted(() => {
  window.removeEventListener('resize', checkDevice)
})

// 主题切换逻辑
const isDark = ref(localStorage.getItem('theme') === 'dark')
const toggleDark = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

// 初始化主题
onMounted(() => {
  document.documentElement.classList.toggle('dark', isDark.value)
})

// 提供主题相关的变量和方法给子组件
provide('isDark', isDark)
provide('toggleDark', toggleDark)
</script>

<template>
  <div id="app" :class="{ 'dark': isDark }">
    <el-container class="container">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="aside-container">
        <Sidebar :is-collapse="isCollapse" @toggle-collapse="isCollapse = !isCollapse" />
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container class="main-container">
        <el-scrollbar>
          <!-- 头部 -->
          <el-header height="60px" class="header" style="">
            <el-button 
              type="text" 
              class="toggle-btn"
              @click="isCollapse = !isCollapse"
            >
              <el-icon :size="20">
                <Fold v-if="!isCollapse"/>
                <Expand v-else/>
              </el-icon>
            </el-button>
          </el-header>
          <!-- 主体 -->
          <el-main>
            <router-view></router-view>
          </el-main>
        </el-scrollbar>
      </el-container>
    </el-container>
  </div>
</template>

<style>
#app {
  width: 100%;
  height: 100vh;
}
.el-main{
  height: 100vh;
}

.el-aside {
  overflow: hidden!important;
}

.container {
  height: 100%;
}

.aside-container {
  transition: width 0.3s;
  box-shadow: 0 0 10px var(--shadow-color);
  z-index: 1000;
}

.header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px var(--shadow-color);
}

.header-title {
  margin-left: 20px;
  font-size: 18px;
  font-weight: bold;
}

.toggle-btn {
  padding: 7px;
  border-radius: 4px;
}

.el-scrollbar  {
  width: 100%;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .aside-container {
    position: fixed;
    height: 100vh;
  }
  
  .main-container {
    margin-left: 64px;
  }
  
  .el-main {
    padding: 15px;
  }
}
</style>
