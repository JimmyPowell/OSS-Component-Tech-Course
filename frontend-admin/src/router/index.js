import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/Login.vue';
import Welcome from '../components/Welcome.vue';
import UserManagement from '../components/UserManagement.vue';
import PptManagement from '../components/PptManagement.vue';
import AttachmentManagement from '../components/AttachmentManagement.vue';
import VideoManagement from '../components/VideoManagement.vue';
import HomeworkManagement from '../components/HomeworkManagement.vue';
import ShowcaseManagement from '../components/ShowcaseManagement.vue';
import ShowcaseReview from '../components/ShowcaseReview.vue';
import ForumManagement from '../components/ForumManagement.vue';
import AnnouncementManagement from '../components/AnnouncementManagement.vue';
import SystemSettings from '../components/SystemSettings.vue';
import VideoPreview from '../components/VideoPreview.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login, meta: { requiresAuth: false } },
  { path: '/welcome', component: Welcome, meta: { requiresAuth: true } },
  { path: '/users', component: UserManagement, meta: { requiresAuth: true } },
  { path: '/ppts', component: PptManagement, meta: { requiresAuth: true } },
  { path: '/attachments', component: AttachmentManagement, meta: { requiresAuth: true } },
  { path: '/videos', component: VideoManagement, meta: { requiresAuth: true } },
  { path: '/homework', component: HomeworkManagement, meta: { requiresAuth: true } },
  { path: '/showcase', component: ShowcaseManagement, meta: { requiresAuth: true } },
  { path: '/showcase-review', component: ShowcaseReview, meta: { requiresAuth: true } },
  { path: '/forum', component: ForumManagement, meta: { requiresAuth: true } },
  { path: '/announcements', component: AnnouncementManagement, meta: { requiresAuth: true } },
  { path: '/settings', component: SystemSettings, meta: { requiresAuth: true } },
  { path: '/video-preview/:uuid', component: VideoPreview, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('access_token') !== null;
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
  } else if (to.path === '/login' && isLoggedIn) {
    next('/welcome');
  } else if (to.path === '/' && isLoggedIn) {
    next('/welcome');
  } else {
    next();
  }
});

export default router;
