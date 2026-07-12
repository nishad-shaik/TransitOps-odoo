<template>
  <header class="topbar">
    <div class="page-title">
      {{ currentRouteName }}
    </div>
    
    <div class="topbar-actions">
      <div class="user-info">
        <span class="user-name">{{ userEmail }}</span>
        <span class="user-role">{{ userRole }}</span>
      </div>
      <button @click="handleLogout" class="btn-logout">Logout</button>
    </div>
  </header>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from '../../composables/useToast';

const route = useRoute();
const router = useRouter();
const { showToast } = useToast();

const userEmail = ref('Active User');
const userRole = ref('Guest');

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('transitops_user') || '{}');
  if (user.email) userEmail.value = user.email;
  if (user.role) userRole.value = user.role;
});

const currentRouteName = computed(() => {
  return route.name || 'TransitOps';
});

// Shared-Device Safe Logout sequence clearing all session indicators
const handleLogout = () => {
  // Clear reactive caches and persistent credentials
  localStorage.clear();
  sessionStorage.clear();
  
  showToast('Logged out securely. Session data terminated.', 'success');
  router.push('/login');
};
</script>

<style scoped>
.topbar {
  height: var(--topbar-height);
  background-color: var(--panel-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2.5rem;
  position: fixed;
  top: 0;
  right: 0;
  left: var(--sidebar-width);
  z-index: 90;
  transition: left 0.3s ease;
  box-shadow: var(--shadow-sm);
}

/* Adapt spacing when sidebar is collapsed in mobile viewports */
:global(.mobile-nav-active) .topbar {
  left: 0;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
  font-family: 'Outfit', sans-serif;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #fff;
}

.user-role {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--primary);
  margin-top: 0.1rem;
}

.btn-logout {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.45rem 1rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background-color: var(--danger-glow);
  border-color: var(--danger);
  color: var(--danger);
}
</style>
