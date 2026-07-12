<template>
  <header class="topbar">
    <div class="page-title">
      {{ currentRouteName }}
    </div>
    
    <div class="topbar-actions">
      <div class="user-info">
        <span class="user-name">Active User</span>
      </div>
      <button @click="handleLogout" class="btn-logout">Logout</button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const currentRouteName = computed(() => {
  return route.name || 'TransitOps';
});

const handleLogout = () => {
  localStorage.removeItem('transitops_token');
  localStorage.removeItem('transitops_user');
  router.push('/login');
};
</script>

<style scoped>
.topbar {
  height: 60px;
  background-color: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  position: fixed;
  top: 0;
  right: 0;
  left: 260px;
  z-index: 90;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-h);
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
  font-weight: 600;
  color: var(--text-h);
}

.btn-logout {
  background-color: transparent;
  border: 1px solid var(--border);
  color: var(--text-h);
  padding: 0.35rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background-color: var(--social-bg);
  border-color: var(--text);
}
</style>
