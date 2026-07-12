<template>
  <div class="trips-container">
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
      <form @submit.prevent="dispatchTrip">
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
            <select v-model="selectedVehicleIndex" @change="checkCapacity">
              <option value="-1">-- Choose Vehicle --</option>
              <option v-for="(v, index) in availableVehicles" :key="v.regNo" :value="index">
                {{ v.regNo }} - {{ v.model }} (Max Load: {{ v.maxLoad }}kg)
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Select Driver (Available &amp; Valid only)</label>
            <select v-model="selectedDriverIndex">
              <option value="-1">-- Choose Driver --</option>
              <option v-for="(d, index) in availableDrivers" :key="d.licenseNo" :value="index">
                {{ d.name }} (Score: {{ d.safetyScore }})
              </option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Cargo Weight (kg)</label>
            <input
              type="number"
              v-model.number="newTrip.cargoWeight"
              @input="checkCapacity"
              required
            />
          </div>
          <div class="form-group">
            <label>Planned Distance (km)</label>
            <input type="number" v-model.number="newTrip.plannedDistance" required />
          </div>
        </div>

        <!-- Live Business Validation Warning -->
        <div v-if="validationError" class="validation-warning">
          ⚠️ {{ validationError }}
        </div>

        <div class="form-actions">
          <button type="button" @click="showCreateForm = false" class="btn-secondary">Cancel</button>
          <button type="submit" class="btn-primary" :disabled="!!validationError || selectedVehicleIndex == -1 || selectedDriverIndex == -1">
            Dispatch Trip
          </button>
        </div>
      </form>
    </div>

    <!-- Trips Dashboard / Live Board -->
    <div class="trips-board">
      <div class="board-column">
        <h3>Drafts</h3>
        <div class="trip-cards">
          <div v-for="t in getTripsByStatus('Draft')" :key="t.id" class="trip-card draft">
            <div class="card-title">Trip #{{ t.id }}</div>
            <div class="route-info"><strong>Route:</strong> {{ t.source }} &rarr; {{ t.destination }}</div>
            <div class="details">Weight: {{ t.cargoWeight }}kg | Dist: {{ t.plannedDistance }}km</div>
            <div class="notes text-muted">Awaiting vehicle &amp; driver assignment</div>
            <div class="actions">
              <button @click="selectForEdit(t)" class="btn-sm btn-accent">Assign</button>
            </div>
          </div>
          <div v-if="getTripsByStatus('Draft').length === 0" class="empty-state">No drafts.</div>
        </div>
      </div>

      <div class="board-column">
        <h3>Dispatched</h3>
        <div class="trip-cards">
          <div v-for="t in getTripsByStatus('Dispatched')" :key="t.id" class="trip-card dispatched">
            <div class="card-title">Trip #{{ t.id }}</div>
            <div class="route-info"><strong>Route:</strong> {{ t.source }} &rarr; {{ t.destination }}</div>
            <div class="assignment">
              <div><strong>Vehicle:</strong> {{ t.vehicle }}</div>
              <div><strong>Driver:</strong> {{ t.driver }}</div>
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
        <h3>Completed</h3>
        <div class="trip-cards">
          <div v-for="t in getTripsByStatus('Completed')" :key="t.id" class="trip-card completed">
            <div class="card-title">Trip #{{ t.id }}</div>
            <div class="route-info"><strong>Route:</strong> {{ t.source }} &rarr; {{ t.destination }}</div>
            <div class="assignment">
              <div><strong>Vehicle:</strong> {{ t.vehicle }}</div>
              <div><strong>Driver:</strong> {{ t.driver }}</div>
            </div>
            <div class="details text-success">Odometer updated: +{{ t.plannedDistance }}km</div>
          </div>
          <div v-if="getTripsByStatus('Completed').length === 0" class="empty-state">No completed trips.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';

const showCreateForm = ref(false);
const selectedVehicleIndex = ref(-1);
const selectedDriverIndex = ref(-1);
const validationError = ref('');

const availableVehicles = ref([
  { regNo: 'VAN-05', model: 'Ford Transit 350', maxLoad: 500 },
  { regNo: 'SDN-01', model: 'Toyota Camry hybrid', maxLoad: 350 }
]);

const availableDrivers = ref([
  { name: 'Alex Johnson', licenseNo: 'DL-55291', safetyScore: 92 },
  { name: 'Peter Parker', licenseNo: 'DL-12290', safetyScore: 95 }
]);

const trips = ref([
  { id: 1045, source: 'Depot North', destination: 'Warehouse South', vehicle: 'VAN-05', driver: 'Alex Johnson', cargoWeight: 450, plannedDistance: 85, status: 'Dispatched', eta: '1h 15m' },
  { id: 1044, source: 'Depot East', destination: 'Distribution Hub', vehicle: 'TRK-02', driver: 'Sarah Connor', cargoWeight: 2200, plannedDistance: 310, status: 'Completed' },
  { id: 1042, source: 'Depot West', destination: 'Airport Cargo Terminal', vehicle: null, driver: null, cargoWeight: 800, plannedDistance: 45, status: 'Draft' }
]);

