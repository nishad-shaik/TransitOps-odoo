<template>
  <div class="app-layout" :class="{ 'auth-view': isAuthView, 'mobile-nav-active': isMobileLayout }">
    <!-- Render desktop sidebar only if not on Login page and not on Mobile Layout roles/widths -->
    <Sidebar v-if="!isAuthView && !isMobileLayout" />
    
    <div class="main-wrapper">
      <!-- Render topbar only if not on Login page -->
      <Topbar v-if="!isAuthView" />
      
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- Render bottom touch navigation for mobile widths or Dispatchers/Drivers -->
    <BottomNav v-if="!isAuthView && isMobileLayout" />
    
    <!-- Global Toasts -->
    <ToastNotification />
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './components/layout/Sidebar.vue';
import Topbar from './components/layout/Topbar.vue';
import BottomNav from './components/layout/BottomNav.vue';
import ToastNotification from './components/ui/ToastNotification.vue';

const route = useRoute();
const userRole = ref('');
const isMobileWidth = ref(false);

const handleResize = () => {
  isMobileWidth.value = window.innerWidth < 768;
};

// Dynamically check user role and size on navigation to adapt the layout
watch(() => route.path, () => {
  const user = JSON.parse(localStorage.getItem('transitops_user') || '{}');
  userRole.value = user.role || '';
}, { immediate: true });

onMounted(() => {
  handleResize();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

// Check if current route is the login view
const isAuthView = computed(() => {
  return route.name === 'Login';
});

// Check if the current user should get the mobile touch-optimized bottom navigation (width < 768px or specific roles)
const isMobileLayout = computed(() => {
  return isMobileWidth.value || ['Dispatcher', 'Driver'].includes(userRole.value);
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

/* Bottom Navigation Layout overrides */
.mobile-nav-active .main-wrapper {
  margin-left: 0;
}

.mobile-nav-active .main-content {
  padding-bottom: 80px; /* Offset to clear the bottom touch menu */
}
</style>
