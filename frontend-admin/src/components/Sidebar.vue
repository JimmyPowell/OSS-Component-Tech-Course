<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue';
import { useRoute } from 'vue-router';
import {
  UserOutlined,
  BookOutlined,
  VideoCameraOutlined,
  FormOutlined,
  ProjectOutlined,
  CommentOutlined,
  NotificationOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue';

const props = defineProps({
  isCollapsed: Boolean,
});

const emit = defineEmits(['toggle']);

const route = useRoute();
const selectedKeys = ref([]);
const openKeys = ref(['sub1']);

watch(
  () => route.path,
  (newPath) => {
    selectedKeys.value = [newPath];
  },
  { immediate: true }
);

const menuItems = ref([
  { key: '/users', title: '用户管理', icon: UserOutlined },
  {
    key: 'sub1',
    title: '课程资源管理',
    icon: BookOutlined,
    children: [
      { key: '/ppts', title: '课件PPT管理', icon: ProjectOutlined },
      { key: '/attachments', title: '课程附件管理', icon: FormOutlined },
      { key: '/videos', title: '课程视频管理', icon: VideoCameraOutlined },
    ]
  },
  { key: '/homework', title: '作业管理', icon: FormOutlined },
  { key: '/showcase', title: '作品管理', icon: ProjectOutlined },
  { key: '/forum', title: '论坛内容管理', icon: CommentOutlined },
  { key: '/announcements', title: '公告管理', icon: NotificationOutlined },
  { key: '/settings', title: '系统设置', icon: SettingOutlined },
]);

const handleOpenChange = (keys) => {
  openKeys.value = keys;
};

const toggle = () => {
  emit('toggle');
};
</script>

<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }">
    <a-menu
      mode="inline"
      :inline-collapsed="isCollapsed"
      v-model:selectedKeys="selectedKeys"
      v-model:openKeys="openKeys"
      @openChange="handleOpenChange"
      class="sidebar-menu"
    >
      <template v-for="item in menuItems" :key="item.key">
        <a-menu-item v-if="!item.children" :key="item.key">
          <router-link :to="item.key">
            <component :is="item.icon" />
            <span>{{ item.title }}</span>
          </router-link>
        </a-menu-item>
        <a-sub-menu v-else :key="item.key">
          <template #title>
            <span>
              <component :is="item.icon" />
              <span>{{ item.title }}</span>
            </span>
          </template>
          <a-menu-item v-for="child in item.children" :key="child.key">
            <router-link :to="child.key">
              <component :is="child.icon" />
              <span>{{ child.title }}</span>
            </router-link>
          </a-menu-item>
        </a-sub-menu>
      </template>
    </a-menu>
    <div class="sidebar-footer">
      <a-button type="text" block @click="toggle">
        <template #icon>
          <component :is="isCollapsed ? MenuUnfoldOutlined : MenuFoldOutlined" />
        </template>
        <span v-if="!isCollapsed">折叠侧边栏</span>
      </a-button>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: 100%;
  height: 100%;
  background-color: transparent;
  color: #333;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: width 0.3s cubic-bezier(0.2, 0, 0, 1);
  will-change: width;
}

.sidebar-footer {
  padding: 10px;
}
.sidebar-footer .ant-btn {
  width: calc(100% - 16px);
  margin: 0 8px;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  border-right: none !important;
  background-color: transparent;
}

:deep(.ant-menu) {
  background-color: transparent !important;
  transition: width 0.3s cubic-bezier(0.2, 0, 0, 1);
}

:deep(.ant-menu-inline) {
  border-right: none;
}

:deep(.ant-menu-item), :deep(.ant-menu-submenu-title) {
  font-size: 14px;
  border-radius: 8px;
  margin: 4px 8px;
  width: calc(100% - 16px) !important;
}

:deep(.ant-menu-item-selected) {
  background-color: #e6f7ff !important;
  color: #1890ff;
}

:deep(.ant-menu-item:hover), :deep(.ant-menu-submenu-title:hover) {
  background-color: #f5f5f5 !important;
}

:deep(.ant-menu-submenu-arrow) {
  color: #999;
}

:deep(.ant-menu-submenu-open .ant-menu-submenu-arrow) {
  color: #1890ff;
}

:deep(.ant-menu-inline .ant-menu-item), :deep(.ant-menu-inline .ant-menu-submenu-title) {
  width: 100%;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
}

:deep(.ant-tooltip-inner) {
  background-color: #ffffff !important;
  color: #1890ff !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}

:deep(.ant-tooltip-arrow::before) {
  background-color: #ffffff !important;
}
</style>
