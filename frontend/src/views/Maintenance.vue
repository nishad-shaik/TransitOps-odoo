<template>
  <div class="maintenance-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Maintenance Log</h1>
        <p class="subtitle">Record service logs and manage vehicle workshop schedules</p>
      </div>
      <button @click="showLogForm = !showLogForm" class="btn-primary">
        {{ showLogForm ? 'Hide Form' : '+ Log Service Record' }}
      </button>
    </div>

    <!-- Rule Banner -->
    <div class="info-banner">
      <span class="info-icon">🔧</span>
      <p><strong>Status Transition Rule:</strong> Registering an active maintenance record automatically flips the vehicle to <strong>In Shop</strong> (removed from the dispatch pool). Closing the record returns the vehicle to <strong>Available</strong>.</p>
    </div>

    <!-- Maintenance Log Form -->
    <div v-if="showLogForm" class="card form-card">
      <h3>Log Service Record</h3>
      <form @submit.prevent="saveMaintenanceLog">
        <div class="form-row">
          <div class="form-group">
            <label>Select Vehicle</label>
            <select v-model="newLog.vehicle" required>
              <option value="">-- Choose Vehicle --</option>
              <option v-for="v in vehicles" :key="v.regNo" :value="v.regNo">
                {{ v.regNo }} - {{ v.model }} (Status: {{ v.status }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Service Type</label>
            <input type="text" v-model="newLog.serviceType" placeholder="e.g. Engine Oil Change, Brake Replacement" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Cost ($)</label>
            <input type="number" v-model.number="newLog.cost" required />
          </div>
          <div class="form-group">
            <label>Service Date</label>
            <input type="date" v-model="newLog.date" required />
          </div>
        </div>

        <div class="form-group">
          <label>Status</label>
          <select v-model="newLog.status">
            <option value="Active">Active (Vehicle goes In Shop)</option>
            <option value="Closed">Closed (Vehicle returns to Available)</option>
          </select>
        </div>

        <div class="form-actions">
          <button type="button" @click="showLogForm = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary">Save Record</button>
        </div>
      </form>
    </div>

    <!-- Service Logs Table -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Log ID</th>
            <th>Vehicle</th>
            <th>Service Type</th>
            <th>Cost ($)</th>
            <th>Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td class="font-mono">#{{ log.id }}</td>
            <td class="font-bold highlight-text">{{ log.vehicle }}</td>
            <td>{{ log.serviceType }}</td>
            <td class="font-bold">${{ log.cost.toLocaleString() }}</td>
            <td>{{ log.date }}</td>
            <td>
              <span class="badge" :class="statusBadgeClass(log.status)">
                {{ log.status }}
              </span>
            </td>
            <td>
              <button
                v-if="log.status === 'Active'"
                @click="closeLog(log)"
                class="btn-text"
              >
                Close Log
              </button>
              <span v-else class="text-completed">Completed</span>
            </td>
          </tr>
          <tr v-if="logs.length === 0">
            <td colspan="7" class="text-center empty-row">No maintenance logs found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const showLogForm = ref(false);

const vehicles = ref([
  { regNo: 'VAN-05', model: 'Ford Transit 350', status: 'Available' },
  { regNo: 'TRK-02', model: 'Volvo FH16 Heavy', status: 'On Trip' },
  { regNo: 'VAN-02', model: 'Mercedes Sprinter Cargo', status: 'In Shop' }
]);

const logs = ref([
  { id: 201, vehicle: 'VAN-02', serviceType: 'Brake Pad Replacement', cost: 450, date: '2026-07-10', status: 'Active' },
  { id: 200, vehicle: 'VAN-05', serviceType: 'Annual General Inspection', cost: 150, date: '2026-06-18', status: 'Closed' }
]);

const newLog = reactive({
  vehicle: '',
  serviceType: '',
  cost: 0,
  date: new Date().toISOString().split('T')[0],
  status: 'Active'
});

const statusBadgeClass = (status) => {
  return status === 'Active' ? 'badge-warning' : 'badge-success';
};

const saveMaintenanceLog = () => {
  const newId = logs.value.length > 0 ? Math.max(...logs.value.map(l => l.id)) + 1 : 201;
  logs.value.unshift({
    id: newId,
    vehicle: newLog.vehicle,
    serviceType: newLog.serviceType,
    cost: newLog.cost,
    date: newLog.date,
    status: newLog.status
  });

  const targetVehicle = vehicles.value.find(v => v.regNo === newLog.vehicle);
  if (targetVehicle && newLog.status === 'Active') {
    targetVehicle.status = 'In Shop';
  }

  showLogForm.value = false;

  newLog.vehicle = '';
  newLog.serviceType = '';
  newLog.cost = 0;
  newLog.status = 'Active';
};

const closeLog = (log) => {
  log.status = 'Closed';
  const targetVehicle = vehicles.value.find(v => v.regNo === log.vehicle);
  if (targetVehicle) {
    targetVehicle.status = 'Available';
  }
};
</script>

<style scoped>
.maintenance-container {
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

.info-banner {
  background-color: var(--primary-glow);
  border: 1px solid rgba(170, 59, 255, 0.15);
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius-md);
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.9rem;
}

.info-icon {
  color: var(--primary);
  font-size: 1.1rem;
}

.form-card {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.font-mono {
  font-family: var(--mono);
}

.font-bold {
  font-weight: 700;
}

.highlight-text {
  color: #fff;
}

.btn-text {
  background: none;
  border: none;
  color: var(--primary);
  cursor: pointer;
  font-weight: 700;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.btn-text:hover {
  color: var(--primary-hover);
}

.text-completed {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.empty-row {
  color: var(--text-secondary);
  padding: 3rem;
  text-align: center;
}
</style>
