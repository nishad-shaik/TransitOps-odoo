<template>
  <div class="vehicles-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Vehicle Registry</h1>
        <p class="subtitle">Manage company vehicles and operational status</p>
      </div>
      <button @click="showAddModal = true" class="btn-primary">
        <span class="plus-icon">+</span> Add Vehicle
      </button>
    </div>

    <!-- Compliance Banner -->
    <div class="info-banner">
      <Info class="info-icon-svg" />
      <p><strong>Business Rules:</strong> Registration No. must be unique. Retired or In Shop vehicles are automatically filtered out from the Trip Dispatch dispatcher pool.</p>
    </div>

    <!-- Table Action Controls -->
    <div class="table-actions">
      <div class="search-box">
        <Search class="search-icon-svg" />
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

    <!-- Data Table Container (Desktop Only: md and above) -->
    <div class="table-card hidden md:block">
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
          <tr v-for="vehicle in filteredVehicles" :key="vehicle.id">
            <td class="font-mono highlight-text">{{ vehicle.registration_number }}</td>
            <td>{{ vehicle.vehicle_name }}</td>
            <td>
              <span class="type-tag">{{ vehicle.type }}</span>
            </td>
            <td>{{ vehicle.max_load_capacity.toLocaleString() }}</td>
            <td>{{ vehicle.odometer.toLocaleString() }}</td>
            <td>${{ vehicle.acquisition_cost.toLocaleString() }}</td>
            <td>
              <span class="badge" :class="statusBadgeClass(vehicle.status)">
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

    <!-- Mobile Data Condensation List (Mobile Viewports: hidden on md and above) -->
    <div class="mobile-accordion-list block md:hidden">
      <div 
        v-for="vehicle in filteredVehicles" 
        :key="'mobile-' + vehicle.id" 
        class="card mobile-accordion-card"
        :class="{ expanded: expandedRegs.includes(vehicle.registration_number) }"
      >
        <!-- Row Header: 3 Vital columns only -->
        <div class="accordion-header" @click="toggleAccordion(vehicle.registration_number)">
          <div class="vital-col font-mono font-bold text-white">{{ vehicle.registration_number }}</div>
          <div class="vital-col">
            <span class="badge" :class="statusBadgeClass(vehicle.status)">
              {{ vehicle.status }}
            </span>
          </div>
          <div class="vital-col text-right pr-4 font-bold">{{ vehicle.odometer.toLocaleString() }} km</div>
          <span class="chevron">&#9662;</span>
        </div>

        <!-- Expanded Accordion Content -->
        <div class="accordion-content" v-if="expandedRegs.includes(vehicle.registration_number)">
          <div class="meta-row">
            <span class="lbl">Name/Model:</span>
            <span class="val">{{ vehicle.vehicle_name }}</span>
          </div>
          <div class="meta-row">
            <span class="lbl">Type:</span>
            <span class="val">{{ vehicle.type }}</span>
          </div>
          <div class="meta-row">
            <span class="lbl">Max Load Capacity:</span>
            <span class="val font-mono">{{ vehicle.max_load_capacity.toLocaleString() }} kg</span>
          </div>
          <div class="meta-row">
            <span class="lbl">Acquisition Cost:</span>
            <span class="val font-mono">${{ vehicle.acquisition_cost.toLocaleString() }}</span>
          </div>
          <div class="meta-row action-row">
            <button @click="editVehicle(vehicle)" class="btn-sm btn-accent">Edit Vehicle</button>
          </div>
        </div>
      </div>
      <div v-if="filteredVehicles.length === 0" class="card empty-row">
        No vehicles found matching criteria.
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Add New Vehicle</h3>
          <button @click="showAddModal = false" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="saveVehicle">
          <div class="form-group">
            <label>Registration Number</label>
            <input type="text" v-model="newVehicle.registration_number" placeholder="e.g. VAN-05" required />
          </div>
          <div class="form-group">
            <label>Name/Model</label>
            <input type="text" v-model="newVehicle.vehicle_name" placeholder="e.g. Ford Transit 350" required />
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
              <input type="number" v-model.number="newVehicle.max_load_capacity" required />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Odometer Reading (km)</label>
              <input type="number" v-model.number="newVehicle.odometer" required />
            </div>
            <div class="form-group">
              <label>Acquisition Cost ($)</label>
              <input type="number" v-model.number="newVehicle.acquisition_cost" required />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Saving...' : 'Save Vehicle' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';
import { Info, Search } from '@lucide/vue';
import { useToast } from '../composables/useToast';


const { showToast } = useToast();

const searchQuery = ref('');
const filterType = ref('All');
const filterStatus = ref('All');
const showAddModal = ref(false);
const isSubmitting = ref(false);
const expandedRegs = ref([]);

