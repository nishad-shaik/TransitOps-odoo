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

    <!-- Drivers Table (Desktop Only: md and above) -->
    <div class="table-card hidden md:block">
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
          <tr v-for="driver in filteredDrivers" :key="driver.id">
            <td class="highlight-text">{{ driver.name }}</td>
            <td class="font-mono">{{ driver.license_number }}</td>
            <td>
              <span class="type-tag">{{ driver.license_category }}</span>
            </td>
            <td>
              <div :class="{ 'text-expired': isExpired(driver.license_expiry_date) }">
                {{ driver.license_expiry_date }}
                <span v-if="isExpired(driver.license_expiry_date)" class="expiry-flag">EXPIRED</span>
              </div>
            </td>
            <td>{{ driver.contact_number }}</td>
            <td class="font-bold">{{ driver.tripCompletionRate }}%</td>
            <td>
              <span class="safety-badge" :class="getSafetyClass(driver.safety_score)">
                {{ driver.safety_score }}/100
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
                :disabled="driver.status === 'On Trip' || isSubmitting"
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

    <!-- Mobile Viewports Accordion Grid (Mobile Layouts: hidden on md and above) -->
    <div class="mobile-accordion-list block md:hidden">
      <div 
        v-for="driver in filteredDrivers" 
        :key="'mobile-dr-' + driver.id" 
        class="card mobile-accordion-card"
        :class="{ expanded: expandedDriverLicenses.includes(driver.license_number) }"
      >
        <!-- Accordion Header: 3 Vital columns only -->
        <div class="accordion-header" @click="toggleDriverAccordion(driver.license_number)">
          <div class="vital-col font-bold text-white">{{ driver.name }}</div>
          <div class="vital-col">
            <span class="badge" :class="statusBadgeClass(driver.status)">
              {{ driver.status }}
            </span>
          </div>
          <div class="vital-col text-right pr-4">
            <span class="safety-badge" :class="getSafetyClass(driver.safety_score)">
              {{ driver.safety_score }}/100
            </span>
          </div>
          <span class="chevron">&#9662;</span>
        </div>

        <!-- Expanded Accordion Content -->
        <div class="accordion-content" v-if="expandedDriverLicenses.includes(driver.license_number)">
          <div class="meta-row">
            <span class="lbl">License No:</span>
            <span class="val font-mono">{{ driver.license_number }}</span>
          </div>
          <div class="meta-row">
            <span class="lbl">Category:</span>
            <span class="val">{{ driver.license_category }}</span>
          </div>
          <div class="meta-row">
            <span class="lbl">Expiry Date:</span>
            <span class="val" :class="{ 'text-expired': isExpired(driver.license_expiry_date) }">
              {{ driver.license_expiry_date }}
              <span v-if="isExpired(driver.license_expiry_date)" class="expiry-flag ml-1">EXPIRED</span>
            </span>
          </div>
          <div class="meta-row">
            <span class="lbl">Contact:</span>
            <span class="val font-mono">{{ driver.contact_number }}</span>
          </div>
          <div class="meta-row">
            <span class="lbl">Trip Completion:</span>
            <span class="val font-bold">{{ driver.tripCompletionRate }}%</span>
          </div>
          <div class="meta-row action-row">
            <button
              @click="toggleStatus(driver)"
              class="btn-sm btn-accent"
              :disabled="driver.status === 'On Trip' || isSubmitting"
            >
              Toggle Status
            </button>
          </div>
        </div>
      </div>
      <div v-if="filteredDrivers.length === 0" class="card empty-row">
        No drivers found matching criteria.
      </div>
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
              <input type="text" v-model="newDriver.license_number" placeholder="e.g. DL-987654" required />
            </div>
            <div class="form-group">
              <label>Category</label>
              <select v-model="newDriver.license_category">
                <option value="Class A">Class A (Heavy Truck)</option>
                <option value="Class B">Class B (Commercial)</option>
                <option value="Class C">Class C (Regular)</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>License Expiry</label>
              <input type="date" v-model="newDriver.license_expiry_date" required />
            </div>
            <div class="form-group">
              <label>Contact Number</label>
              <input type="text" v-model="newDriver.contact_number" placeholder="e.g. +1 555-0199" required />
            </div>
          </div>
          <div class="form-group">
            <label>Initial Safety Score (0-100)</label>
            <input type="number" v-model.number="newDriver.safety_score" min="0" max="100" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Saving...' : 'Save Driver' }}
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

const searchQuery = ref('');
const filterStatus = ref('All');
const filterCompliance = ref('All');
const showAddModal = ref(false);
const isSubmitting = ref(false);
const expandedDriverLicenses = ref([]);

