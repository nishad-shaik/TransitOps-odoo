<template>
  <div class="expenses-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Fuel &amp; Expenses</h1>
        <p class="subtitle">Log fuel cards and record additional operational expenditures</p>
      </div>
      <div class="actions">
        <button @click="showFuelModal = true" class="btn-secondary">+ Log Fuel</button>
        <button @click="showExpenseModal = true" class="btn-primary">+ Add Expense</button>
      </div>
    </div>

    <!-- Live Cost Rollup Metric Card -->
    <div class="cost-rollup-card">
      <div class="rollup-metric">
        <span class="label">Total Operational Cost (Rollup)</span>
        <span class="value">${{ totalOperationalCost.toLocaleString() }}</span>
        <span class="subtext">Auto-computed: Fuel Cost + Maintenance Service Costs</span>
      </div>
      <div class="glow-orb"></div>
    </div>

    <!-- Tables Grid -->
    <div class="expense-grids">
      <!-- Fuel Logs Table Card -->
      <div class="card grid-card">
        <div class="card-header">
          <h3>Fuel Logs</h3>
          <p class="card-subtitle font-bold">Fuel card fill receipts</p>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Date</th>
              <th>Liters</th>
              <th>Fuel Cost ($)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in fuelLogs" :key="log.id">
              <td class="font-bold highlight-text">{{ log.vehicle }}</td>
              <td>{{ log.date }}</td>
              <td class="font-bold">{{ log.liters }} L</td>
              <td class="font-bold">${{ log.cost.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Other Expenses Table Card -->
      <div class="card grid-card">
        <div class="card-header">
          <h3>Other Expenses</h3>
          <p class="card-subtitle font-bold">Tolls, maintenance, and fees</p>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Trip ID</th>
              <th>Vehicle</th>
              <th>Tolls ($)</th>
              <th>Other ($)</th>
              <th>Maint. Linked</th>
              <th>Total ($)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exp in expenses" :key="exp.id">
              <td class="font-mono highlight-text">#{{ exp.tripId }}</td>
              <td class="font-bold">{{ exp.vehicle }}</td>
              <td>${{ exp.tolls }}</td>
              <td>${{ exp.other }}</td>
              <td>
                <span class="maint-link" v-if="exp.maintId">
                  Maint #{{ exp.maintId }}
                </span>
                <span v-else class="text-muted">None</span>
              </td>
              <td class="font-bold highlight-text">${{ (exp.tolls + exp.other).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showFuelModal" class="modal-overlay" @click.self="showFuelModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Log Fuel Fill</h3>
          <button @click="showFuelModal = false" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="saveFuelLog">
          <div class="form-group">
            <label>Vehicle</label>
            <input type="text" v-model="newFuel.vehicle" placeholder="e.g. VAN-05" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Liters</label>
              <input type="number" v-model.number="newFuel.liters" required />
            </div>
            <div class="form-group">
              <label>Cost ($)</label>
              <input type="number" v-model.number="newFuel.cost" required />
            </div>
          </div>
          <div class="form-group">
            <label>Date</label>
            <input type="date" v-model="newFuel.date" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showFuelModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">Save Fuel Log</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showExpenseModal" class="modal-overlay" @click.self="showExpenseModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Add Operational Expense</h3>
          <button @click="showExpenseModal = false" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="saveExpense">
          <div class="form-row">
            <div class="form-group">
              <label>Trip ID</label>
              <input type="number" v-model.number="newExpense.tripId" required />
            </div>
            <div class="form-group">
              <label>Vehicle</label>
              <input type="text" v-model="newExpense.vehicle" placeholder="e.g. TRK-02" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Tolls ($)</label>
              <input type="number" v-model.number="newExpense.tolls" required />
            </div>
            <div class="form-group">
              <label>Other Costs ($)</label>
              <input type="number" v-model.number="newExpense.other" required />
            </div>
          </div>
          <div class="form-group">
            <label>Linked Maintenance Log ID (Optional)</label>
            <input type="number" v-model.number="newExpense.maintId" placeholder="e.g. 201" />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showExpenseModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">Save Expense</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';

const showFuelModal = ref(false);
const showExpenseModal = ref(false);

const fuelLogs = ref([
  { id: 1, vehicle: 'VAN-05', date: '2026-07-11', liters: 45, cost: 90 },
  { id: 2, vehicle: 'TRK-02', date: '2026-07-10', liters: 210, cost: 420 },
  { id: 3, vehicle: 'SDN-01', date: '2026-07-09', liters: 32, cost: 64 }
]);

const expenses = ref([
  { id: 1, tripId: 1045, vehicle: 'VAN-05', tolls: 15, other: 5, maintId: null },
  { id: 2, tripId: 1044, vehicle: 'TRK-02', tolls: 85, other: 24, maintId: null },
  { id: 3, vehicle: 'VAN-02', tolls: 0, other: 0, maintId: 201 }
]);

const simulatedMaintenanceCost = 600;

const totalOperationalCost = computed(() => {
  const fuelTotal = fuelLogs.value.reduce((acc, log) => acc + log.cost, 0);
  return fuelTotal + simulatedMaintenanceCost;
});

const newFuel = reactive({
  vehicle: '',
  liters: 0,
  cost: 0,
  date: new Date().toISOString().split('T')[0]
});

const newExpense = reactive({
  tripId: 0,
  vehicle: '',
  tolls: 0,
  other: 0,
  maintId: null
});

const saveFuelLog = () => {
  fuelLogs.value.unshift({
    id: fuelLogs.value.length + 1,
    ...newFuel
  });
  showFuelModal.value = false;
  newFuel.vehicle = '';
  newFuel.liters = 0;
  newFuel.cost = 0;
};

const saveExpense = () => {
  expenses.value.unshift({
    id: expenses.value.length + 1,
    ...newExpense
  });
  showExpenseModal.value = false;
  newExpense.tripId = 0;
  newExpense.vehicle = '';
  newExpense.tolls = 0;
  newExpense.other = 0;
  newExpense.maintId = null;
};
</script>

<style scoped>
.expenses-container {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
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

.actions {
  display: flex;
  gap: 0.75rem;
}

.cost-rollup-card {
  background: linear-gradient(135deg, var(--primary) 0%, #4f46e5 100%);
  color: white;
  padding: 2.25rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-primary);
  position: relative;
  overflow: hidden;
}

.rollup-metric {
  position: relative;
  z-index: 2;
}

.rollup-metric .label {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.9;
}

.rollup-metric .value {
  font-size: 3rem;
  font-weight: 800;
  margin: 0.5rem 0;
  letter-spacing: -0.03em;
}

.rollup-metric .subtext {
  font-size: 0.85rem;
  opacity: 0.8;
}

.glow-orb {
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%);
  pointer-events: none;
}

.expense-grids {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.75rem;
}

.card-header h3 {
  margin: 0;
}

.card-subtitle {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.25rem;
}

.font-mono { font-family: var(--mono); }
.font-bold { font-weight: 700; }
.highlight-text { color: #fff; }

.text-muted {
  color: var(--text-muted);
  font-style: italic;
  font-size: 0.85rem;
}

.maint-link {
  font-size: 0.8rem;
  background-color: var(--primary-glow);
  color: var(--primary);
  border: 1px solid rgba(170, 59, 255, 0.2);
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-weight: 700;
}

/* Modal Headers */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 1000px) {
  .expense-grids {
    grid-template-columns: 1fr;
  }
}
</style>
