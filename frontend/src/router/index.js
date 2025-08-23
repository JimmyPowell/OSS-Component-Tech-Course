import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth.js';
import MainLayout from '../layout/MainLayout.vue';
import Home from '../views/Home.vue';
import ResourceDetailPage from '../views/ResourceDetailPage.vue';
import CourseResourcesPage from '../views/CourseResourcesPage.vue';
import VideoPreviewPage from '../views/VideoPreviewPage.vue';
import HomeworkPage from '../views/HomeworkPage.vue';
import ShowcasePage from '../views/ShowcasePage.vue';
import CommunityPage from '../views/CommunityPage.vue';
import AnnouncementListPage from '../views/AnnouncementListPage.vue';
import AnnouncementDetailPage from '../views/AnnouncementDetailPage.vue';
import ShowcaseDetailPage from '../views/ShowcaseDetailPage.vue';
// 登录和注册现在使用弹窗模式，不需要独立页面路由

const routes = [
  {
    path: '/login',
    redirect: '/', // 重定向到首页，因为我们使用的是弹窗登录
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home,
      },
      {
        path: 'resources',
        name: 'CourseResources',
        component: CourseResourcesPage,
        meta: { requiresAuth: true },
      },
      {
        path: 'homework',
        name: 'Homework',
        component: HomeworkPage,
        meta: { requiresAuth: true },
      },
      {
        path: 'showcase',
        name: 'Showcase',
        component: ShowcasePage,
      },
      {
        path: 'community',
        name: 'Community',
        component: CommunityPage,
      },
      {
        path: 'resource/:id',
        name: 'ResourceDetail',
        component: ResourceDetailPage,
        meta: { requiresAuth: true },
      },
      {
        path: 'resource/:id/preview',
        name: 'VideoPreview',
        component: VideoPreviewPage,
        meta: { requiresAuth: true },
      },
      {
        path: 'homework/:id',
        name: 'HomeworkDetail',
        component: () => import('../views/HomeworkDetailPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'announcements',
        name: 'AnnouncementList',
        component: AnnouncementListPage,
      },
      {
        path: 'announcements/:uuid',
        name: 'AnnouncementDetail',
        component: AnnouncementDetailPage,
      },
      {
        path: 'showcase/:uuid',
        name: 'ShowcaseDetail',
        component: ShowcaseDetailPage,
      },
      {
        path: 'notifications',
        name: 'NotificationList',
        component: () => import('../views/NotificationListPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'community/forum',
        name: 'ForumCenter',
        component: () => import('../views/ForumCenterPage.vue'),
      },
      {
        path: 'community/forum/post/:uuid',
        name: 'ForumPostDetail',
        component: () => import('../views/ForumPostDetailPage.vue'),
      },
      {
        path: 'blogs',
        name: 'BlogList',
        component: () => import('../views/BlogListPage.vue'),
      },
      {
        path: 'blog/:uuid',
        name: 'BlogDetail',
        component: () => import('../views/BlogDetailPage.vue'),
      },
    ],
  },
  // Add other routes here later
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 如果有锚点，滚动到锚点位置
    if (to.hash) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            el: to.hash,
            behavior: 'smooth',
            top: 20
          });
        }, 300);
      });
    }
    // 如果有保存的位置，返回到保存的位置
    if (savedPosition) {
      return savedPosition;
    }
    // 默认滚动到顶部
    return { top: 0 };
  },
});

// 路由守卫：保护需要身份验证的页面
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  // 检查路由是否需要身份验证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      // 未登录，触发登录弹窗并保存目标路径
      console.log('Course resources require authentication. Showing login modal.');
      authStore.showLoginModal(to.fullPath);
      next(false); // 阻止导航
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
