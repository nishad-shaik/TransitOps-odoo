<template>
  <Transition name="toast-fade">
    <div v-if="toastVisible" class="toast-wrapper" :class="toastType">
      <span class="toast-icon">{{ icon }}</span>
      <span class="toast-msg">{{ toastMessage }}</span>
      <button @click="toastVisible = false" class="toast-close">&times;</button>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue';
import { useToast } from '../../composables/useToast';

const { toastMessage, toastType, toastVisible } = useToast();

const icon = computed(() => {
  if (toastType.value === 'success') return '✅';
  if (toastType.value === 'error') return '❌';
  if (toastType.value === 'warning') return '⚠️';
  return 'ℹ️';
});
</script>

<style scoped>
.toast-wrapper {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  min-width: 300px;
  max-width: 450px;
}

/* Colors matching semantic variables */
.toast-wrapper.success {
  background-color: #111827;
  border-color: rgba(16, 185, 129, 0.4);
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
}
.toast-wrapper.success .toast-icon { color: var(--success); }

.toast-wrapper.error {
  background-color: #111827;
  border-color: rgba(239, 68, 68, 0.4);
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.15);
}
.toast-wrapper.error .toast-icon { color: var(--danger); }

.toast-wrapper.warning {
  background-color: #111827;
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);
}
.toast-wrapper.warning .toast-icon { color: var(--warning); }

.toast-wrapper.info {
  background-color: #111827;
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
}
.toast-wrapper.info .toast-icon { color: var(--info); }

.toast-msg {
  flex: 1;
}

.toast-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 0.25rem;
}

.toast-close:hover {
  color: #fff;
}

/* Transitions */
.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-fade-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}
</style>
