<template>
  <div class="drivers-container">
    <div class="page-header">
      <div>
        <h1>Drivers &amp; Safety</h1>
        <p class="subtitle">Manage driver records, licensing compliance, and safety ratings</p>
      </div>
      <button @click="showAddModal = true" class="btn-primary">+ Add Driver</button>
    </div>

    <!-- Info banner containing safety and licensing business rules -->
    <div class="info-banner warning-style">
      <span class="info-icon">⚠️</span>
      <p><strong>Compliance Rule:</strong> Drivers with an expired license or Suspended status are automatically blocked from trip assignments in the dispatcher.</p>
    </div>

    <!-- Search & Filter Controls -->
    <div class="table-actions">
      <div class="search-box">
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
            <td class="font-bold">{{ driver.name }}</td>
            <td class="font-mono">{{ driver.licenseNo }}</td>
            <td>{{ driver.category }}</td>
            <td :class="{ 'text-expired': isExpired(driver.expiryDate) }">
              {{ driver.expiryDate }}
              <span v-if="isExpired(driver.expiryDate)" class="expiry-flag">[EXPIRED]</span>
            </td>
            <td>{{ driver.contact }}</td>
            <td>{{ driver.tripCompletionRate }}%</td>
            <td>
              <span class="safety-score" :class="getSafetyClass(driver.safetyScore)">
                {{ driver.safetyScore }}/100
              </span>
            </td>
            <td>
              <span class="status-badge" :class="driver.status.toLowerCase().replace(' ', '-')">
                {{ driver.status }}
              </span>
            </td>
            <td>
              <div class="actions-cell">
                <button
                  @click="toggleStatus(driver)"
                  class="btn-text"
                  :disabled="driver.status === 'On Trip'"
                >
                  Toggle Status
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredDrivers.length === 0">
            <td colspan="9" class="text-center empty-row">No drivers found matching criteria.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Driver Modal -->
    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal">
        <h3>Add New Driver</h3>
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
  // Check unique license number constraint
  const exists = drivers.value.some(d => d.licenseNo.toLowerCase() === newDriver.licenseNo.toLowerCase());
  if (exists) {
    alert('License Number must be unique');
    return;
  }

  drivers.value.push({ ...newDriver });
  showAddModal.value = false;
  // Reset
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
  background-color: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.2);
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

.font-bold {
  font-weight: 600;
}

.font-mono {
  font-family: var(--mono);
}

.text-expired {
  color: #ef4444;
  font-weight: 600;
}

.expiry-flag {
  font-size: 0.75rem;
  margin-left: 0.25rem;
  background-color: rgba(239, 68, 68, 0.1);
  padding: 0.1rem 0.3rem;
  border-radius: 0.25rem;
}

.safety-score {
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  font-weight: 600;
}

.safety-score.excellent {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.safety-score.good {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.safety-score.risk {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
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

.status-badge.off-duty {
  background-color: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.status-badge.suspended {
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

.btn-text:disabled {
  color: var(--text);
  opacity: 0.5;
  cursor: not-allowed;
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
