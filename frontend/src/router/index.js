import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../layout/MainLayout.vue';
import Home from '../views/Home.vue';
import ResourceDetailPage from '../views/ResourceDetailPage.vue';
import CourseResourcesPage from '../views/CourseResourcesPage.vue';
import HomeworkPage from '../views/HomeworkPage.vue';
import ShowcasePage from '../views/ShowcasePage.vue';
import CommunityPage from '../views/CommunityPage.vue';
import AdminPanelPage from '../views/AdminPanelPage.vue';
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
      },
      {
        path: 'homework',
        name: 'Homework',
        component: HomeworkPage,
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
      },
      {
        path: 'admin',
        name: 'AdminPanel',
        component: AdminPanelPage,
      },
    ],
  },
  // Add other routes here later
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // always scroll to top
    return { top: 0 };
  },
});

export default router;
