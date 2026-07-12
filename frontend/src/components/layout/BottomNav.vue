<template>
  <nav class="bottom-nav">
    <router-link
      v-for="link in allLinks"
      :key="link.path"
      :to="link.path"
      class="nav-item"
      active-class="active"
    >
      <component :is="link.icon" class="nav-icon-svg" />
      <span class="nav-label">{{ link.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { LayoutDashboard, Compass, Wrench, CreditCard } from '@lucide/vue';

const allLinks = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/trips', label: 'Trips', icon: Compass },
  { path: '/maintenance', label: 'Maintenance', icon: Wrench },
  { path: '/fuel-expenses', label: 'Fuel & Exp', icon: CreditCard }
];
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 65px;
  background-color: var(--panel-bg);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.2);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.5rem 1rem;
  min-height: 48px;
  transition: all 0.2s ease;
  flex: 1;
}

.nav-icon-svg {
  width: 20px;
  height: 20px;
  margin-bottom: 0.25rem;
}

.nav-item:hover {
  color: var(--text-primary);
}

.nav-item.active {
  color: var(--primary);
  background-color: rgba(245, 166, 35, 0.03);
}
</style>
