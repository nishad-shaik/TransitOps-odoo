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
      <AlertTriangle class="info-icon-svg" />
      <p><strong>Compliance Rule:</strong> Drivers with an expired license or Suspended status are automatically blocked from trip assignments in the dispatcher.</p>
    </div>

    <!-- Search & Filter Controls -->
    <div class="table-actions">
      <div class="search-box">
        <Search class="search-icon-svg" />
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

    <!-- High-Density Split-Pane Operations Console (Desktop and Tablet Viewports) -->
    <div class="grid grid-cols-1 lg:grid-cols-10 gap-6 mt-4 h-[calc(100vh-210px)] overflow-hidden">
      <!-- Left Column: 40% (4 grid cols) - Scrollable Asset Stream -->
      <div class="lg:col-span-4 flex flex-col h-full overflow-y-auto space-y-3 pr-2 scrollable-stream">
        <div 
          v-for="driver in filteredDrivers" 
          :key="driver.id"
          @click="selectDriver(driver)"
          class="p-4 rounded-lg bg-[#1A1C26] border cursor-pointer transition-all duration-300 ease-in-out hover:translate-y-[-2px] hover:shadow-lg flex flex-col justify-between"
          :class="selectedDriver?.id === driver.id ? 'border-[#2563EB] shadow-lg shadow-blue-500/10' : 'border-[#2D3142]'"
        >
          <div class="flex justify-between items-start mb-2">
            <span class="font-bold text-white text-base">{{ driver.name }}</span>
            <span class="badge" :class="statusBadgeClass(driver.status)">{{ driver.status }}</span>
          </div>
          <div class="flex justify-between items-center text-xs text-[#94A3B8]">
            <span class="font-mono">{{ driver.license_number }}</span>
            <span class="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white font-mono text-[10px] uppercase tracking-widest">{{ driver.license_category }}</span>
          </div>
        </div>
        <div v-if="filteredDrivers.length === 0" class="text-center p-8 text-[#94A3B8] bg-[#1A1C26] rounded-lg border border-[#2D3142]">
          No driver profiles match current filters
        </div>
      </div>

      <!-- Right Column: 60% (6 grid cols) - Deep Inspection Console -->
      <div class="lg:col-span-6 flex flex-col h-full bg-[#1A1C26] border border-[#2D3142] rounded-lg overflow-hidden">
        <div v-if="selectedDriver" class="flex flex-col h-full">
          <!-- Console Header -->
          <div class="p-6 border-b border-[#2D3142] bg-[#1A1C26] flex justify-between items-center">
            <div>
              <span class="text-[10px] uppercase tracking-widest font-mono text-[#2563EB] font-bold">Driver Compliance Record</span>
              <h2 class="text-2xl font-bold text-white font-display mt-0.5">{{ selectedDriver.name }}</h2>
              <p class="text-xs text-[#94A3B8] font-mono tracking-wider">License: {{ selectedDriver.license_number }} ({{ selectedDriver.license_category }})</p>
            </div>
            <button 
              @click="toggleStatus(selectedDriver)" 
              class="btn-primary" 
              :disabled="selectedDriver.status === 'On Trip' || isSubmitting"
            >
              Toggle Duty Status
            </button>
          </div>

          <!-- Console Body / Metadata Grid -->
          <div class="p-6 flex-1 overflow-y-auto space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">Contact Phone</label>
                <span class="font-mono text-lg font-bold text-white">{{ selectedDriver.contact_number }}</span>
              </div>
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">License Expiry</label>
                <span 
                  class="font-mono text-lg font-bold text-white flex items-center gap-1.5"
                  :class="{ 'text-[#FF3B30]': isExpired(selectedDriver.license_expiry_date) }"
                >
                  {{ selectedDriver.license_expiry_date }}
                  <span v-if="isExpired(selectedDriver.license_expiry_date)" class="px-1.5 py-0.5 text-[9px] bg-[#FF3B30]/10 border border-[#FF3B30]/20 rounded text-[#FF3B30] font-bold">EXPIRED</span>
                </span>
              </div>
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">Trip Completion Rate</label>
                <span class="text-lg font-bold text-white tracking-wide">{{ selectedDriver.tripCompletionRate || 100 }}%</span>
              </div>
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">Duty Status</label>
                <span class="badge mt-1 inline-block" :class="statusBadgeClass(selectedDriver.status)">
                  {{ selectedDriver.status }}
                </span>
              </div>
            </div>

            <!-- Horizontal Safety Score Gauge Bar -->
            <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142] space-y-3">
              <div class="flex justify-between items-center text-xs">
                <span class="font-mono text-[#94A3B8] uppercase tracking-widest">Driver Safety Index</span>
                <span class="font-mono font-bold text-white" :class="getSafetyClass(selectedDriver.safety_score)">{{ selectedDriver.safety_score }} / 100</span>
              </div>
              <div class="h-8 w-full bg-[#1A1C26] border border-[#2D3142] rounded overflow-hidden relative flex items-center justify-center">
                <div class="absolute left-0 top-0 h-full bg-[#2563EB] transition-all duration-500 ease-out" :style="{ width: selectedDriver.safety_score + '%' }"></div>
                <span class="absolute text-xs font-mono font-bold text-white z-10">{{ selectedDriver.safety_score }}% DRIVER SCORE RATING</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full text-[#94A3B8] p-8">
          <Info class="h-12 w-12 text-[#2D3142] mb-3" />
          <p class="font-display font-medium text-slate-400">No Driver Selected</p>
          <p class="text-xs text-slate-500 mt-1">Select a driver compliance record from the stream list to inspect compliance stats</p>
        </div>
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
import { ref, computed, reactive, onMounted, watch } from 'vue';
import { AlertTriangle, Info, Search } from '@lucide/vue';
import { useToast } from '../composables/useToast';
import { useApiResource } from '../composables/useApiResource';

const { showToast } = useToast();

const searchQuery = ref('');
const filterStatus = ref('All');
const filterCompliance = ref('All');
const showAddModal = ref(false);
const isSubmitting = ref(false);
const selectedDriver = ref(null);

const { data: apiDrivers, fetch: fetchDrivers, create: createDriver } = useApiResource('/drivers');
const drivers = computed(() => apiDrivers.value || []);

onMounted(() => {
  fetchDrivers();
});

const selectDriver = (d) => {
  selectedDriver.value = d;
};

watch(filteredDrivers, (newVal) => {
  if (newVal && newVal.length > 0) {
    if (!selectedDriver.value || !newVal.some(x => x.id === selectedDriver.value.id)) {
      selectedDriver.value = newVal[0];
    }
  } else {
    selectedDriver.value = null;
  }
}, { immediate: true });

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
  try {
    await createDriver({
      name: String(newDriver.name).trim(),
      license_number: licenseNoCopy,
      license_category: newDriver.license_category,
      license_expiry_date: newDriver.license_expiry_date,
      contact_number: String(newDriver.contact_number).trim(),
      safety_score: Number(newDriver.safety_score)
    });

    showToast(`Driver ${newDriver.name} added successfully!`, 'success');
    showAddModal.value = false;

    // Reset Form
    newDriver.name = '';
    newDriver.license_number = '';
    newDriver.license_expiry_date = '';
    newDriver.contact_number = '';
    newDriver.safety_score = 90;
  } catch (err) {
    showToast(err.message || 'Failed to add driver.', 'error');
  } finally {
    isSubmitting.value = false;
  }
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
