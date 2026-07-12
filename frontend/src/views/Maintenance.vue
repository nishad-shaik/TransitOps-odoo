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
      <Wrench class="info-icon-svg" />
      <p><strong>Status Transition Rule:</strong> Registering an active maintenance record automatically flips the vehicle to <strong>In Shop</strong> (removed from the dispatch pool). Closing the record returns the vehicle to <strong>Available</strong>.</p>
    </div>

    <!-- Maintenance Log Form -->
    <div v-if="showLogForm" class="card form-card">
      <h3>Log Service Record</h3>
      <form @submit.prevent="saveMaintenanceLog">
        <div class="form-row">
          <div class="form-group">
            <label>Select Vehicle</label>
            <select v-model="newLog.vehicle_id" required>
              <option value="">-- Choose Vehicle --</option>
              <option v-for="v in vehicles" :key="v.registration_number" :value="v.registration_number">
                {{ v.registration_number }} - {{ v.vehicle_name }} (Status: {{ v.status }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Service Description</label>
            <input type="text" v-model="newLog.description" placeholder="e.g. Engine Oil Change, Brake Replacement" required />
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
            <option value="Open">Open (Vehicle goes In Shop)</option>
            <option value="Closed">Closed (Vehicle returns to Available)</option>
          </select>
        </div>

        <div class="form-actions">
          <button type="button" @click="showLogForm = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Logging...' : 'Save Record' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Service Logs Table (Desktop: md and above) -->
    <div class="table-card hidden md:block">
      <table class="data-table">
        <thead>
          <tr>
            <th>Log ID</th>
            <th>Vehicle</th>
            <th>Service Description</th>
            <th>Cost ($)</th>
            <th>Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td class="font-mono">#{{ log.id }}</td>
            <td class="font-bold highlight-text">{{ log.vehicle_id }}</td>
            <td>{{ log.description }}</td>
            <td class="font-bold">${{ log.cost.toLocaleString() }}</td>
            <td>{{ log.date }}</td>
            <td>
              <span class="badge" :class="statusBadgeClass(log.status)">
                {{ log.status }}
              </span>
            </td>
            <td>
              <button
                v-if="log.status === 'Open'"
                @click="closeLog(log)"
                class="btn-text"
                :disabled="isSubmitting"
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

    <!-- Mobile Viewports (Expandable Accordions: hidden on md and above) -->
    <div class="mobile-accordion-list block md:hidden">
      <div 
        v-for="log in logs" 
        :key="'mobile-log-' + log.id" 
        class="card mobile-accordion-card"
        :class="{ expanded: expandedLogs.includes(log.id) }"
      >
        <!-- Accordion Header: 3 Vital columns only -->
        <div class="accordion-header" @click="toggleLogAccordion(log.id)">
          <div class="vital-col font-mono font-bold text-white">#{{ log.id }} - {{ log.vehicle_id }}</div>
          <div class="vital-col">
            <span class="badge" :class="statusBadgeClass(log.status)">
              {{ log.status }}
            </span>
          </div>
          <div class="vital-col text-right pr-4 font-bold">${{ log.cost.toLocaleString() }}</div>
          <span class="chevron">&#9662;</span>
        </div>

        <!-- Expanded Content -->
        <div class="accordion-content" v-if="expandedLogs.includes(log.id)">
          <div class="meta-row">
            <span class="lbl">Service Details:</span>
            <span class="val">{{ log.description }}</span>
          </div>
          <div class="meta-row">
            <span class="lbl">Log Date:</span>
            <span class="val font-mono">{{ log.date }}</span>
          </div>
          <div class="meta-row action-row">
            <button 
              v-if="log.status === 'Open'" 
              @click="closeLog(log)" 
              class="btn-sm btn-accent"
              :disabled="isSubmitting"
            >
              Close Log
            </button>
            <span v-else class="text-completed">Completed</span>
          </div>
        </div>
      </div>
      <div v-if="logs.length === 0" class="card empty-row">
        No maintenance logs found.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { Wrench } from '@lucide/vue';
import { useToast } from '../composables/useToast';


const { showToast } = useToast();

const showLogForm = ref(false);
const isSubmitting = ref(false);
const expandedLogs = ref([]);

const vehicles = ref([
  { id: 1, registration_number: 'VAN-05', vehicle_name: 'Ford Transit 350', status: 'Available' },
  { id: 2, registration_number: 'TRK-02', vehicle_name: 'Volvo FH16 Heavy', status: 'On Trip' },
  { id: 4, registration_number: 'VAN-02', vehicle_name: 'Mercedes Sprinter Cargo', status: 'In Shop' }
]);

const logs = ref([
  { id: 201, vehicle_id: 'VAN-02', description: 'Brake Pad Replacement', cost: 450, date: '2026-07-10', status: 'Open' },
  { id: 200, vehicle_id: 'VAN-05', description: 'Annual General Inspection', cost: 150, date: '2026-06-18', status: 'Closed' }
]);

const newLog = reactive({
  vehicle_id: '',
  description: '',
  cost: 0,
  date: new Date().toISOString().split('T')[0],
  status: 'Open'
});

const toggleLogAccordion = (id) => {
  if (expandedLogs.value.includes(id)) {
    expandedLogs.value = expandedLogs.value.filter(l => l !== id);
  } else {
    expandedLogs.value.push(id);
  }
};

const statusBadgeClass = (status) => {
  return status === 'Open' ? 'badge-warning' : 'badge-success';
};

const saveMaintenanceLog = async () => {
  if (isSubmitting.value) return;

  const selectReg = String(newLog.vehicle_id);
  const targetVehicle = vehicles.value.find(v => v.registration_number === selectReg);

  if (!targetVehicle) {
    showToast('Validation Error: Selected vehicle registry not found.', 'error');
    return;
  }

  // Hard Business Validation: Vehicle cannot be On Trip
  if (targetVehicle.status === 'On Trip') {
    showToast(`Validation Error: Cannot place vehicle ${selectReg} into active maintenance log because it is currently On Trip.`, 'error');
    return;
  }

  isSubmitting.value = true;

  // Prevent duplicate submissions and trigger success toast
  setTimeout(() => {
    const newId = logs.value.length > 0 ? Math.max(...logs.value.map(l => l.id)) + 1 : 201;
    
    logs.value.unshift({
      id: newId,
      vehicle_id: selectReg,
      description: String(newLog.description).trim(),
      cost: Number(newLog.cost),
      date: newLog.date,
      status: newLog.status
    });

    if (newLog.status === 'Open') {
      targetVehicle.status = 'In Shop';
    }

    showToast(`Maintenance log #${newId} recorded successfully!`, 'success');
    showLogForm.value = false;
    isSubmitting.value = false;

    // Reset Form
    newLog.vehicle_id = '';
    newLog.description = '';
    newLog.cost = 0;
    newLog.status = 'Open';
  }, 800);
};

const closeLog = async (log) => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;

  setTimeout(() => {
    log.status = 'Closed';
    const targetVehicle = vehicles.value.find(v => v.registration_number === log.vehicle_id);
    if (targetVehicle) {
      targetVehicle.status = 'Available';
    }
    showToast(`Maintenance log #${log.id} marked as closed. Vehicle returns to Available status.`, 'success');
    isSubmitting.value = false;
  }, 500);
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

/* Mobile Accordions */
.mobile-accordion-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-accordion-card {
  padding: 0;
  overflow: hidden;
  border-radius: var(--border-radius-md);
  transition: border-color 0.2s ease;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.1rem 1.25rem;
  cursor: pointer;
}

.vital-col {
  flex: 1;
  font-size: 0.9rem;
}

.chevron {
  color: var(--text-muted);
  font-size: 0.85rem;
  transition: transform 0.2s ease;
}

.mobile-accordion-card.expanded .chevron {
  transform: rotate(180deg);
}

.accordion-content {
  background-color: rgba(255, 255, 255, 0.01);
  border-top: 1px solid var(--border-color);
  padding: 1.1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  animation: slideDown 0.2s ease-out;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.meta-row .lbl {
  color: var(--text-secondary);
}

.meta-row .val {
  color: #fff;
  font-weight: 600;
}

.text-white {
  color: #fff;
}

.action-row {
  margin-top: 0.5rem;
  justify-content: flex-end;
}
</style>
