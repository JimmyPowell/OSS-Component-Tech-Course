<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AdminLayout from './components/AdminLayout.vue';

const route = useRoute();

const showLayout = computed(() => {
  return route.path !== '/login' && !route.path.startsWith('/video-preview');
});
</script>

<template>
  <div>
    <AdminLayout v-if="showLayout">
      <router-view />
    </AdminLayout>
    <router-view v-else />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
  background-color: #f5f5f5;
}
</style>