const drivers = ref([
  { id: 1, name: 'Alex Johnson', license_number: 'DL-55291', license_category: 'Class B', license_expiry_date: '2027-08-14', contact_number: '555-0144', tripCompletionRate: 98, safety_score: 92, status: 'Available' },
  { id: 2, name: 'Sarah Connor', license_number: 'DL-88210', license_category: 'Class A', license_expiry_date: '2028-11-20', contact_number: '555-0182', tripCompletionRate: 100, safety_score: 98, status: 'On Trip' },
  { id: 3, name: 'Bruce Wayne', license_number: 'DL-00707', license_category: 'Class C', license_expiry_date: '2026-02-15', contact_number: '555-0199', tripCompletionRate: 94, safety_score: 89, status: 'Available' },
  { id: 4, name: 'Jack Torrance', license_number: 'DL-66611', license_category: 'Class B', license_expiry_date: '2024-05-10', contact_number: '555-0133', tripCompletionRate: 80, safety_score: 45, status: 'Suspended' },
  { id: 5, name: 'Peter Parker', license_number: 'DL-12290', license_category: 'Class C', license_expiry_date: '2028-09-05', contact_number: '555-0121', tripCompletionRate: 99, safety_score: 95, status: 'Off Duty' }
]);

const newDriver = reactive({
  name: '',
  license_number: '',
  license_category: 'Class C',
  license_expiry_date: '',
  contact_number: '',
  tripCompletionRate: 100,
  safety_score: 90,
  status: 'Available'
});

const isExpired = (dateStr) => {
  const expiry = new Date(dateStr);
  const now = new Date('2026-07-12'); // Fixed mock date matching the dynamic alerts anchor
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

const toggleDriverAccordion = (licenseNo) => {
  if (expandedDriverLicenses.value.includes(licenseNo)) {
    expandedDriverLicenses.value = expandedDriverLicenses.value.filter(l => l !== licenseNo);
  } else {
    expandedDriverLicenses.value.push(licenseNo);
  }
};

const filteredDrivers = computed(() => {
  return drivers.value.filter(d => {
    const matchesSearch = d.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          d.license_number.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesStatus = filterStatus.value === 'All' || d.status === filterStatus.value;
    
    let matchesCompliance = true;
    if (filterCompliance.value === 'Valid') {
      matchesCompliance = !isExpired(d.license_expiry_date);
    } else if (filterCompliance.value === 'Expired') {
      matchesCompliance = isExpired(d.license_expiry_date);
    }
    
    return matchesSearch && matchesStatus && matchesCompliance;
  });
});

const toggleStatus = async (driver) => {
  if (driver.status === 'On Trip' || isSubmitting.value) return;
  
  isSubmitting.value = true;
  
  setTimeout(() => {
    if (driver.status === 'Available') {
      driver.status = 'Off Duty';
    } else if (driver.status === 'Off Duty') {
      driver.status = 'Suspended';
    } else if (driver.status === 'Suspended') {
      driver.status = 'Available';
    }
    showToast(`Status toggled for ${driver.name}`, 'info');
    isSubmitting.value = false;
  }, 300);
};

const saveDriver = async () => {
  if (isSubmitting.value) return;

  const licenseNoCopy = String(newDriver.license_number).trim();
  const exists = drivers.value.some(d => d.license_number.toLowerCase() === licenseNoCopy.toLowerCase());
  
  if (exists) {
    showToast('Validation Error: License Number must be unique.', 'error');
    return;
  }

  isSubmitting.value = true;

  setTimeout(() => {
    drivers.value.push({
      id: drivers.value.length + 1,
      name: String(newDriver.name).trim(),
      license_number: licenseNoCopy,
      license_category: newDriver.license_category,
      license_expiry_date: newDriver.license_expiry_date,
      contact_number: String(newDriver.contact_number).trim(),
      tripCompletionRate: 100,
      safety_score: Number(newDriver.safety_score),
      status: 'Available'
    });

    showToast(`Driver ${newDriver.name} added successfully!`, 'success');
    showAddModal.value = false;
    isSubmitting.value = false;

    // Reset Form
    newDriver.name = '';
    newDriver.license_number = '';
    newDriver.license_expiry_date = '';
    newDriver.contact_number = '';
    newDriver.safety_score = 90;
  }, 800);
};
</script>

<script>
export default {
  name: 'Drivers'
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

.font-mono {
  font-family: var(--mono);
}

.font-bold {
  font-weight: 700;
}

.highlight-text {
  color: #fff;
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
  background-color: var(--danger-glow);
  color: var(--danger);
  font-size: 0.7rem;
  padding: 0.1rem 0.35rem;
  border-radius: var(--border-radius-sm);
  font-weight: 800;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.safety-badge {
  font-weight: 700;
  font-size: 0.85rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius-sm);
}

.safety-badge.excellent {
  color: var(--success);
  background-color: var(--success-glow);
}

.safety-badge.good {
  color: var(--info);
  background-color: var(--info-glow);
}

.safety-badge.risk {
  color: var(--danger);
  background-color: var(--danger-glow);
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
