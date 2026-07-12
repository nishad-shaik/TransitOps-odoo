<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <h2>TransitOps</h2>
    </div>
    
    <div class="sidebar-user">
      <span class="user-role-badge">{{ userRole }}</span>
      <span class="user-email">{{ userEmail }}</span>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="link in allowedLinks"
        :key="link.path"
        :to="link.path"
        class="nav-link"
        active-class="active"
      >
        <span class="nav-icon">{{ link.icon }}</span>
        <span class="nav-text">{{ link.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const userRole = ref('Fleet Manager');
const userEmail = ref('manager@transitops.dev');

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('transitops_user') || '{}');
  if (user.role) userRole.value = user.role;
  if (user.email) userEmail.value = user.email;
});

const allLinks = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊', roles: ['Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst'] },
  { path: '/vehicles', label: 'Fleet Registry', icon: '🚚', roles: ['Fleet Manager', 'Dispatcher', 'Financial Analyst'] },
  { path: '/drivers', label: 'Drivers & Safety', icon: '👤', roles: ['Fleet Manager', 'Safety Officer'] },
  { path: '/trips', label: 'Trip Dispatcher', icon: '🗺️', roles: ['Dispatcher', 'Safety Officer'] },
  { path: '/maintenance', label: 'Maintenance Log', icon: '🔧', roles: ['Fleet Manager'] },
  { path: '/fuel-expenses', label: 'Fuel & Expenses', icon: '💳', roles: ['Financial Analyst'] },
  { path: '/analytics', label: 'Reports & ROI', icon: '📈', roles: ['Fleet Manager', 'Financial Analyst'] },
  { path: '/settings', label: 'Settings', icon: '⚙️', roles: ['Fleet Manager'] }
];

const allowedLinks = computed(() => {
  return allLinks.filter(link => link.roles.includes(userRole.value));
});
</script>

<style scoped>
.sidebar {
  width: 260px;
  background-color: var(--text-h);
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  border-right: 1px solid var(--border);
  z-index: 100;
}

.sidebar-brand {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-brand h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--accent);
}

.sidebar-user {
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(255, 255, 255, 0.02);
}

.user-role-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  background-color: var(--accent);
  color: white;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  align-self: flex-start;
}

.user-email {
  font-size: 0.8rem;
  opacity: 0.7;
}

.sidebar-nav {
  padding: 1.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s;
}

.nav-link:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-link.active {
  color: white;
  background-color: var(--accent);
}

.nav-icon {
  font-size: 1.1rem;
}
</style>
