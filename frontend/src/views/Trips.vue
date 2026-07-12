<template>
  <div class="trips-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Trip Dispatcher</h1>
        <p class="subtitle">Plan, dispatch, and track trips across your fleet</p>
      </div>
      <button @click="showCreateForm = !showCreateForm" class="btn-primary">
        {{ showCreateForm ? 'Hide Form' : '+ New Dispatch' }}
      </button>
    </div>

    <!-- Dispatch Creation Form -->
    <div v-if="showCreateForm" class="card form-card">
      <h3>Create Dispatch Record</h3>
      <form @submit.prevent="openConfirmationModal">
        <div class="form-row">
          <div class="form-group">
            <label>Source Location</label>
            <input type="text" v-model="newTrip.source" placeholder="e.g. Depot East" required />
          </div>
          <div class="form-group">
            <label>Destination Location</label>
            <input type="text" v-model="newTrip.destination" placeholder="e.g. Retail Center B" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Select Vehicle (Available only)</label>
            <select v-model="selectedVehicleIndex" @change="handleVehicleChange">
              <option value="-1">-- Choose Vehicle --</option>
              <option v-for="(v, index) in availableVehicles" :key="v.registration_number" :value="index">
                {{ v.registration_number }} - {{ v.vehicle_name }} (Max Load: {{ v.max_load_capacity }}kg | Status: {{ v.status }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Select Driver (Available &amp; Valid only)</label>
            <select v-model="selectedDriverIndex">
              <option value="-1">-- Choose Driver --</option>
              <option v-for="(d, index) in availableDrivers" :key="d.license_number" :value="index">
                {{ d.name }} (Score: {{ d.safety_score }} | Expiry: {{ d.license_expiry_date }})
              </option>
            </select>
          </div>
        </div>

        <!-- Cargo weight with progressive validation bar -->
        <div class="form-row">
          <div class="form-group">
            <label>Cargo Weight (kg)</label>
            <input
              type="number"
              v-model.number="newTrip.cargo_weight"
              @input="validateTripCapacity"
              required
            />
            
            <!-- Progressive Validation Bar -->
            <div class="capacity-tracker" v-if="selectedVehicle">
              <div class="progress-bar-wrapper">
                <div 
                  class="progress-fill" 
                  :style="{ width: Math.min(capacityPercentage, 100) + '%' }" 
                  :class="{ 'over-capacity': capacityPercentage > 100 }"
                ></div>
              </div>
              <div class="progress-metrics" :class="{ 'danger-text': capacityPercentage > 100 }">
                <span>{{ Math.round(capacityPercentage) }}% Capacity Utilized</span>
                <span>{{ newTrip.cargo_weight }} / {{ selectedVehicle.max_load_capacity }} kg</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Planned Distance (km)</label>
            <input type="number" v-model.number="newTrip.planned_distance" required />
          </div>
        </div>

        <!-- Live Business Validation Warning -->
        <div v-if="validationError" class="validation-warning">
          <AlertTriangle class="warning-icon-svg" />
          <span>{{ validationError }}</span>
        </div>

        <div class="form-actions">
          <button type="button" @click="showCreateForm = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary">
            Dispatch Trip
          </button>
        </div>
      </form>
    </div>

    <!-- Trips Dashboard / Live Board -->
    <div class="trips-board">
      <div class="board-column">
        <div class="column-header">
          <h3>Drafts</h3>
          <span class="column-count">{{ getTripsByStatus('Draft').length }}</span>
        </div>
        <div class="trip-cards">
          <div v-for="t in getTripsByStatus('Draft')" :key="t.id" class="trip-card draft">
            <div class="card-title">Trip #{{ t.id }}</div>
            <div class="route-info"><strong>Route:</strong> {{ t.source }} &rarr; {{ t.destination }}</div>
            <div class="details">Weight: {{ t.cargo_weight }}kg | Dist: {{ t.planned_distance }}km</div>
            <div class="notes font-bold text-muted">Awaiting vehicle &amp; driver assignment</div>
            <div class="actions">
              <button @click="selectForEdit(t)" class="btn-sm btn-accent">Assign</button>
            </div>
          </div>
          <div v-if="getTripsByStatus('Draft').length === 0" class="empty-state">No drafts.</div>
        </div>
      </div>

      <div class="board-column">
        <div class="column-header">
          <h3>Dispatched</h3>
          <span class="column-count">{{ getTripsByStatus('Dispatched').length }}</span>
        </div>
        <div class="trip-cards">
          <div v-for="t in getTripsByStatus('Dispatched')" :key="t.id" class="trip-card dispatched">
            <div class="card-title">Trip #{{ t.id }}</div>
            <div class="route-info"><strong>Route:</strong> {{ t.source }} &rarr; {{ t.destination }}</div>
            <div class="assignment">
              <div><strong>Vehicle:</strong> {{ t.vehicle_id }}</div>
              <div><strong>Driver:</strong> {{ t.driver_id }}</div>
            </div>
            <div class="notes font-bold text-accent">ETA: {{ t.eta }}</div>
            <div class="actions">
              <button @click="completeTrip(t)" class="btn-sm btn-success">Complete</button>
              <button @click="cancelTrip(t)" class="btn-sm btn-danger">Cancel</button>
            </div>
          </div>
          <div v-if="getTripsByStatus('Dispatched').length === 0" class="empty-state">No active trips.</div>
        </div>
      </div>

      <div class="board-column">
        <div class="column-header">
          <h3>Completed</h3>
          <span class="column-count">{{ getTripsByStatus('Completed').length }}</span>
        </div>
        <div class="trip-cards">
          <div v-for="t in getTripsByStatus('Completed')" :key="t.id" class="trip-card completed">
            <div class="card-title">Trip #{{ t.id }}</div>
            <div class="route-info"><strong>Route:</strong> {{ t.source }} &rarr; {{ t.destination }}</div>
            <div class="assignment">
              <div><strong>Vehicle:</strong> {{ t.vehicle_id }}</div>
              <div><strong>Driver:</strong> {{ t.driver_id }}</div>
            </div>
            <div class="details text-success font-bold">Odometer updated: +{{ t.planned_distance }}km</div>
          </div>
          <div v-if="getTripsByStatus('Completed').length === 0" class="empty-state">No completed trips.</div>
        </div>
      </div>
    </div>

    <!-- Trip Log History Grid (Desktop: Comprehensive table / Mobile: Condensed expandable accordion) -->
    <div class="card grid-card mt-6">
      <div class="grid-header">
        <h3>Trip Log Registry</h3>
        <span class="row-count">Records: {{ trips.length }}</span>
      </div>

      <!-- Desktop View (md and above) -->
      <div class="table-wrapper hidden md:block">
        <table class="data-table">
          <thead>
            <tr>
              <th>Trip ID</th>
              <th>Route</th>
              <th>Vehicle</th>
              <th>Driver</th>
              <th>Cargo Weight</th>
              <th>Distance</th>
              <th>Status</th>
              <th>ETA</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in trips" :key="t.id">
              <td class="font-mono highlight-text">#{{ t.id }}</td>
              <td>{{ t.source }} &rarr; {{ t.destination }}</td>
              <td>{{ t.vehicle_id || 'Not assigned' }}</td>
              <td>{{ t.driver_id || 'Not assigned' }}</td>
              <td>{{ t.cargo_weight }} kg</td>
              <td>{{ t.planned_distance }} km</td>
              <td>
                <span class="badge" :class="badgeClass(t.status)">
                  {{ t.status }}
                </span>
              </td>
              <td>{{ t.eta || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile View (hidden on md and above) -->
      <div class="mobile-accordion-list block md:hidden">
        <div 
          v-for="t in trips" 
          :key="'mobile-trip-' + t.id" 
          class="card mobile-accordion-card"
          :class="{ expanded: expandedTrips.includes(t.id) }"
        >
          <!-- Accordion Header: 3 Vital columns only -->
          <div class="accordion-header" @click="toggleTripAccordion(t.id)">
            <div class="vital-col font-mono font-bold text-white">#{{ t.id }} - {{ t.driver_id || 'Unassigned' }}</div>
            <div class="vital-col">
              <span class="badge" :class="badgeClass(t.status)">
                {{ t.status }}
              </span>
            </div>
            <div class="vital-col text-right pr-4 font-bold">{{ t.planned_distance }} km</div>
            <span class="chevron">&#9662;</span>
          </div>

          <!-- Accordion Content -->
          <div class="accordion-content" v-if="expandedTrips.includes(t.id)">
            <div class="meta-row">
              <span class="lbl">Route:</span>
              <span class="val">{{ t.source }} &rarr; {{ t.destination }}</span>
            </div>
            <div class="meta-row">
              <span class="lbl">Vehicle:</span>
              <span class="val">{{ t.vehicle_id || 'Unassigned' }}</span>
            </div>
            <div class="meta-row">
              <span class="lbl">Cargo Load Weight:</span>
              <span class="val font-mono">{{ t.cargo_weight }} kg</span>
            </div>
            <div class="meta-row">
              <span class="lbl">Estimated ETA:</span>
              <span class="val font-mono">{{ t.eta || 'N/A' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Two-Step Dispatch Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal confirm-modal">
        <div class="modal-header">
          <h3>Confirm Fleet Dispatch</h3>
          <button @click="showConfirmModal = false" class="close-btn">&times;</button>
        </div>
        
        <div class="confirm-content" v-if="selectedVehicle && selectedDriver">
          <p class="confirm-alert-text"><AlertTriangle class="confirm-alert-icon-svg inline-block text-warning mr-2" /> Are you sure you want to dispatch this vehicle? Action will update driver and vehicle schedules to "On Trip".</p>
          
          <div class="summary-card">
            <div class="summary-item">
              <span class="lbl">Route:</span>
              <span class="val font-bold">{{ newTrip.source }} &rarr; {{ newTrip.destination }}</span>
            </div>
            <div class="summary-item">
              <span class="lbl">Vehicle assigned:</span>
              <span class="val font-bold text-accent">{{ selectedVehicle.registration_number }} ({{ selectedVehicle.vehicle_name }})</span>
            </div>
            <div class="summary-item">
              <span class="lbl">Driver assigned:</span>
              <span class="val font-bold text-accent">{{ selectedDriver.name }}</span>
            </div>
            <div class="summary-item">
              <span class="lbl">Cargo Load:</span>
              <span class="val font-bold">{{ newTrip.cargo_weight }} kg</span>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="showConfirmModal = false" class="btn-secondary">Cancel</button>
          <button @click="dispatchTrip" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Dispatching...' : 'Confirm & Dispatch' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue';
import { AlertTriangle } from '@lucide/vue';
import { useToast } from '../composables/useToast';
import { useApiResource } from '../composables/useApiResource';

const { showToast } = useToast();

const showCreateForm = ref(false);
const showConfirmModal = ref(false);
const selectedVehicleIndex = ref(-1);
const selectedDriverIndex = ref(-1);
const validationError = ref('');
const isSubmitting = ref(false);
const expandedTrips = ref([]);

const { data: apiVehicles, fetch: fetchVehicles } = useApiResource('/vehicles');
const { data: apiDrivers, fetch: fetchDrivers } = useApiResource('/drivers');
const { data: apiTrips, fetch: fetchTrips, create: createTrip } = useApiResource('/trips');

const availableVehicles = computed(() => (apiVehicles.value || []).filter(v => v.status === 'Available'));
const availableDrivers = computed(() => (apiDrivers.value || []).filter(d => d.status === 'Available'));
const trips = computed(() => apiTrips.value || []);

onMounted(() => {
  fetchVehicles();
  fetchDrivers();
  fetchTrips();
});

const newTrip = reactive({
  source: '',
  destination: '',
  cargo_weight: 0,
  planned_distance: 0
});


const toggleTripAccordion = (id) => {
  if (expandedTrips.value.includes(id)) {
    expandedTrips.value = expandedTrips.value.filter(t => t !== id);
  } else {
    expandedTrips.value.push(id);
  }
};

const getTripsByStatus = (status) => {
  return trips.value.filter(t => t.status === status);
};

const selectedVehicle = computed(() => {
  const idx = parseInt(selectedVehicleIndex.value);
  return idx >= 0 ? availableVehicles.value[idx] : null;
});

const selectedDriver = computed(() => {
  const idx = parseInt(selectedDriverIndex.value);
  return idx >= 0 ? availableDrivers.value[idx] : null;
});

const capacityPercentage = computed(() => {
  if (!selectedVehicle.value || !newTrip.cargo_weight) return 0;
  return (newTrip.cargo_weight / selectedVehicle.value.max_load_capacity) * 100;
});

const validateTripCapacity = () => {
  validationError.value = '';
  if (selectedVehicle.value) {
    if (newTrip.cargo_weight > selectedVehicle.value.max_load_capacity) {
      const overage = newTrip.cargo_weight - selectedVehicle.value.max_load_capacity;
      validationError.value = `Capacity exceeded by ${overage}kg — dispatch blocked`;
    }
  }
};

const handleVehicleChange = () => {
  validateTripCapacity();
};

const validateOperationalRules = () => {
  if (selectedVehicleIndex.value === -1 || selectedDriverIndex.value === -1) {
    showToast('Validation Error: Select both a vehicle and a driver.', 'error');
    return false;
  }

  // Clone local references
  const vehicle = { ...availableVehicles.value[selectedVehicleIndex.value] };
  const driver = { ...availableDrivers.value[selectedDriverIndex.value] };
  const weight = Number(newTrip.cargo_weight);

  // 1. Capacity weight check
  if (weight > vehicle.max_load_capacity) {
    showToast(`Validation Error: Cargo Weight (${weight}kg) exceeds selected vehicle's Maximum Load Capacity (${vehicle.max_load_capacity}kg).`, 'error');
    return false;
  }

  // 2. Driver status and license validity checks
  const mockCurrentDate = new Date('2026-07-12');
  const expiryDate = new Date(driver.license_expiry_date);
  if (driver.status === 'Suspended' || expiryDate < mockCurrentDate) {
    showToast(`Security Alert: Selected driver (${driver.name}) is Suspended or has an Expired license (${driver.license_expiry_date}).`, 'error');
    return false;
  }

  // 3. Busy states check ("On Trip")
  if (vehicle.status === 'On Trip' || driver.status === 'On Trip') {
    showToast('Operation Blocked: Selected vehicle or driver is currently On Trip.', 'error');
    return false;
  }

  // 4. Shop or Retired state check
  if (vehicle.status === 'In Shop' || vehicle.status === 'Retired') {
    showToast(`Maintenance Blocked: Vehicle ${vehicle.registration_number} has status '${vehicle.status}' and cannot be dispatched.`, 'error');
    return false;
  }

  return true;
};

const openConfirmationModal = () => {
  if (!validateOperationalRules()) return;
  showConfirmModal.value = true;
};

const dispatchTrip = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;

  const vehicle = availableVehicles.value[selectedVehicleIndex.value];
  const driver = availableDrivers.value[selectedDriverIndex.value];

  try {
    await createTrip({
      source: String(newTrip.source).trim(),
      destination: String(newTrip.destination).trim(),
      vehicle_id: vehicle.registration_number,
      driver_id: driver.name,
      cargo_weight: Number(newTrip.cargo_weight),
      planned_distance: Number(newTrip.planned_distance)
    });
    
    // Refresh vehicles and drivers since status changed on backend
    await fetchVehicles();
    await fetchDrivers();

    // Reset indices and modal
    selectedVehicleIndex.value = -1;
    selectedDriverIndex.value = -1;
    showConfirmModal.value = false;
    showCreateForm.value = false;

    newTrip.source = '';
    newTrip.destination = '';
    newTrip.cargo_weight = 0;
    newTrip.planned_distance = 0;
    
    showToast('Fleet dispatch started successfully!', 'success');
  } catch (err) {
    showToast(err.message || 'Failed to dispatch trip.', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const completeTrip = async (trip) => {
  showToast('Simulated: Complete trip action logged.', 'info');
};

const cancelTrip = async (trip) => {
  showToast('Simulated: Cancel trip action logged.', 'info');
};

const selectForEdit = (trip) => {
  newTrip.source = trip.source;
  newTrip.destination = trip.destination;
  newTrip.cargo_weight = trip.cargo_weight;
  newTrip.planned_distance = trip.planned_distance;
  showCreateForm.value = true;
};

const badgeClass = (status) => {
  if (status === 'Dispatched') return 'badge-info';
  if (status === 'Completed') return 'badge-success';
  if (status === 'Draft') return 'badge-warning';
  return 'badge-danger';
};
</script>

<style scoped>
.trips-container {
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

.capacity-tracker {
  margin-top: 0.5rem;
}

.progress-bar-wrapper {
  height: 0.4rem;
  background-color: var(--border-color);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, #a855f7 100%);
  border-radius: var(--border-radius-sm);
  transition: width 0.3s ease;
}

.progress-fill.over-capacity {
  background: var(--danger);
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
}

.progress-metrics {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
  font-weight: 700;
}

.progress-metrics.danger-text {
  color: var(--danger);
}

.validation-warning {
  background-color: var(--danger-glow);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--danger);
  padding: 0.85rem 1rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.9rem;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.trips-board {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
}

.board-column {
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  padding: 1.25rem;
  border-radius: var(--border-radius-lg);
  min-height: 500px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.column-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
}

.column-count {
  background-color: var(--border-color);
  color: var(--text-primary);
  padding: 0.15rem 0.5rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
}

.trip-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trip-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 1rem;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.trip-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-hover);
}

.trip-card.draft { border-left: 4px solid var(--text-muted); }
.trip-card.dispatched { border-left: 4px solid var(--info); }
.trip-card.completed { border-left: 4px solid var(--success); }

.card-title {
  font-weight: 800;
  color: #fff;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.route-info {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.assignment {
  font-size: 0.8rem;
  margin: 0.75rem 0;
  padding: 0.5rem;
  background-color: var(--panel-bg);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.details {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.notes {
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

.font-bold { font-weight: 700; }
.text-accent { color: var(--primary); }
.text-success { color: var(--success); }
.text-muted { color: var(--text-muted); }

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  border-radius: var(--border-radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 700;
  transition: opacity 0.2s ease;
}

.btn-sm:hover {
  opacity: 0.9;
}

.btn-sm.btn-accent { background-color: var(--primary); color: white; }
.btn-sm.btn-success { background-color: var(--success); color: white; }
.btn-sm.btn-danger { background-color: var(--danger); color: white; }

.empty-state {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 3rem 0;
  border: 1px dashed var(--border-color);
  border-radius: var(--border-radius-md);
}

/* Modal Styling overrides */
.confirm-modal {
  max-width: 480px;
}

.confirm-alert-text {
  font-size: 0.85rem;
  color: var(--warning);
  background-color: var(--warning-glow);
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius-sm);
  border: 1px solid rgba(245, 158, 11, 0.2);
  margin-bottom: 1.25rem;
}

.summary-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.summary-item .lbl {
  color: var(--text-secondary);
}

.summary-item .val {
  color: #fff;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.grid-card {
  padding: 1.5rem;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.grid-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.row-count {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 700;
  background-color: rgba(255,255,255,0.02);
  padding: 0.35rem 0.75rem;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-color);
}

.mt-6 {
  margin-top: 1.75rem;
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

@media (max-width: 950px) {
  .trips-board {
    grid-template-columns: 1fr;
  }
}
</style>
