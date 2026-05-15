import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      title: '首页'
    }
  },
  {
    path: '/posts',


    name: 'Posts',
    component: () => import('../views/Posts.vue'),
    meta: {
      title: '文章管理'
    }
  },
  {
    path: '/posts/new',
    name: 'NewPost',
    component: () => import('../views/PostEdit.vue'),
    meta: {
      title: '写文章'
    }
  },
  {
    path: '/posts/edit/:id',
    name: 'EditPost',
    component: () => import('../views/PostEdit.vue'),
    meta: {
      title: '编辑文章'
    }
  },
  {
    path: '/images',
    name: 'Images',
    component: () => import('../views/Images.vue'),
    meta: {
      title: '图片管理'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    // component: () => import('../views/Settings.vue'),
    meta: {
      title: '设置'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 博客管理系统` : '博客管理系统'
  next()
})

export default router