const newTrip = reactive({
  source: '',
  destination: '',
  cargoWeight: 0,
  plannedDistance: 0
});

const getTripsByStatus = (status) => {
  return trips.value.filter(t => t.status === status);
};

const checkCapacity = () => {
  validationError.value = '';
  const vehicleIdx = parseInt(selectedVehicleIndex.value);
  if (vehicleIdx >= 0) {
    const vehicle = availableVehicles.value[vehicleIdx];
    if (newTrip.cargoWeight > vehicle.maxLoad) {
      const overage = newTrip.cargoWeight - vehicle.maxLoad;
      validationError.value = `Capacity exceeded by ${overage}kg — dispatch blocked`;
    }
  }
};

const dispatchTrip = () => {
  checkCapacity();
  if (validationError.value) return;

  const vehicle = availableVehicles.value[selectedVehicleIndex.value];
  const driver = availableDrivers.value[selectedDriverIndex.value];

  const dispatchedRecord = {
    id: trips.value.length + 1041,
    source: newTrip.source,
    destination: newTrip.destination,
    vehicle: vehicle.regNo,
    driver: driver.name,
    cargoWeight: newTrip.cargoWeight,
    plannedDistance: newTrip.plannedDistance,
    status: 'Dispatched',
    eta: 'Calculation pending'
  };

  trips.value.push(dispatchedRecord);
  showCreateForm.value = false;

  // Simulate updating vehicle/driver to 'On Trip' (they get filtered out of the selection lists)
  availableVehicles.value.splice(selectedVehicleIndex.value, 1);
  availableDrivers.value.splice(selectedDriverIndex.value, 1);

  // Reset
  selectedVehicleIndex.value = -1;
  selectedDriverIndex.value = -1;
  newTrip.source = '';
  newTrip.destination = '';
  newTrip.cargoWeight = 0;
  newTrip.plannedDistance = 0;
};

const completeTrip = (trip) => {
  trip.status = 'Completed';
  // Re-add mock vehicle/driver to available pools
  availableVehicles.value.push({ regNo: trip.vehicle, model: 'Restored vehicle', maxLoad: trip.cargoWeight + 200 });
  availableDrivers.value.push({ name: trip.driver, licenseNo: 'MOCK-DL', safetyScore: 85 });
};

const cancelTrip = (trip) => {
  trip.status = 'Cancelled';
  availableVehicles.value.push({ regNo: trip.vehicle, model: 'Restored vehicle', maxLoad: trip.cargoWeight + 200 });
  availableDrivers.value.push({ name: trip.driver, licenseNo: 'MOCK-DL', safetyScore: 85 });
};

const selectForEdit = (trip) => {
  newTrip.source = trip.source;
  newTrip.destination = trip.destination;
  newTrip.cargoWeight = trip.cargoWeight;
  newTrip.plannedDistance = trip.plannedDistance;
  showCreateForm.value = true;
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
  margin: 0;
  font-size: 1.75rem;
  color: var(--text-h);
}

.subtitle {
  margin: 0.25rem 0 0 0;
  color: var(--text);
  font-size: 0.9rem;
}

.card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1.25rem;
  box-shadow: var(--shadow);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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

.validation-warning {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  margin-bottom: 1rem;
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
  background-color: var(--social-bg);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  min-height: 400px;
}

.board-column h3 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: var(--text-h);
  border-bottom: 2px solid var(--border);
  padding-bottom: 0.5rem;
}

.trip-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trip-card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  padding: 0.85rem;
  box-shadow: var(--shadow);
}

.trip-card.draft { border-left: 4px solid var(--border); }
.trip-card.dispatched { border-left: 4px solid #3b82f6; }
.trip-card.completed { border-left: 4px solid #10b981; }

.card-title {
  font-weight: 700;
  color: var(--text-h);
  margin-bottom: 0.5rem;
}

.route-info {
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.assignment {
  font-size: 0.8rem;
  margin: 0.5rem 0;
  padding: 0.4rem;
  background-color: var(--social-bg);
  border-radius: 0.25rem;
}

.details {
  font-size: 0.8rem;
  color: var(--text);
}

.notes {
  font-size: 0.75rem;
  margin: 0.5rem 0;
}

.font-bold { font-weight: 600; }
.text-accent { color: var(--accent); }
.text-success { color: #10b981; }
.text-muted { color: var(--text); }

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.btn-sm.btn-accent { background-color: var(--accent); color: white; }
.btn-sm.btn-success { background-color: #10b981; color: white; }
.btn-sm.btn-danger { background-color: #ef4444; color: white; }

.empty-state {
  text-align: center;
  color: var(--text);
  font-size: 0.85rem;
  padding: 2rem 0;
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

.btn-secondary {
  padding: 0.5rem 1rem;
  background-color: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-h);
  border-radius: 0.375rem;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 768px) {
  .trips-board {
    grid-template-columns: 1fr;
  }
}
</style>
