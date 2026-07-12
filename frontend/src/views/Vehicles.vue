<template>
  <div class="vehicles-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Vehicle Registry</h1>
        <p class="subtitle">Manage company vehicles and operational status</p>
      </div>
      <button @click="openAddDrawer" class="btn-primary">
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

    <!-- High-Density Split-Pane Operations Console (Desktop and Tablet Viewports) -->
    <div class="grid grid-cols-1 lg:grid-cols-10 gap-6 mt-4 h-[calc(100vh-210px)] overflow-hidden">
      <!-- Left Column: 40% (4 grid cols) - Scrollable Asset Stream -->
      <div class="lg:col-span-4 flex flex-col h-full overflow-y-auto space-y-3 pr-2 scrollable-stream">
        <div 
          v-for="vehicle in filteredVehicles" 
          :key="vehicle.id"
          @click="selectVehicle(vehicle)"
          class="p-4 rounded-lg bg-[#1A1C26] border cursor-pointer transition-all duration-300 ease-in-out hover:translate-y-[-2px] hover:shadow-lg flex flex-col justify-between"
          :class="selectedVehicle?.id === vehicle.id ? 'border-[#2563EB] shadow-lg shadow-blue-500/10' : 'border-[#2D3142]'"
        >
          <div class="flex justify-between items-start mb-2">
            <span class="font-mono font-bold text-white text-base tracking-wider">{{ vehicle.registration_number }}</span>
            <span class="badge" :class="statusBadgeClass(vehicle.status)">{{ vehicle.status }}</span>
          </div>
          <div class="flex justify-between items-center text-xs text-[#94A3B8]">
            <span class="font-medium text-slate-300">{{ vehicle.vehicle_name }}</span>
            <span class="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white font-mono text-[10px] uppercase tracking-widest">{{ vehicle.type }}</span>
          </div>
        </div>
        <div v-if="filteredVehicles.length === 0" class="text-center p-8 text-[#94A3B8] bg-[#1A1C26] rounded-lg border border-[#2D3142]">
          No vehicle assets match current filters
        </div>
      </div>

      <!-- Right Column: 60% (6 grid cols) - Deep Inspection Console -->
      <div class="lg:col-span-6 flex flex-col h-full bg-[#1A1C26] border border-[#2D3142] rounded-lg overflow-hidden">
        <div v-if="selectedVehicle" class="flex flex-col h-full">
          <!-- Console Header -->
          <div class="p-6 border-b border-[#2D3142] bg-[#1A1C26] flex justify-between items-center">
            <div>
              <span class="text-[10px] uppercase tracking-widest font-mono text-[#2563EB] font-bold">Logistics Asset Profile</span>
              <h2 class="text-2xl font-bold text-white font-display mt-0.5">{{ selectedVehicle.vehicle_name }}</h2>
              <p class="text-xs text-[#94A3B8] font-mono tracking-wider">{{ selectedVehicle.registration_number }}</p>
            </div>
            <button @click.stop="openVehicleDrawer(selectedVehicle)" class="btn-primary flex items-center gap-1.5">
              <span>Edit Asset</span>
            </button>
          </div>

          <!-- Console Body / Metadata Grid -->
          <div class="p-6 flex-1 overflow-y-auto space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">Current Odometer</label>
                <span class="font-mono text-lg font-bold text-white">{{ selectedVehicle.odometer.toLocaleString() }} km</span>
              </div>
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">Acquisition Cost</label>
                <span class="font-mono text-lg font-bold text-white">${{ selectedVehicle.acquisition_cost.toLocaleString() }}</span>
              </div>
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">Asset Class / Type</label>
                <span class="text-lg font-bold text-white tracking-wide">{{ selectedVehicle.type }}</span>
              </div>
              <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142]">
                <label class="block text-[10px] font-semibold text-[#94A3B8] uppercase tracking-widest mb-1 font-mono">Operational Status</label>
                <span class="badge mt-1 inline-block" :class="statusBadgeClass(selectedVehicle.status)">
                  {{ selectedVehicle.status }}
                </span>
              </div>
            </div>

            <!-- Horizontal Capacity Progress Column -->
            <div class="p-4 rounded-lg bg-[#12131C] border border-[#2D3142] space-y-3">
              <div class="flex justify-between items-center text-xs">
                <span class="font-mono text-[#94A3B8] uppercase tracking-widest">Payload Carrying Capacity</span>
                <span class="font-mono font-bold text-white">{{ selectedVehicle.max_load_capacity.toLocaleString() }} kg Max</span>
              </div>
              <div class="h-8 w-full bg-[#1A1C26] border border-[#2D3142] rounded overflow-hidden relative flex items-center justify-center">
                <div class="absolute left-0 top-0 h-full bg-[#2563EB]" style="width: 100%"></div>
                <span class="absolute text-xs font-mono font-bold text-white z-10">100% CAPACITY BLOCK DESIGN LIMIT</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full text-[#94A3B8] p-8">
          <Info class="h-12 w-12 text-[#2D3142] mb-3" />
          <p class="font-display font-medium text-slate-400">No Asset Selected</p>
          <p class="text-xs text-slate-500 mt-1">Select a logistics vehicle from the stream view to inspect telemetry</p>
        </div>
      </div>
    </div>

    <!-- Right-Hand Sliding Glassmorphic Side Drawer -->
    <div 
      class="fixed top-0 right-0 h-full w-full max-w-[460px] bg-[#161B26]/90 backdrop-blur-lg border-l border-white/10 z-[999] shadow-2xl flex flex-col transition-all duration-300 ease-in-out"
      :class="showAddModal ? 'translate-x-0' : 'translate-x-full'"
    >
      <div class="p-6 border-b border-white/5 flex justify-between items-center bg-[#0B0F19]/30">
        <h3 class="text-xl font-bold text-white">
          {{ isEditing ? 'Edit Vehicle specifications' : 'Register New Vehicle' }}
        </h3>
        <button @click="showAddModal = false" class="text-2xl text-slate-400 hover:text-white transition">&times;</button>
      </div>
      
      <form @submit.prevent="saveVehicle" class="flex-1 overflow-y-auto p-6 space-y-5">
        <div class="space-y-1">
          <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Registration Number</label>
          <input 
            type="text" 
            v-model="newVehicle.registration_number" 
            placeholder="e.g. VAN-05" 
            required 
            class="bg-[#1E2533] border border-white/10 text-white rounded px-4 py-3 w-full focus:border-cyan-500 transition outline-none font-mono"
            :disabled="isEditing"
          />
        </div>
        
        <div class="space-y-1">
          <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Vehicle Name / Model</label>
          <input 
            type="text" 
            v-model="newVehicle.vehicle_name" 
            placeholder="e.g. Ford Transit 350" 
            required 
            class="bg-[#1E2533] border border-white/10 text-white rounded px-4 py-3 w-full focus:border-cyan-500 transition outline-none"
          />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Type</label>
            <select 
              v-model="newVehicle.type" 
              class="bg-[#1E2533] border border-white/10 text-white rounded px-4 py-3 w-full focus:border-cyan-500 transition outline-none"
            >
              <option value="Van">Van</option>
              <option value="Truck">Truck</option>
              <option value="Sedan">Sedan</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Max Load (kg)</label>
            <input 
              type="number" 
              v-model.number="newVehicle.max_load_capacity" 
              required 
              class="bg-[#1E2533] border border-white/10 text-white rounded px-4 py-3 w-full focus:border-cyan-500 transition outline-none font-mono"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Odometer (km)</label>
            <input 
              type="number" 
              v-model.number="newVehicle.odometer" 
              required 
              class="bg-[#1E2533] border border-white/10 text-white rounded px-4 py-3 w-full focus:border-cyan-500 transition outline-none font-mono"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Acquisition Cost ($)</label>
            <input 
              type="number" 
              v-model.number="newVehicle.acquisition_cost" 
              required 
              class="bg-[#1E2533] border border-white/10 text-white rounded px-4 py-3 w-full focus:border-cyan-500 transition outline-none font-mono"
            />
          </div>
        </div>

        <div class="space-y-1" v-if="isEditing">
          <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</label>
          <select 
            v-model="newVehicle.status" 
            class="bg-[#1E2533] border border-white/10 text-white rounded px-4 py-3 w-full focus:border-cyan-500 transition outline-none"
          >
            <option value="Available">Available</option>
            <option value="On Trip">On Trip</option>
            <option value="In Shop">In Shop</option>
            <option value="Retired">Retired</option>
          </select>
        </div>

        <div class="pt-6 flex gap-4">
          <button 
            type="button" 
            @click="showAddModal = false" 
            class="flex-1 px-4 py-3 bg-white/5 hover:bg-white/10 text-white rounded font-bold transition"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            class="flex-1 px-4 py-3 bg-cyan-500 hover:bg-cyan-600 text-slate-900 rounded font-bold transition shadow-lg"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Saving...' : 'Save specifications' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue';
import { Info, Search } from '@lucide/vue';
import { useToast } from '../composables/useToast';
import { useApiResource } from '../composables/useApiResource';
import { client } from '../api/client';

const { showToast } = useToast();

const searchQuery = ref('');
const filterType = ref('All');
const filterStatus = ref('All');
const showAddModal = ref(false);
const isSubmitting = ref(false);
const isEditing = ref(false);
const selectedVehicle = ref(null);

const { data: apiVehicles, fetch: fetchVehicles, create: createVehicle } = useApiResource('/vehicles');
const vehicles = computed(() => apiVehicles.value || []);

onMounted(() => {
  fetchVehicles();
});

const selectVehicle = (v) => {
  selectedVehicle.value = v;
};

watch(filteredVehicles, (newVal) => {
  if (newVal && newVal.length > 0) {
    if (!selectedVehicle.value || !newVal.some(x => x.id === selectedVehicle.value.id)) {
      selectedVehicle.value = newVal[0];
    }
  } else {
    selectedVehicle.value = null;
  }
}, { immediate: true });

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

const openVehicleDrawer = (vehicle) => {
  isEditing.value = true;
  newVehicle.registration_number = vehicle.registration_number;
  newVehicle.vehicle_name = vehicle.vehicle_name;
  newVehicle.type = vehicle.type;
  newVehicle.max_load_capacity = vehicle.max_load_capacity;
  newVehicle.odometer = vehicle.odometer;
  newVehicle.acquisition_cost = vehicle.acquisition_cost;
  newVehicle.status = vehicle.status;
  showAddModal.value = true;
};

const openAddDrawer = () => {
  isEditing.value = false;
  newVehicle.registration_number = '';
  newVehicle.vehicle_name = '';
  newVehicle.type = 'Van';
  newVehicle.max_load_capacity = 500;
  newVehicle.odometer = 0;
  newVehicle.acquisition_cost = 20000;
  newVehicle.status = 'Available';
  showAddModal.value = true;
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
  
  const regNoCopy = String(newVehicle.registration_number).trim();
  
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      // Execute live PATCH to the backend update route
      await client.patch(`/vehicles/${regNoCopy}`, {
        vehicle_name: String(newVehicle.vehicle_name).trim(),
        type: newVehicle.type,
        max_load_capacity: Number(newVehicle.max_load_capacity),
        odometer: Number(newVehicle.odometer),
        acquisition_cost: Number(newVehicle.acquisition_cost),
        status: newVehicle.status
      });
      showToast(`Vehicle ${regNoCopy} specifications updated!`, 'success');
    } else {
      const exists = vehicles.value.some(v => v.registration_number.toLowerCase() === regNoCopy.toLowerCase());
      if (exists) {
        showToast('Validation Error: Registration Number must be unique.', 'error');
        isSubmitting.value = false;
        return;
      }
      await createVehicle({
        registration_number: regNoCopy,
        vehicle_name: String(newVehicle.vehicle_name).trim(),
        type: newVehicle.type,
        max_load_capacity: Number(newVehicle.max_load_capacity),
        odometer: Number(newVehicle.odometer),
        acquisition_cost: Number(newVehicle.acquisition_cost)
      });
      showToast(`Vehicle ${regNoCopy} registered successfully!`, 'success');
    }
    
    await fetchVehicles();
    showAddModal.value = false;
  } catch (err) {
    showToast(err.message || 'Failed to save vehicle details.', 'error');
  } finally {
    isSubmitting.value = false;
  }
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
