<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <Truck class="brand-icon-svg" />
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
        <component :is="link.icon" class="nav-icon-svg" />
        <span class="nav-text">{{ link.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  LayoutDashboard, 
  Truck, 
  Users, 
  Compass, 
  Wrench, 
  CreditCard, 
  BarChart3, 
  Settings 
} from '@lucide/vue';

const userRole = ref('Fleet Manager');
const userEmail = ref('manager@transitops.dev');

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('transitops_user') || '{}');
  if (user.role) userRole.value = user.role;
  if (user.email) userEmail.value = user.email;
});

const allLinks = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['Fleet Manager', 'Dispatcher', 'Safety Officer', 'Financial Analyst', 'Driver', 'Developer'] },
  { path: '/vehicles', label: 'Fleet Registry', icon: Truck, roles: ['Fleet Manager', 'Dispatcher', 'Financial Analyst', 'Developer'] },
  { path: '/drivers', label: 'Drivers & Safety', icon: Users, roles: ['Fleet Manager', 'Safety Officer', 'Developer'] },
  { path: '/trips', label: 'Trip Dispatcher', icon: Compass, roles: ['Dispatcher', 'Safety Officer', 'Driver', 'Developer'] },
  { path: '/maintenance', label: 'Maintenance Log', icon: Wrench, roles: ['Fleet Manager', 'Developer'] },
  { path: '/fuel-expenses', label: 'Fuel & Expenses', icon: CreditCard, roles: ['Financial Analyst', 'Developer'] },
  { path: '/analytics', label: 'Reports & ROI', icon: BarChart3, roles: ['Fleet Manager', 'Financial Analyst', 'Developer'] },
  { path: '/settings', label: 'Settings', icon: Settings, roles: ['Fleet Manager', 'Developer'] }
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
  gap: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.brand-icon-svg {
  width: 24px;
  height: 24px;
  color: var(--primary);
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
  border: 1px solid rgba(245, 166, 35, 0.25);
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
  color: #15181D;
  background: var(--primary);
  box-shadow: var(--shadow-primary);
}

.nav-icon-svg {
  width: 18px;
  height: 18px;
}
</style>
