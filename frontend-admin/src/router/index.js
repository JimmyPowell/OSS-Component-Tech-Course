import { createRouter, createWebHistory } from 'vue-router';
import UserManagement from '../components/UserManagement.vue';
import PptManagement from '../components/PptManagement.vue';
import AttachmentManagement from '../components/AttachmentManagement.vue';
import VideoManagement from '../components/VideoManagement.vue';
import HomeworkManagement from '../components/HomeworkManagement.vue';
import ShowcaseManagement from '../components/ShowcaseManagement.vue';
import ForumManagement from '../components/ForumManagement.vue';
import AnnouncementManagement from '../components/AnnouncementManagement.vue';

const routes = [
  { path: '/', redirect: '/users' },
  { path: '/users', component: UserManagement },
  { path: '/ppts', component: PptManagement },
  { path: '/attachments', component: AttachmentManagement },
  { path: '/videos', component: VideoManagement },
  { path: '/homework', component: HomeworkManagement },
  { path: '/showcase', component: ShowcaseManagement },
  { path: '/forum', component: ForumManagement },
  { path: '/announcements', component: AnnouncementManagement },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
