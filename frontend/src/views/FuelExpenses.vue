<template>
  <div class="expenses-container">
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

    <!-- Live Cost Rollup Metric Panel -->
    <div class="cost-rollup-card">
      <div class="rollup-metric">
        <span class="label">Total Operational Cost (Rollup)</span>
        <span class="value">${{ totalOperationalCost.toLocaleString() }}</span>
        <span class="subtext">Auto-computed: Fuel Cost + Maintenance Service Costs</span>
      </div>
    </div>

    <div class="expense-grids">
      <!-- Fuel Logs Table Card -->
      <div class="card grid-card">
        <div class="card-header">
          <h3>Fuel Logs</h3>
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
              <td class="font-bold">{{ log.vehicle }}</td>
              <td>{{ log.date }}</td>
              <td>{{ log.liters }} L</td>
              <td>${{ log.cost.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Other Expenses Table Card -->
      <div class="card grid-card">
        <div class="card-header">
          <h3>Other Expenses</h3>
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
              <td class="font-mono">#{{ exp.tripId }}</td>
              <td class="font-bold">{{ exp.vehicle }}</td>
              <td>${{ exp.tolls }}</td>
              <td>${{ exp.other }}</td>
              <td>
                <span class="maint-link" v-if="exp.maintId">
                  Maint #{{ exp.maintId }}
                </span>
                <span v-else class="text-muted">None</span>
              </td>
              <td class="font-bold">${{ (exp.tolls + exp.other).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals for adding entries -->
    <div v-if="showFuelModal" class="modal-overlay">
      <div class="modal">
        <h3>Log Fuel Fill</h3>
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

    <div v-if="showExpenseModal" class="modal-overlay">
      <div class="modal">
        <h3>Add Operational Expense</h3>
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
  { id: 3, vehicle: 'VAN-02', tolls: 0, other: 0, maintId: 201 } // Linked maint expense
]);

// Simulated Maintenance costs (from our Maintenance.vue mockup logs: Active record costs 450, closed cost 150)
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

.actions {
  display: flex;
  gap: 1rem;
}

.cost-rollup-card {
  background: linear-gradient(135deg, #aa3bff 0%, #7c3aed 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: var(--shadow);
}

.rollup-metric {
  display: flex;
  flex-direction: column;
}

.rollup-metric .label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.9;
}

.rollup-metric .value {
  font-size: 2.25rem;
  font-weight: 800;
  margin: 0.5rem 0;
}

.rollup-metric .subtext {
  font-size: 0.8rem;
  opacity: 0.8;
}

.expense-grids {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1.25rem;
  box-shadow: var(--shadow);
}

.card-header h3 {
  margin: 0 0 1rem 0;
  color: var(--text-h);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.data-table th {
  color: var(--text);
  font-weight: 600;
}

.data-table td {
  color: var(--text-h);
}

.font-mono { font-family: var(--mono); }
.font-bold { font-weight: 600; }
.text-muted { color: var(--text); font-style: italic; }

.maint-link {
  font-size: 0.8rem;
  background-color: rgba(170, 59, 255, 0.1);
  color: var(--accent);
  padding: 0.15rem 0.3rem;
  border-radius: 0.25rem;
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

/* Modal styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: var(--bg);
  border-radius: 0.5rem;
  padding: 1.5rem;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border);
}

.modal h3 {
  margin: 0 0 1rem 0;
  color: var(--text-h);
}

.form-group {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text);
}

.modal input,
.modal select {
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  background-color: var(--bg);
  color: var(--text-h);
  outline: none;
}

.modal input:focus {
  border-color: var(--accent);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .expense-grids {
    grid-template-columns: 1fr;
  }
}
</style>
