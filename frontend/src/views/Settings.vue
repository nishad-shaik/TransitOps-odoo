<template>
  <div class="settings-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Settings &amp; Role Matrix</h1>
        <p class="subtitle">Configure organization settings and review Role-Based Access Control matrix</p>
      </div>
      <button @click="saveSettings" class="btn-primary">Save Settings</button>
    </div>

    <!-- Layout Grid -->
    <div class="settings-grid">
      <!-- General Org Settings Card -->
      <div class="card">
        <h3>Organization Configurations</h3>
        <p class="card-subtitle">Manage default currencies, depots, and localization units</p>
        
        <form @submit.prevent="saveSettings" class="settings-form">
          <div class="form-group">
            <label>Depot Name</label>
            <input type="text" v-model="orgSettings.depotName" required />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Currency</label>
              <select v-model="orgSettings.currency">
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="INR">INR (₹)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Distance Unit</label>
              <select v-model="orgSettings.distanceUnit">
                <option value="km">Kilometers (km)</option>
                <option value="miles">Miles (mi)</option>
              </select>
            </div>
          </div>
        </form>
      </div>

      <!-- RBAC Info Card -->
      <div class="card rbac-card">
        <h3>Role Permission Matrix</h3>
        <p class="card-subtitle">Permissions are enforced server-side via the Flask application and mirrored in the Vue router guards.</p>
        
        <div class="matrix-wrapper">
          <table class="matrix-table">
            <thead>
              <tr>
                <th>Role</th>
                <th>Fleet</th>
                <th>Drivers</th>
                <th>Trips</th>
                <th>Fuel/Exp</th>
                <th>Analytics</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rbacMatrix" :key="row.role">
                <td class="font-bold highlight-text">{{ row.role }}</td>
                <td>
                  <span class="matrix-badge" :class="getPermClass(row.fleet)">{{ row.fleet }}</span>
                </td>
                <td>
                  <span class="matrix-badge" :class="getPermClass(row.drivers)">{{ row.drivers }}</span>
                </td>
                <td>
                  <span class="matrix-badge" :class="getPermClass(row.trips)">{{ row.trips }}</span>
                </td>
                <td>
                  <span class="matrix-badge" :class="getPermClass(row.expenses)">{{ row.expenses }}</span>
                </td>
                <td>
                  <span class="matrix-badge" :class="getPermClass(row.analytics)">{{ row.analytics }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';

const orgSettings = reactive({
  depotName: 'TransitOps Central Depot',
  currency: 'USD',
  distanceUnit: 'km'
});

const rbacMatrix = ref([
  { role: 'Fleet Manager', fleet: 'Full Access', drivers: 'Full Access', trips: 'No Access', expenses: 'No Access', analytics: 'Read-Only' },
  { role: 'Dispatcher', fleet: 'Read-Only', drivers: 'No Access', trips: 'Full Access', expenses: 'No Access', analytics: 'No Access' },
  { role: 'Safety Officer', fleet: 'No Access', drivers: 'Full Access', trips: 'Read-Only', expenses: 'No Access', analytics: 'No Access' },
  { role: 'Financial Analyst', fleet: 'Read-Only', drivers: 'No Access', trips: 'No Access', expenses: 'Full Access', analytics: 'Full Access' },
  { role: 'Driver', fleet: 'No Access', drivers: 'No Access', trips: 'Read-Only', expenses: 'No Access', analytics: 'No Access' }
]);

const getPermClass = (perm) => {
  if (perm === 'Full Access') return 'full-access';
  if (perm === 'Read-Only') return 'read-only';
  return 'no-access';
};

const saveSettings = () => {
  alert('Organization configurations saved successfully!');
};
</script>

<style scoped>
.settings-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  font-size: 2.25rem;
  margin: 0;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-top: 0.25rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 1.75rem;
}

.card h3 {
  margin: 0;
}

.card-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
  margin-bottom: 1.5rem;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.matrix-wrapper {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.matrix-table th,
.matrix-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.85rem;
}

.matrix-table th {
  color: var(--text-secondary);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background-color: rgba(255, 255, 255, 0.015);
}

.matrix-table td {
  color: var(--text-primary);
}

.font-bold { font-weight: 700; }
.highlight-text { color: #fff; }

.matrix-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
}

.matrix-badge.full-access {
  background-color: var(--success-glow);
  color: var(--success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.matrix-badge.read-only {
  background-color: var(--info-glow);
  color: var(--info);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.matrix-badge.no-access {
  background-color: var(--danger-glow);
  color: var(--danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
  opacity: 0.75;
}

@media (max-width: 1100px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
