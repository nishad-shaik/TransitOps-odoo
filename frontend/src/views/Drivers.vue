<template>
  <div class="drivers-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Drivers &amp; Safety</h1>
        <p class="subtitle">Manage driver records, licensing compliance, and safety ratings</p>
      </div>
      <button @click="showAddModal = true" class="btn-primary">
        <span>+</span> Add Driver
      </button>
    </div>

    <!-- Compliance Banner -->
    <div class="info-banner warning-style">
      <span class="info-icon">⚠️</span>
      <p><strong>Compliance Rule:</strong> Drivers with an expired license or Suspended status are automatically blocked from trip assignments in the dispatcher.</p>
    </div>

    <!-- Search & Filter Controls -->
    <div class="table-actions">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search by Driver Name or License No..."
        />
      </div>
      <div class="filter-group">
        <select v-model="filterStatus">
          <option value="All">All Statuses</option>
          <option value="Available">Available</option>
          <option value="On Trip">On Trip</option>
          <option value="Off Duty">Off Duty</option>
          <option value="Suspended">Suspended</option>
        </select>
        <select v-model="filterCompliance">
          <option value="All">All Compliance</option>
          <option value="Valid">Valid License</option>
          <option value="Expired">Expired License</option>
        </select>
      </div>
    </div>

    <!-- Drivers Table -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Driver Name</th>
            <th>License No.</th>
            <th>Category</th>
            <th>Expiry Date</th>
            <th>Contact</th>
            <th>Trip Compl. %</th>
            <th>Safety Score</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="driver in filteredDrivers" :key="driver.licenseNo">
            <td class="highlight-text">{{ driver.name }}</td>
            <td class="font-mono">{{ driver.licenseNo }}</td>
            <td>
              <span class="type-tag">{{ driver.category }}</span>
            </td>
            <td>
              <div :class="{ 'text-expired': isExpired(driver.expiryDate) }">
                {{ driver.expiryDate }}
                <span v-if="isExpired(driver.expiryDate)" class="expiry-flag">EXPIRED</span>
              </div>
            </td>
            <td>{{ driver.contact }}</td>
            <td class="font-bold">{{ driver.tripCompletionRate }}%</td>
            <td>
              <span class="safety-badge" :class="getSafetyClass(driver.safetyScore)">
                {{ driver.safetyScore }}/100
              </span>
            </td>
            <td>
              <span class="badge" :class="statusBadgeClass(driver.status)">
                {{ driver.status }}
              </span>
            </td>
            <td>
              <button
                @click="toggleStatus(driver)"
                class="btn-text"
                :disabled="driver.status === 'On Trip'"
              >
                Toggle Status
              </button>
            </td>
          </tr>
          <tr v-if="filteredDrivers.length === 0">
            <td colspan="9" class="text-center empty-row">No drivers found matching criteria.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Driver Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Add New Driver</h3>
          <button @click="showAddModal = false" class="close-btn">&times;</button>
        </div>
        <form @submit.prevent="saveDriver">
          <div class="form-group">
            <label>Driver Name</label>
            <input type="text" v-model="newDriver.name" placeholder="e.g. John Doe" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>License Number</label>
              <input type="text" v-model="newDriver.licenseNo" placeholder="e.g. DL-987654" required />
            </div>
            <div class="form-group">
              <label>Category</label>
              <select v-model="newDriver.category">
                <option value="Class A">Class A (Heavy Truck)</option>
                <option value="Class B">Class B (Commercial)</option>
                <option value="Class C">Class C (Regular)</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>License Expiry</label>
              <input type="date" v-model="newDriver.expiryDate" required />
            </div>
            <div class="form-group">
              <label>Contact Number</label>
              <input type="text" v-model="newDriver.contact" placeholder="e.g. +1 555-0199" required />
            </div>
          </div>
          <div class="form-group">
            <label>Initial Safety Score (0-100)</label>
            <input type="number" v-model.number="newDriver.safetyScore" min="0" max="100" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">Save Driver</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue';

const searchQuery = ref('');
const filterStatus = ref('All');
const filterCompliance = ref('All');
const showAddModal = ref(false);

