<template>
  <div class="vehicles-container">
    <div class="page-header">
      <div>
        <h1>Vehicle Registry</h1>
        <p class="subtitle">Manage company vehicles and operational status</p>
      </div>
      <button @click="showAddModal = true" class="btn-primary">+ Add Vehicle</button>
    </div>

    <!-- Info message mapping to evaluation business rules -->
    <div class="info-banner">
      <span class="info-icon">ℹ</span>
      <p><strong>Business Rules:</strong> Registration No. must be unique. Retired or In Shop vehicles are automatically filtered out from the Trip Dispatch dispatcher pool.</p>
    </div>

    <!-- Filters & Search -->
    <div class="table-actions">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search by Registration No. or Model..."
        />
      </div>
      <div class="filter-group">
        <select v-model="filterType">
          <option value="All">All Types</option>
          <option value="Truck">Truck</option>
          <option value="Van">Van</option>
          <option value="Sedan">Sedan</option>
        </select>
        <select v-model="filterStatus">
          <option value="All">All Statuses</option>
          <option value="Available">Available</option>
          <option value="On Trip">On Trip</option>
          <option value="In Shop">In Shop</option>
          <option value="Retired">Retired</option>
        </select>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Reg. No.</th>
            <th>Name/Model</th>
            <th>Type</th>
            <th>Max Load (kg)</th>
            <th>Odometer (km)</th>
            <th>Acquisition Cost</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="vehicle in filteredVehicles" :key="vehicle.regNo">
            <td class="font-mono">{{ vehicle.regNo }}</td>
            <td>{{ vehicle.model }}</td>
            <td>{{ vehicle.type }}</td>
            <td>{{ vehicle.maxLoad.toLocaleString() }}</td>
            <td>{{ vehicle.odometer.toLocaleString() }}</td>
            <td>${{ vehicle.acquisitionCost.toLocaleString() }}</td>
            <td>
              <span class="status-badge" :class="vehicle.status.toLowerCase().replace(' ', '-')">
                {{ vehicle.status }}
              </span>
            </td>
            <td>
              <button @click="editVehicle(vehicle)" class="btn-text">Edit</button>
            </td>
          </tr>
          <tr v-if="filteredVehicles.length === 0">
            <td colspan="8" class="text-center empty-row">No vehicles found matching criteria.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Vehicle Modal (Placeholder) -->
    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal">
        <h3>Add New Vehicle</h3>
        <form @submit.prevent="saveVehicle">
          <div class="form-group">
            <label>Registration Number</label>
            <input type="text" v-model="newVehicle.regNo" placeholder="e.g. TN-05-A-1234" required />
          </div>
          <div class="form-group">
            <label>Name/Model</label>
            <input type="text" v-model="newVehicle.model" placeholder="e.g. Ford Transit" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Type</label>
              <select v-model="newVehicle.type">
                <option value="Van">Van</option>
                <option value="Truck">Truck</option>
                <option value="Sedan">Sedan</option>
              </select>
            </div>
            <div class="form-group">
              <label>Max Load Capacity (kg)</label>
              <input type="number" v-model.number="newVehicle.maxLoad" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Odometer Reading (km)</label>
              <input type="number" v-model.number="newVehicle.odometer" required />
            </div>
            <div class="form-group">
              <label>Acquisition Cost ($)</label>
              <input type="number" v-model.number="newVehicle.acquisitionCost" required />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">Save Vehicle</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';

const searchQuery = ref('');
const filterType = ref('All');
const filterStatus = ref('All');
const showAddModal = ref(false);

const vehicles = ref([
  { regNo: 'VAN-05', model: 'Ford Transit 350', type: 'Van', maxLoad: 500, odometer: 12450, acquisitionCost: 35000, status: 'Available' },
  { regNo: 'TRK-02', model: 'Volvo FH16 Heavy', type: 'Truck', maxLoad: 12000, odometer: 87400, acquisitionCost: 145000, status: 'On Trip' },
  { regNo: 'SDN-01', model: 'Toyota Camry hybrid', type: 'Sedan', maxLoad: 350, odometer: 32100, acquisitionCost: 28000, status: 'Available' },
  { regNo: 'VAN-02', model: 'Mercedes Sprinter Cargo', type: 'Van', maxLoad: 800, odometer: 45200, acquisitionCost: 48000, status: 'In Shop' },
  { regNo: 'TRK-01', model: 'Scania R500 Flatbed', type: 'Truck', maxLoad: 8000, odometer: 112000, acquisitionCost: 120000, status: 'Retired' }
]);

const newVehicle = reactive({
  regNo: '',
  model: '',
  type: 'Van',
  maxLoad: 500,
  odometer: 0,
  acquisitionCost: 20000,
  status: 'Available'
});

const filteredVehicles = computed(() => {
  return vehicles.value.filter(v => {
    const matchesSearch = v.regNo.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          v.model.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesType = filterType.value === 'All' || v.type === filterType.value;
    const matchesStatus = filterStatus.value === 'All' || v.status === filterStatus.value;
    return matchesSearch && matchesType && matchesStatus;
  });
});

const saveVehicle = () => {
  // Check unique registration number constraint
  const exists = vehicles.value.some(v => v.regNo.toLowerCase() === newVehicle.regNo.toLowerCase());
  if (exists) {
    alert('Registration No. must be unique');
    return;
  }
  
  vehicles.value.push({ ...newVehicle });
  showAddModal.value = false;
  // Reset fields
  newVehicle.regNo = '';
  newVehicle.model = '';
  newVehicle.maxLoad = 500;
  newVehicle.odometer = 0;
  newVehicle.acquisitionCost = 20000;
};

const editVehicle = (vehicle) => {
  alert(`Edit layout for ${vehicle.regNo} will be loaded here.`);
};
</script>

<style scoped>
.vehicles-container {
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

.info-banner {
  background-color: rgba(170, 59, 255, 0.05);
  border: 1px solid rgba(170, 59, 255, 0.2);
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  font-size: 0.85rem;
  color: var(--text-h);
}

.info-banner p {
  margin: 0;
}

.info-icon {
  color: var(--accent);
  font-weight: bold;
}

.table-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box input {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  width: 300px;
  background-color: var(--bg);
  color: var(--text-h);
  outline: none;
}

.search-box input:focus {
  border-color: var(--accent);
}

.filter-group {
  display: flex;
  gap: 1rem;
}

.filter-group select {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  background-color: var(--bg);
  color: var(--text-h);
  font-size: 0.9rem;
}

.table-card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  overflow-x: auto;
  box-shadow: var(--shadow);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--border);
}

.data-table th {
  color: var(--text);
  font-weight: 600;
  background-color: var(--social-bg);
}

.data-table td {
  color: var(--text-h);
}

.font-mono {
  font-family: var(--mono);
  font-weight: 600;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.status-badge.available {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.on-trip {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.in-shop {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.retired {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
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

.btn-text {
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-weight: 600;
}

.empty-row {
  color: var(--text);
  padding: 2rem;
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
</style>
