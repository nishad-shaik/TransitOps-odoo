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
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './components/layout/Sidebar.vue';
import Topbar from './components/layout/Topbar.vue';

const route = useRoute();

// Check if current route is the login view
const isAuthView = computed(() => {
  return route.name === 'Login';
});
</script>

<style>
/* Global CSS variables or resets if needed */
:root {
  --text: #6b6375;
  --text-h: #08060d;
  --bg: #ffffff;
  --border: #e5e4e7;
  --code-bg: #f4f3ec;
  --accent: #aa3bff;
  --accent-bg: rgba(170, 59, 255, 0.1);
  --accent-border: rgba(170, 59, 255, 0.5);
  --social-bg: rgba(244, 243, 236, 0.5);
  --shadow: rgba(0, 0, 0, 0.05) 0 4px 6px -2px, rgba(0, 0, 0, 0.1) 0 10px 15px -3px;
  --sans: system-ui, 'Segoe UI', Roboto, sans-serif;
  --mono: ui-monospace, Consolas, monospace;
}

body {
  margin: 0;
  padding: 0;
  font-family: var(--sans);
  background-color: var(--bg);
  color: var(--text-h);
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  margin-left: 260px; /* Width of Sidebar */
}

.main-content {
  padding: 2rem;
  margin-top: 60px; /* Height of Topbar */
  flex: 1;
  background-color: #faf9fb;
  min-height: calc(100vh - 60px);
}

/* Auth view overrides layout margins */
.auth-view .main-wrapper {
  margin-left: 0;
}

.auth-view .main-content {
  margin-top: 0;
  padding: 0;
  background-color: var(--bg);
}
</style>
