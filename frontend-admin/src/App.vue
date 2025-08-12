<script setup>
import AdminLayout from './components/AdminLayout.vue';
</script>

<template>
  <AdminLayout>
    <router-view />
  </AdminLayout>
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
