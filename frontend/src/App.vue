<template>
  <div class="app-layout" :class="{ 'auth-view': isAuthView }">
    <!-- Render sidebar only if not on Login page -->
    <Sidebar v-if="!isAuthView" />
    
    <div class="main-wrapper">
      <!-- Render topbar only if not on Login page -->
      <Topbar v-if="!isAuthView" />
      
      <main class="main-content">
        <router-view />
      </main>
    </div>
    
    <!-- Global Toasts -->
    <ToastNotification />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './components/layout/Sidebar.vue';
import Topbar from './components/layout/Topbar.vue';
import ToastNotification from './components/ui/ToastNotification.vue';

const route = useRoute();

// Check if current route is the login view
const isAuthView = computed(() => {
  return route.name === 'Login';
});
</script>


<style>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  margin-left: var(--sidebar-width);
  transition: margin-left 0.3s ease;
}

.main-content {
  padding: 2.5rem;
  margin-top: var(--topbar-height);
  flex: 1;
  background-color: var(--dark-bg);
  min-height: calc(100vh - var(--topbar-height));
}

/* Auth view overrides layout margins */
.auth-view .main-wrapper {
  margin-left: 0;
}

.auth-view .main-content {
  margin-top: 0;
  padding: 0;
  background-color: var(--dark-bg);
}
</style>