const vehicles = ref([
  { id: 1, registration_number: 'VAN-05', vehicle_name: 'Ford Transit 350', type: 'Van', max_load_capacity: 500, odometer: 12450, acquisition_cost: 35000, status: 'Available' },
  { id: 2, registration_number: 'TRK-02', vehicle_name: 'Volvo FH16 Heavy', type: 'Truck', max_load_capacity: 12000, odometer: 87400, acquisition_cost: 145000, status: 'On Trip' },
  { id: 3, registration_number: 'SDN-01', vehicle_name: 'Toyota Camry hybrid', type: 'Sedan', max_load_capacity: 350, odometer: 32100, acquisition_cost: 28000, status: 'Available' },
  { id: 4, registration_number: 'VAN-02', vehicle_name: 'Mercedes Sprinter Cargo', type: 'Van', max_load_capacity: 800, odometer: 45200, acquisition_cost: 48000, status: 'In Shop' },
  { id: 5, registration_number: 'TRK-01', vehicle_name: 'Scania R500 Flatbed', type: 'Truck', max_load_capacity: 8000, odometer: 112000, acquisition_cost: 120000, status: 'Retired' }
]);

const newVehicle = reactive({
  registration_number: '',
  vehicle_name: '',
  type: 'Van',
  max_load_capacity: 500,
  odometer: 0,
  acquisition_cost: 20000,
  status: 'Available'
});

const toggleAccordion = (regNo) => {
  if (expandedRegs.value.includes(regNo)) {
    expandedRegs.value = expandedRegs.value.filter(r => r !== regNo);
  } else {
    expandedRegs.value.push(regNo);
  }
};

const filteredVehicles = computed(() => {
  return vehicles.value.filter(v => {
    const matchesSearch = v.registration_number.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          v.vehicle_name.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesType = filterType.value === 'All' || v.type === filterType.value;
    const matchesStatus = filterStatus.value === 'All' || v.status === filterStatus.value;
    return matchesSearch && matchesType && matchesStatus;
  });
});

const statusBadgeClass = (status) => {
  if (status === 'Available') return 'badge-success';
  if (status === 'On Trip') return 'badge-info';
  if (status === 'In Shop') return 'badge-warning';
  return 'badge-danger';
};

const saveVehicle = async () => {
  if (isSubmitting.value) return;
  
  // Clone state copies for tamper-resistant validations
  const regNoCopy = String(newVehicle.registration_number).trim();
  const exists = vehicles.value.some(v => v.registration_number.toLowerCase() === regNoCopy.toLowerCase());
  
  if (exists) {
    showToast('Validation Error: Registration Number must be unique.', 'error');
    return;
  }

  isSubmitting.value = true;
  
  // Prevent duplicate submissions and trigger success toast
  setTimeout(() => {
    vehicles.value.push({
      id: vehicles.value.length + 1,
      registration_number: regNoCopy,
      vehicle_name: String(newVehicle.vehicle_name).trim(),
      type: newVehicle.type,
      max_load_capacity: Number(newVehicle.max_load_capacity),
      odometer: Number(newVehicle.odometer),
      acquisition_cost: Number(newVehicle.acquisition_cost),
      status: 'Available'
    });
    
    showToast(`Vehicle ${regNoCopy} added successfully!`, 'success');
    showAddModal.value = false;
    isSubmitting.value = false;

    // Reset Form
    newVehicle.registration_number = '';
    newVehicle.vehicle_name = '';
    newVehicle.max_load_capacity = 500;
    newVehicle.odometer = 0;
    newVehicle.acquisition_cost = 20000;
  }, 800);
};

const editVehicle = (vehicle) => {
  showToast(`Edit record loaded for ${vehicle.registration_number}`, 'info');
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
  font-size: 2.25rem;
  margin: 0;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-top: 0.25rem;
}

.plus-icon {
  margin-right: 0.25rem;
  font-weight: 700;
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

.table-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
}

.search-box input {
  padding-left: 2.75rem;
  width: 320px;
}

.filter-group {
  display: flex;
  gap: 0.75rem;
}

.filter-group select {
  width: auto;
  cursor: pointer;
}

.font-mono {
  font-family: var(--mono);
}

.highlight-text {
  font-weight: 700;
  color: #fff;
}

.type-tag {
  background-color: var(--border-color);
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
  color: var(--text-primary);
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

.empty-row {
  color: var(--text-secondary);
  padding: 3rem;
  text-align: center;
}

/* Mobile Accordion details */
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

.action-row {
  margin-top: 0.5rem;
  justify-content: flex-end;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Modal Styling Extensions */
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
</style>
