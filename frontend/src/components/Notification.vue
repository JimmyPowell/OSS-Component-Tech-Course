<template>
  <Teleport to="body">
    <transition name="notification-fade">
      <div v-if="isVisible" class="notification-container" :class="type">
        <div class="notification-content">
          <i class="notification-icon" :class="iconClass"></i>
          <span>{{ message }}</span>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  message: String,
  type: {
    type: String,
    default: 'success' // success, error
  },
  duration: {
    type: Number,
    default: 3000
  }
})

const isVisible = ref(false)

const iconClass = computed(() => {
  return {
    'success': 'iconfont icon-check-circle',
    'error': 'iconfont icon-close-circle'
  }[props.type]
})

const show = () => {
  isVisible.value = true
  setTimeout(() => {
    isVisible.value = false
  }, props.duration)
}

// Expose the show method to be called from parent
defineExpose({ show })
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 12px;
  color: white;
  display: flex;
  align-items: center;
  z-index: 9999;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.notification-container.success {
  background-color: #48bb78;
}

.notification-container.error {
  background-color: #f56565;
}

.notification-content {
  display: flex;
  align-items: center;
}

.notification-icon {
  font-size: 24px;
  margin-right: 15px;
}

.notification-fade-enter-active,
.notification-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

.notification-fade-enter-from,
.notification-fade-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
