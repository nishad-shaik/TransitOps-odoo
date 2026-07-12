<template>
  <nav class="bottom-nav">
    <router-link
      v-for="link in allLinks"
      :key="link.path"
      :to="link.path"
      class="nav-item"
      active-class="active"
    >
      <span class="nav-icon">{{ link.icon }}</span>
      <span class="nav-label">{{ link.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
const allLinks = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/trips', label: 'Trips', icon: '🗺️' },
  { path: '/maintenance', label: 'Maintenance', icon: '🔧' },
  { path: '/fuel-expenses', label: 'Fuel & Exp', icon: '💳' }
];
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px; /* Over 48px height target optimized for touch */
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
  min-height: 48px; /* Thumb-friendly tap zones (minimum 48px height) */
  transition: all 0.2s ease;
  flex: 1;
}

.nav-icon {
  font-size: 1.25rem;
  margin-bottom: 0.15rem;
}

.nav-item:hover {
  color: var(--text-primary);
}

.nav-item.active {
  color: var(--primary);
  background-color: rgba(170, 59, 255, 0.03);
}
</style>