const drivers = ref([
  { name: 'Alex Johnson', licenseNo: 'DL-55291', category: 'Class B', expiryDate: '2027-08-14', contact: '555-0144', tripCompletionRate: 98, safetyScore: 92, status: 'Available' },
  { name: 'Sarah Connor', licenseNo: 'DL-88210', category: 'Class A', expiryDate: '2028-11-20', contact: '555-0182', tripCompletionRate: 100, safetyScore: 98, status: 'On Trip' },
  { name: 'Bruce Wayne', licenseNo: 'DL-00707', category: 'Class C', expiryDate: '2026-02-15', contact: '555-0199', tripCompletionRate: 94, safetyScore: 89, status: 'Available' },
  { name: 'Jack Torrance', licenseNo: 'DL-66611', category: 'Class B', expiryDate: '2024-05-10', contact: '555-0133', tripCompletionRate: 80, safetyScore: 45, status: 'Suspended' },
  { name: 'Peter Parker', licenseNo: 'DL-12290', category: 'Class C', expiryDate: '2028-09-05', contact: '555-0121', tripCompletionRate: 99, safetyScore: 95, status: 'Off Duty' }
]);

const newDriver = reactive({
  name: '',
  licenseNo: '',
  category: 'Class C',
  expiryDate: '',
  contact: '',
  tripCompletionRate: 100,
  safetyScore: 90,
  status: 'Available'
});

const isExpired = (dateStr) => {
  const expiry = new Date(dateStr);
  const now = new Date();
  return expiry < now;
};

const getSafetyClass = (score) => {
  if (score >= 90) return 'excellent';
  if (score >= 70) return 'good';
  return 'risk';
};

const statusBadgeClass = (status) => {
  if (status === 'Available') return 'badge-success';
  if (status === 'On Trip') return 'badge-info';
  if (status === 'Off Duty') return 'badge-warning';
  return 'badge-danger';
};

const filteredDrivers = computed(() => {
  return drivers.value.filter(d => {
    const matchesSearch = d.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          d.licenseNo.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesStatus = filterStatus.value === 'All' || d.status === filterStatus.value;
    
    let matchesCompliance = true;
    if (filterCompliance.value === 'Valid') {
      matchesCompliance = !isExpired(d.expiryDate);
    } else if (filterCompliance.value === 'Expired') {
      matchesCompliance = isExpired(d.expiryDate);
    }
    
    return matchesSearch && matchesStatus && matchesCompliance;
  });
});

const toggleStatus = (driver) => {
  if (driver.status === 'On Trip') return;
  
  if (driver.status === 'Available') {
    driver.status = 'Off Duty';
  } else if (driver.status === 'Off Duty') {
    driver.status = 'Suspended';
  } else if (driver.status === 'Suspended') {
    driver.status = 'Available';
  }
};

const saveDriver = () => {
  const exists = drivers.value.some(d => d.licenseNo.toLowerCase() === newDriver.licenseNo.toLowerCase());
  if (exists) {
    alert('License Number must be unique');
    return;
  }

  drivers.value.push({ ...newDriver });
  showAddModal.value = false;
  newDriver.name = '';
  newDriver.licenseNo = '';
  newDriver.expiryDate = '';
  newDriver.contact = '';
  newDriver.safetyScore = 90;
};
</script>

<style scoped>
.drivers-container {
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

.warning-style {
  background-color: var(--warning-glow);
  border: 1px solid rgba(245, 158, 11, 0.15);
  padding: 1rem 1.25rem;
  border-radius: var(--border-radius-md);
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.9rem;
}

.info-icon {
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

.highlight-text {
  font-weight: 700;
  color: #fff;
}

.font-mono {
  font-family: var(--mono);
}

.font-bold {
  font-weight: 700;
}

.type-tag {
  background-color: var(--border-color);
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
  color: var(--text-primary);
}

.text-expired {
  color: var(--danger);
  font-weight: 700;
}

.expiry-flag {
  font-size: 0.7rem;
  margin-left: 0.35rem;
  background-color: var(--danger-glow);
  color: var(--danger);
  padding: 0.15rem 0.4rem;
  border-radius: var(--border-radius-sm);
  font-weight: 700;
}

.safety-badge {
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-weight: 700;
  font-size: 0.85rem;
}

.safety-badge.excellent {
  background-color: var(--success-glow);
  color: var(--success);
}

.safety-badge.good {
  background-color: var(--info-glow);
  color: var(--info);
}

.safety-badge.risk {
  background-color: var(--danger-glow);
  color: var(--danger);
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

.btn-text:disabled {
  color: var(--text-muted);
  cursor: not-allowed;
}

.empty-row {
  color: var(--text-secondary);
  padding: 3rem;
  text-align: center;
}

/* Modal Extensions */
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
