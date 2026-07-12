<template>
  <div class="dashboard-container driver-theme">
    <div class="page-header">
      <div>
        <h1>My Active Dispatches</h1>
        <p class="subtitle">Real-time status updates and trip logging</p>
      </div>
    </div>

    <!-- Linear Workflow Stepper Widget -->
    <div class="card stepper-card">
      <div class="card-header">
        <h3>Workflow Actions</h3>
        <span v-if="activeTrip" class="badge badge-info">Trip #{{ activeTrip.id }}</span>
      </div>

      <div v-if="activeTrip" class="stepper-widget">
        <!-- Horizontal Stepper Bar -->
        <div class="stepper-steps">
          <div class="step-item" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
            <span class="step-num">1</span>
            <span class="step-text">Assigned</span>
          </div>
          <div class="step-divider" :class="{ active: currentStep > 1 }"></div>
          <div class="step-item" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
            <span class="step-num">2</span>
            <span class="step-text">On Road</span>
          </div>
          <div class="step-divider" :class="{ active: currentStep > 2 }"></div>
          <div class="step-item" :class="{ active: currentStep >= 3 }">
            <span class="step-num">3</span>
            <span class="step-text">Finished</span>
          </div>
        </div>

        <!-- Trip details container -->
        <div class="active-trip-details">
          <div class="detail-row">
            <div>
              <span class="label">Route</span>
              <span class="value">{{ activeTrip.source }} &rarr; {{ activeTrip.destination }}</span>
            </div>
            <div>
              <span class="label">Cargo Weight</span>
              <span class="value font-mono">{{ activeTrip.cargo_weight }} kg</span>
            </div>
            <div>
              <span class="label">Distance</span>
              <span class="value font-mono">{{ activeTrip.planned_distance }} km</span>
            </div>
          </div>

            <!-- Stepper Actions Context -->
            <div class="workflow-actions">
              <!-- Step 1: Draft -> Dispatch -->
              <div v-if="activeTrip.status === 'Draft'" class="action-block">
                <p>Verify cargo loading limits and click to declare departure.</p>
                <button @click="startTrip" class="btn-primary" :disabled="isSubmitting">
                  <Compass class="btn-icon-svg" /> Start Departure
                </button>
              </div>

              <!-- Step 2: Dispatched -> Complete -->
              <div v-else-if="activeTrip.status === 'Dispatched'" class="action-block">
                <p class="warning-text">Enter trip closing values to complete this dispatch.</p>
                <div class="form-row">
                  <div class="form-group">
                    <label>Actual Distance Traveled (km)</label>
                    <input type="number" v-model.number="completionData.actualDistance" required />
                  </div>
                  <div class="form-group">
                    <label>Logged Fuel Cost ($)</label>
                    <input type="number" v-model.number="completionData.fuelCost" required />
                  </div>
                </div>
                <button @click="finishTrip" class="btn-primary" :disabled="!completionData.actualDistance || !completionData.fuelCost || isSubmitting">
                  <Check class="btn-icon-svg" /> Complete Trip
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- No active dispatches placeholder -->
        <div v-else class="empty-dispatcher">
          <Compass class="dispatcher-icon-svg text-primary" />
          <h4>No Active Dispatches</h4>
          <p>You have completed all assigned routes. Awaiting dispatcher scheduling.</p>
        </div>
      </div>

    <!-- Historical Trips Card -->
    <div class="card">
      <div class="card-header">
        <h3>My Completed Shifts</h3>
        <p class="card-subtitle">Historical dispatches records</p>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>Trip ID</th>
            <th>Route</th>
            <th>Cargo</th>
            <th>Distance</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in driverTrips" :key="t.id">
            <td class="font-mono">#{{ t.id }}</td>
            <td>{{ t.source }} &rarr; {{ t.destination }}</td>
            <td>{{ t.cargo_weight }} kg</td>
            <td>{{ t.planned_distance }} km</td>
            <td>
              <span class="badge badge-success">Completed</span>
            </td>
          </tr>
          <tr v-if="driverTrips.length === 0">
            <td colspan="5" class="text-center empty-row">No completed dispatches logged.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Compass, Check } from '@lucide/vue';
import { useToast } from '../../composables/useToast';
import { useApiResource } from '../../composables/useApiResource';

const { showToast } = useToast();
const isSubmitting = ref(false);

const { data: allTrips, fetch: fetchTrips } = useApiResource('/trips');
const { data: allDrivers, fetch: fetchDrivers } = useApiResource('/drivers');

const driverName = ref('');

const driverTrips = computed(() => {
  if (!driverName.value) return [];
  return (allTrips.value || []).filter(t => t.driver_id === driverName.value && t.status === 'Completed');
});

const activeTrip = computed(() => {
  if (!driverName.value) return null;
  return (allTrips.value || []).find(t => t.driver_id === driverName.value && (t.status === 'Dispatched' || t.status === 'Draft' || t.status === 'Ongoing'));
});

const currentStep = computed(() => {
  if (!activeTrip.value) return 3;
  if (activeTrip.value.status === 'Draft') return 1;
  if (activeTrip.value.status === 'Dispatched' || activeTrip.value.status === 'Ongoing') return 2;
  return 3;
});

const completionData = reactive({
  actualDistance: 95,
  fuelCost: 120
});

onMounted(async () => {
  const user = JSON.parse(localStorage.getItem('transitops_user') || '{}');
  await fetchDrivers();
  // Match driver name with email
  const matchedDriver = (allDrivers.value || []).find(d => d.email === user.email);
  driverName.value = matchedDriver ? matchedDriver.name : 'Fatima Diaz';
  await fetchTrips();
});

const startTrip = () => {
  showToast('Departure declared! Drive safely.', 'success');
};

const finishTrip = () => {
  showToast('Trip dispatches completed successfully and logged!', 'success');
};
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
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

/* Stepper widget for Drivers layout */
.stepper-card {
  border-left: 4px solid var(--primary);
}

.stepper-widget {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin: 1rem 0;
}

.stepper-steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background-color: var(--card-bg);
  padding: 1.25rem 2rem;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  background-color: var(--panel-bg);
}

.step-text {
  font-size: 0.85rem;
  font-weight: 700;
}

.step-item.active {
  color: var(--primary);
}
.step-item.active .step-num {
  border-color: var(--primary);
  box-shadow: 0 0 10px var(--primary-glow);
}

.step-item.completed {
  color: var(--success);
}
.step-item.completed .step-num {
  border-color: var(--success);
  background-color: var(--success-glow);
}

.step-divider {
  flex: 1;
  height: 2px;
  background-color: var(--border-color);
  margin: 0 1rem;
}

.step-divider.active {
  background-color: var(--primary);
}

.active-trip-details {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.detail-row .label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.detail-row .value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #fff;
}

.workflow-actions {
  border-top: 1px solid var(--border-color);
  padding-top: 1.5rem;
}

.action-block p {
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.action-block .form-row {
  margin-bottom: 1.25rem;
}

.warning-text {
  color: var(--warning);
  font-weight: 600;
}

.empty-dispatcher {
  text-align: center;
  padding: 3rem 1.5rem;
}

.dispatcher-icon-svg {
  width: 48px;
  height: 48px;
  display: block;
  margin: 0 auto 1rem auto;
}

.empty-dispatcher h4 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.empty-dispatcher p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  max-width: 320px;
  margin: 0 auto;
}

.font-mono { font-family: var(--mono); }
.font-bold { font-weight: 700; }
.highlight-text { color: #fff; }

@media (max-width: 600px) {
  .stepper-steps {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .step-divider {
    display: none;
  }
  .step-item {
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }
}
</style>
