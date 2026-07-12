<template>
  <div class="settings-container">
    <div class="page-header">
      <div>
        <h1>Settings &amp; Role Matrix</h1>
        <p class="subtitle">Configure organization settings and review Role-Based Access Control matrix</p>
      </div>
      <button @click="saveSettings" class="btn-primary">Save Settings</button>
    </div>

    <div class="settings-grid">
      <!-- General Org Settings Card -->
      <div class="card">
        <h3>Organization Configurations</h3>
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
        <p class="matrix-desc">Permissions are enforced server-side via the Flask application and mirrored in the Vue router guards.</p>
        
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
                <td class="font-bold">{{ row.role }}</td>
                <td :class="getPermClass(row.fleet)">{{ row.fleet }}</td>
                <td :class="getPermClass(row.drivers)">{{ row.drivers }}</td>
                <td :class="getPermClass(row.trips)">{{ row.trips }}</td>
                <td :class="getPermClass(row.expenses)">{{ row.expenses }}</td>
                <td :class="getPermClass(row.analytics)">{{ row.analytics }}</td>
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
  { role: 'Financial Analyst', fleet: 'Read-Only', drivers: 'No Access', trips: 'No Access', expenses: 'Full Access', analytics: 'Full Access' }
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
  margin: 0;
  font-size: 1.75rem;
  color: var(--text-h);
}

.subtitle {
  margin: 0.25rem 0 0 0;
  color: var(--text);
  font-size: 0.9rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 1.5rem;
}

.card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1.25rem;
  box-shadow: var(--shadow);
}

.card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-h);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-h);
}

.form-group input,
.form-group select {
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  background-color: var(--bg);
  color: var(--text-h);
  outline: none;
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--accent);
}

.rbac-card {
  display: flex;
  flex-direction: column;
}

.matrix-desc {
  font-size: 0.85rem;
  color: var(--text);
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.matrix-wrapper {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.85rem;
}

.matrix-table th,
.matrix-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.matrix-table th {
  color: var(--text);
  font-weight: 600;
}

.matrix-table td {
  color: var(--text-h);
}

.font-bold { font-weight: 600; }

.full-access {
  color: #10b981;
  font-weight: 600;
}

.read-only {
  color: #3b82f6;
  font-weight: 500;
}

.no-access {
  color: #ef4444;
  opacity: 0.8;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background-color: var(--accent);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 1024px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
