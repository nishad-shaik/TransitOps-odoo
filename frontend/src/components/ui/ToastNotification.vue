<template>
  <Transition name="toast-fade">
    <div v-if="toastVisible" class="toast-wrapper" :class="toastType">
      <component :is="icon" class="toast-icon-svg" />
      <span class="toast-msg">{{ toastMessage }}</span>
      <button @click="toastVisible = false" class="toast-close">&times;</button>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue';
import { CheckCircle2, XCircle, AlertTriangle, Info } from '@lucide/vue';
import { useToast } from '../../composables/useToast';

const { toastMessage, toastType, toastVisible } = useToast();

const icon = computed(() => {
  if (toastType.value === 'success') return CheckCircle2;
  if (toastType.value === 'error') return XCircle;
  if (toastType.value === 'warning') return AlertTriangle;
  return Info;
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

.toast-icon-svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Colors matching semantic variables */
.toast-wrapper.success {
  background-color: var(--panel-bg);
  border-color: rgba(76, 154, 106, 0.4);
  box-shadow: 0 4px 20px rgba(76, 154, 106, 0.15);
}
.toast-wrapper.success .toast-icon-svg { color: var(--success); }

.toast-wrapper.error {
  background-color: var(--panel-bg);
  border-color: rgba(209, 67, 67, 0.4);
  box-shadow: 0 4px 20px rgba(209, 67, 67, 0.15);
}
.toast-wrapper.error .toast-icon-svg { color: var(--danger); }

.toast-wrapper.warning {
  background-color: var(--panel-bg);
  border-color: rgba(245, 166, 35, 0.4);
  box-shadow: 0 4px 20px rgba(245, 166, 35, 0.15);
}
.toast-wrapper.warning .toast-icon-svg { color: var(--warning); }

.toast-wrapper.info {
  background-color: var(--panel-bg);
  border-color: rgba(59, 130, 196, 0.4);
  box-shadow: 0 4px 20px rgba(59, 130, 196, 0.15);
}
.toast-wrapper.info .toast-icon-svg { color: var(--info); }

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
