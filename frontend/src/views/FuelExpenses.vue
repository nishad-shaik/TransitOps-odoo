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
      <!-- Fuel Logs Table Card (Desktop: md and above) -->
      <div class="card grid-card">
        <div class="card-header">
          <h3>Fuel Logs</h3>
          <p class="card-subtitle font-bold">Fuel card fill receipts</p>
        </div>

        <!-- Desktop Table -->
        <div class="hidden md:block">
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
                <td class="font-bold highlight-text">{{ log.vehicle_id }}</td>
                <td>{{ log.date }}</td>
                <td class="font-bold">{{ log.liters }} L</td>
                <td class="font-bold">${{ log.amount.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Accordion -->
        <div class="mobile-accordion-list block md:hidden">
          <div 
            v-for="log in fuelLogs" 
            :key="'m-fuel-' + log.id" 
            class="card mobile-accordion-card"
            :class="{ expanded: expandedFuelIds.includes(log.id) }"
          >
            <div class="accordion-header" @click="toggleFuelAccordion(log.id)">
              <div class="vital-col font-bold text-white">{{ log.vehicle_id }}</div>
              <div class="vital-col font-bold">${{ log.amount.toLocaleString() }}</div>
              <div class="vital-col text-right pr-4">{{ log.liters }} L</div>
              <span class="chevron">&#9662;</span>
            </div>
            <div class="accordion-content" v-if="expandedFuelIds.includes(log.id)">
              <div class="meta-row">
                <span class="lbl">Date:</span>
                <span class="val font-mono">{{ log.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Other Expenses Table Card (Desktop: md and above) -->
      <div class="card grid-card">
        <div class="card-header">
          <h3>Other Expenses</h3>
          <p class="card-subtitle font-bold">Tolls, maintenance, and fees</p>
        </div>

        <!-- Desktop Table -->
        <div class="hidden md:block">
          <table class="data-table">
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Date</th>
                <th>Type</th>
                <th>Amount ($)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="exp in expenses" :key="exp.id">
                <td class="font-bold highlight-text">{{ exp.vehicle_id }}</td>
                <td>{{ exp.date }}</td>
                <td>
                  <span class="maint-link" v-if="exp.type === 'Maintenance'">
                    {{ exp.type }}
                  </span>
                  <span v-else>{{ exp.type }}</span>
                </td>
                <td class="font-bold highlight-text">${{ exp.amount.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Accordion -->
        <div class="mobile-accordion-list block md:hidden">
          <div 
            v-for="exp in expenses" 
            :key="'m-exp-' + exp.id" 
            class="card mobile-accordion-card"
            :class="{ expanded: expandedExpIds.includes(exp.id) }"
          >
            <div class="accordion-header" @click="toggleExpAccordion(exp.id)">
              <div class="vital-col font-bold text-white">{{ exp.vehicle_id }}</div>
              <div class="vital-col font-bold">{{ exp.type }}</div>
              <div class="vital-col text-right pr-4 font-bold">${{ exp.amount.toLocaleString() }}</div>
              <span class="chevron">&#9662;</span>
            </div>
            <div class="accordion-content" v-if="expandedExpIds.includes(exp.id)">
              <div class="meta-row">
                <span class="lbl">Date:</span>
                <span class="val font-mono">{{ exp.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Fuel Log Modal -->
    <div v-if="showFuelModal" class="modal-overlay" @click.self="showFuelModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Log Fuel Fill</h3>
          <button @click="showFuelModal = false" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="saveFuelLog">
          <div class="form-group">
            <label>Vehicle</label>
            <input type="text" v-model="newFuel.vehicle_id" placeholder="e.g. VAN-05" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Liters</label>
              <input type="number" v-model.number="newFuel.liters" required />
            </div>
            <div class="form-group">
              <label>Cost ($)</label>
              <input type="number" v-model.number="newFuel.amount" required />
            </div>
          </div>
          <div class="form-group">
            <label>Date</label>
            <input type="date" v-model="newFuel.date" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showFuelModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Posting...' : 'Save Fuel Log' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Expense Modal -->
    <div v-if="showExpenseModal" class="modal-overlay" @click.self="showExpenseModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Add Operational Expense</h3>
          <button @click="showExpenseModal = false" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="saveExpense">
          <div class="form-row">
            <div class="form-group">
              <label>Vehicle</label>
              <input type="text" v-model="newExpense.vehicle_id" placeholder="e.g. TRK-02" required />
            </div>
            <div class="form-group">
              <label>Type</label>
              <select v-model="newExpense.type">
                <option value="Toll">Toll</option>
                <option value="Maintenance">Maintenance</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Amount ($)</label>
              <input type="number" v-model.number="newExpense.amount" required />
            </div>
            <div class="form-group">
              <label>Date</label>
              <input type="date" v-model="newExpense.date" required />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showExpenseModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Posting...' : 'Save Expense' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { useToast } from '../composables/useToast';

const { showToast } = useToast();

const showFuelModal = ref(false);
const showExpenseModal = ref(false);
const isSubmitting = ref(false);
const expandedFuelIds = ref([]);
const expandedExpIds = ref([]);

const fuelLogs = ref([
  { id: 1, vehicle_id: 'VAN-05', date: '2026-07-11', liters: 45, amount: 90, type: 'Fuel' },
  { id: 2, vehicle_id: 'TRK-02', date: '2026-07-10', liters: 210, amount: 420, type: 'Fuel' },
  { id: 3, vehicle_id: 'SDN-01', date: '2026-07-09', liters: 32, amount: 64, type: 'Fuel' }
]);

const expenses = ref([
  { id: 1, vehicle_id: 'VAN-05', amount: 15, date: '2026-07-11', type: 'Toll' },
  { id: 2, vehicle_id: 'TRK-02', amount: 85, date: '2026-07-10', type: 'Toll' },
  { id: 3, vehicle_id: 'VAN-02', amount: 450, date: '2026-07-10', type: 'Maintenance' }
]);

const simulatedMaintenanceCost = 600;

const totalOperationalCost = computed(() => {
  const fuelTotal = fuelLogs.value.reduce((acc, log) => acc + log.amount, 0);
  return fuelTotal + simulatedMaintenanceCost;
});

const toggleFuelAccordion = (id) => {
  if (expandedFuelIds.value.includes(id)) {
    expandedFuelIds.value = expandedFuelIds.value.filter(i => i !== id);
  } else {
    expandedFuelIds.value.push(id);
  }
};

const toggleExpAccordion = (id) => {
  if (expandedExpIds.value.includes(id)) {
    expandedExpIds.value = expandedExpIds.value.filter(i => i !== id);
  } else {
    expandedExpIds.value.push(id);
  }
};

const newFuel = reactive({
  vehicle_id: '',
  liters: 0,
  amount: 0,
  date: new Date().toISOString().split('T')[0],
  type: 'Fuel'
});

const newExpense = reactive({
  vehicle_id: '',
  type: 'Toll',
  amount: 0,
  date: new Date().toISOString().split('T')[0]
});

const saveFuelLog = async () => {
  if (isSubmitting.value) return;

  const vehicleId = String(newFuel.vehicle_id).trim();
  const liters = Number(newFuel.liters);
  const amount = Number(newFuel.amount);

  if (!vehicleId) {
    showToast('Validation Error: Vehicle identifier is required.', 'error');
    return;
  }
  if (liters <= 0 || amount <= 0) {
    showToast('Validation Error: Liters and Cost must be positive values.', 'error');
    return;
  }

  isSubmitting.value = true;

  setTimeout(() => {
    fuelLogs.value.unshift({
      id: fuelLogs.value.length + 1,
      vehicle_id: vehicleId,
      liters,
      amount,
      date: newFuel.date,
      type: 'Fuel'
    });

    showToast(`Fuel log for ${vehicleId} posted successfully!`, 'success');
    showFuelModal.value = false;
    isSubmitting.value = false;

    newFuel.vehicle_id = '';
    newFuel.liters = 0;
    newFuel.amount = 0;
  }, 600);
};

const saveExpense = async () => {
  if (isSubmitting.value) return;

  const vehicleId = String(newExpense.vehicle_id).trim();
  const amount = Number(newExpense.amount);

  if (!vehicleId) {
    showToast('Validation Error: Vehicle is required.', 'error');
    return;
  }
  if (amount < 0) {
    showToast('Validation Error: Cost values cannot be negative.', 'error');
    return;
  }

  isSubmitting.value = true;

  setTimeout(() => {
    expenses.value.unshift({
      id: expenses.value.length + 1,
      vehicle_id: vehicleId,
      amount,
      type: newExpense.type,
      date: newExpense.date
    });

    showToast(`Expense posted successfully!`, 'success');
    showExpenseModal.value = false;
    isSubmitting.value = false;

    newExpense.vehicle_id = '';
    newExpense.amount = 0;
  }, 600);
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

/* Mobile Accordion */
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

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
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

.text-white { color: #fff; }

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
