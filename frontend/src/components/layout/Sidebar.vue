<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span class="brand-icon">🔮</span>
      <h2>TransitOps</h2>
    </div>
    
    <div class="sidebar-user">
      <span class="user-role-badge">{{ userRole }}</span>
      <span class="user-email" :title="userEmail">{{ userEmail }}</span>
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
  { path: '/dashboard', label: 'Dashboard', icon: '📊', roles: ['Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst', 'Driver'] },
  { path: '/vehicles', label: 'Fleet Registry', icon: '🚚', roles: ['Fleet Manager', 'Dispatcher', 'Financial Analyst'] },
  { path: '/drivers', label: 'Drivers & Safety', icon: '👤', roles: ['Fleet Manager', 'Safety Officer'] },
  { path: '/trips', label: 'Trip Dispatcher', icon: '🗺️', roles: ['Dispatcher', 'Safety Officer', 'Driver'] },
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
  width: var(--sidebar-width);
  background-color: var(--panel-bg);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  border-right: 1px solid var(--border-color);
  z-index: 100;
}

.sidebar-brand {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.brand-icon {
  font-size: 1.4rem;
}

.sidebar-brand h2 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, var(--primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-user {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  border-bottom: 1px solid var(--border-color);
  background-color: rgba(255, 255, 255, 0.01);
}

.user-role-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  background-color: var(--primary-glow);
  color: var(--primary);
  border: 1px solid rgba(170, 59, 255, 0.25);
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius-sm);
  align-self: flex-start;
}

.user-email {
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  padding: 1.25rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.02);
}

.nav-link.active {
  color: white;
  background: linear-gradient(135deg, var(--primary) 0%, hsl(var(--primary-h), var(--primary-s), 55%) 100%);
  box-shadow: var(--shadow-primary);
}

.nav-icon {
  font-size: 1.15rem;
}
</style>
