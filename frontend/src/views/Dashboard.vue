<template>
  <div>
    <!-- Render safety-officer custom dashboard layout -->
    <SafetyOfficerDashboard v-if="userRole === 'Safety Officer'" />

    <!-- Render driver-focused operation stepper dashboard layout -->
    <DriverDashboard v-else-if="userRole === 'Driver'" />

    <!-- Render standard overview fleet dashboard for other roles -->
    <ManagerDashboard v-else />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SafetyOfficerDashboard from '../components/dashboard/SafetyOfficerDashboard.vue';
import DriverDashboard from '../components/dashboard/DriverDashboard.vue';
import ManagerDashboard from '../components/dashboard/ManagerDashboard.vue';

const userRole = ref('Fleet Manager');

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('transitops_user') || '{}');
  if (user.role) userRole.value = user.role;
});
</script>

<style scoped>
/* Page layout spacing is handled by subcomponents */
</style>
