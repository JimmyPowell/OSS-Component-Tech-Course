<template>
  <div>
    <Navbar />
    <main>
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue';
import Footer from '../components/Footer.vue';
</script>

<style scoped>
/* Scoped styles for the layout can go here */
main {
  /* We might need some styles here later, e.g., to prevent content from hiding behind the fixed navbar */
}
</style>
