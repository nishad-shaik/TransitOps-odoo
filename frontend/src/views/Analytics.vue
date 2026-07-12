<template>
  <div class="analytics-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Financial Analytics</h1>
        <p class="subtitle">Vehicle performance, ROI analysis, and CSV export portal</p>
      </div>
      <button @click="downloadCSV" class="btn-primary flex-btn">
        <span>📥 Export Grid to CSV</span>
      </button>
    </div>

    <!-- Derived Metrics Cards -->
    <div class="kpi-grid">
      <!-- Operational Costs -->
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-icon">💳</span>
          <span class="kpi-label">Fleet Operational Costs</span>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">${{ totalOperationalCost.toLocaleString() }}</span>
          <span class="kpi-subtext">Sum of maintenance ($14,500) + fuel ($18,200)</span>
        </div>
        <div class="kpi-border"></div>
      </div>

      <!-- Fuel Efficiency Summary -->
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-icon">⚡</span>
          <span class="kpi-label">Avg Fuel Efficiency</span>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">8.9 km/L</span>
          <span class="kpi-subtext">Optimal range target is 10.0+ km/L</span>
        </div>
        <div class="kpi-border"></div>
      </div>

      <!-- Average ROI Card -->
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-icon">📈</span>
          <span class="kpi-label">Fleet Average ROI</span>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">{{ averageRoi }}%</span>
          <span class="kpi-subtext">Formula: (Rev - (Maint + Fuel)) / Acq</span>
        </div>
        <div class="kpi-border"></div>
      </div>
    </div>

    <!-- Filters Control Panel -->
    <div class="card filters-card">
      <div class="search-bar-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search by Vehicle Reg No (e.g. TRK-02)..." 
          class="search-input"
        />
      </div>

      <!-- Multi-select Filter Popovers -->
      <div class="filter-dropdowns">
        <!-- Type Filter -->
        <div class="dropdown-wrapper">
          <button @click="toggleDropdown('type')" class="btn-dropdown">
            Type ({{ selectedTypes.length || 'All' }})
            <span class="arrow">&#9662;</span>
          </button>
          <div class="dropdown-menu" v-if="activeDropdown === 'type'">
            <label class="checkbox-label" v-for="t in typeOptions" :key="t">
              <input type="checkbox" :value="t" v-model="selectedTypes" />
              <span>{{ t }}</span>
            </label>
          </div>
        </div>

        <!-- Status Filter -->
        <div class="dropdown-wrapper">
          <button @click="toggleDropdown('status')" class="btn-dropdown">
            Status ({{ selectedStatuses.length || 'All' }})
            <span class="arrow">&#9662;</span>
          </button>
          <div class="dropdown-menu" v-if="activeDropdown === 'status'">
            <label class="checkbox-label" v-for="s in statusOptions" :key="s">
              <input type="checkbox" :value="s" v-model="selectedStatuses" />
              <span>{{ s }}</span>
            </label>
          </div>
        </div>

        <!-- Region Filter -->
        <div class="dropdown-wrapper">
          <button @click="toggleDropdown('region')" class="btn-dropdown">
            Region ({{ selectedRegions.length || 'All' }})
            <span class="arrow">&#9662;</span>
          </button>
          <div class="dropdown-menu" v-if="activeDropdown === 'region'">
            <label class="checkbox-label" v-for="r in regionOptions" :key="r">
              <input type="checkbox" :value="r" v-model="selectedRegions" />
              <span>{{ r }}</span>
            </label>
          </div>
        </div>

        <!-- Reset Button -->
        <button @click="clearFilters" class="btn-secondary btn-reset" v-if="hasActiveFilters">
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Data Grid Framework Table -->
    <div class="card grid-card">
      <div class="grid-header">
        <h3>Vehicle ROI Financial Matrix</h3>
        <span class="row-count">Records: {{ filteredRoiData.length }}</span>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Type</th>
              <th>Region</th>
              <th>Revenue</th>
              <th>Maintenance</th>
              <th>Fuel</th>
              <th>Acquisition</th>
              <th>Calculated ROI</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in filteredRoiData" :key="v.regNo">
              <td class="font-bold highlight-text font-mono">{{ v.regNo }}</td>
              <td>{{ v.type }}</td>
              <td>{{ v.region }}</td>
              <td>${{ v.revenue.toLocaleString() }}</td>
              <td>${{ v.maintenance.toLocaleString() }}</td>
              <td>${{ v.fuel.toLocaleString() }}</td>
              <td>${{ v.acqCost.toLocaleString() }}</td>
              <td class="font-bold" :class="getRoiClass(calculateRoi(v))">
                {{ calculateRoi(v) }}%
              </td>
              <td>
                <span class="badge" :class="statusBadgeClass(v.status)">
                  {{ v.status }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredRoiData.length === 0">
              <td colspan="9" class="text-center empty-grid-row">No records match the active search and filter parameters.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from '../composables/useToast';

const { showToast } = useToast();

const searchQuery = ref('');
const activeDropdown = ref(null);

const selectedTypes = ref([]);
const selectedStatuses = ref([]);
const selectedRegions = ref([]);

const typeOptions = ['Truck', 'Van', 'Sedan'];
const statusOptions = ['Available', 'On Trip', 'In Shop'];
const regionOptions = ['North', 'West', 'East', 'South'];

// Analytical dataset containing costs and revenues
const roiData = ref([
  { regNo: 'VAN-05', type: 'Van', status: 'Available', region: 'North', revenue: 12000, maintenance: 350, fuel: 600, acqCost: 35000 },
  { regNo: 'TRK-02', type: 'Truck', status: 'On Trip', region: 'West', revenue: 45000, maintenance: 1800, fuel: 2000, acqCost: 145000 },
  { regNo: 'SDN-01', type: 'Sedan', status: 'Available', region: 'East', revenue: 4800, maintenance: 120, fuel: 200, acqCost: 28000 },
  { regNo: 'TRK-04', type: 'Truck', status: 'In Shop', region: 'South', revenue: 22000, maintenance: 2500, fuel: 1100, acqCost: 95000 },
  { regNo: 'VAN-01', type: 'Van', status: 'On Trip', region: 'North', revenue: 15000, maintenance: 800, fuel: 1200, acqCost: 32000 },
  { regNo: 'SDN-02', type: 'Sedan', status: 'In Shop', region: 'West', revenue: 3200, maintenance: 600, fuel: 150, acqCost: 29000 }
]);

const toggleDropdown = (menu) => {
  if (activeDropdown.value === menu) {
    activeDropdown.value = null;
  } else {
    activeDropdown.value = menu;
  }
};

// Close dropdowns if user clicks outside
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-wrapper')) {
      activeDropdown.value = null;
    }
  });
});

const clearFilters = () => {
  selectedTypes.value = [];
  selectedStatuses.value = [];
  selectedRegions.value = [];
  searchQuery.value = '';
};

const hasActiveFilters = computed(() => {
  return selectedTypes.value.length > 0 || 
         selectedStatuses.value.length > 0 || 
         selectedRegions.value.length > 0 || 
         searchQuery.value !== '';
});

// Dynamic Business Metric Formulations
const calculateRoi = (v) => {
  const netEarnings = v.revenue - (v.maintenance + v.fuel);
  const val = (netEarnings / v.acqCost) * 100;
  return parseFloat(val.toFixed(1));
};

const totalOperationalCost = computed(() => {
  return roiData.value.reduce((acc, curr) => acc + curr.maintenance + curr.fuel, 0);
});

// Computed dynamic ranking filters
const filteredRoiData = computed(() => {
  return roiData.value.filter(v => {
    const matchesSearch = v.regNo.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesType = selectedTypes.value.length === 0 || selectedTypes.value.includes(v.type);
    const matchesStatus = selectedStatuses.value.length === 0 || selectedStatuses.value.includes(v.status);
    const matchesRegion = selectedRegions.value.length === 0 || selectedRegions.value.includes(v.region);
    return matchesSearch && matchesType && matchesStatus && matchesRegion;
  });
});

const averageRoi = computed(() => {
  if (filteredRoiData.value.length === 0) return 0;
  const sum = filteredRoiData.value.reduce((acc, curr) => acc + calculateRoi(curr), 0);
  return (sum / filteredRoiData.value.length).toFixed(1);
});

const getRoiClass = (roi) => {
  return roi >= 20 ? 'text-success' : (roi >= 10 ? 'text-info' : 'text-danger');
};

const statusBadgeClass = (status) => {
  if (status === 'Available') return 'badge-success';
  if (status === 'On Trip') return 'badge-info';
  return 'badge-warning';
};

// CSV Export Generator Utility
const downloadCSV = () => {
  if (filteredRoiData.value.length === 0) {
    showToast('Cannot export empty grid data.', 'warning');
    return;
  }

  let csvContent = 'data:text/csv;charset=utf-8,';
  csvContent += 'Vehicle,Type,Region,Revenue ($),Maintenance ($),Fuel ($),Acquisition ($),ROI (%),Status\n';
  
  filteredRoiData.value.forEach(row => {
    const roi = calculateRoi(row);
    csvContent += `${row.regNo},${row.type},${row.region},${row.revenue},${row.maintenance},${row.fuel},${row.acqCost},${roi}%,${row.status}\n`;
  });
  
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', 'TransitOps_Financials_ROI_Report.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  showToast('CSV report downloaded successfully!', 'success');
};
</script>

<style scoped>
.analytics-container {
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

.kpi-card {
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-hover);
}

.kpi-card .kpi-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-card .kpi-value {
  font-size: 2.25rem;
  font-weight: 800;
  color: #fff;
  margin: 0.5rem 0;
}

.kpi-card .kpi-subtext {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.kpi-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary) 0%, #a855f7 100%);
}

/* Filters UI Styling */
.filters-card {
  display: flex;
  gap: 1.25rem;
  align-items: center;
  padding: 1.25rem 1.5rem;
  flex-wrap: wrap;
}

.search-bar-wrapper {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
  border-radius: var(--border-radius-sm);
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  border-color: var(--primary);
}

.filter-dropdowns {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.dropdown-wrapper {
  position: relative;
}

.btn-dropdown {
  padding: 0.7rem 1.25rem;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: var(--border-radius-sm);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: border-color 0.2s ease;
}

.btn-dropdown:hover {
  border-color: var(--border-hover);
}

.dropdown-menu {
  position: absolute;
  top: 105%;
  left: 0;
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-lg);
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 10;
  min-width: 160px;
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.25rem;
}

.checkbox-label input {
  cursor: pointer;
}

.btn-reset {
  padding: 0.7rem 1.25rem;
  font-size: 0.9rem;
  border-radius: var(--border-radius-sm);
}

/* Grid card layout */
.grid-card {
  padding: 1.5rem;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.grid-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.row-count {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 700;
  background-color: rgba(255,255,255,0.02);
  padding: 0.35rem 0.75rem;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-color);
}

.table-wrapper {
  overflow-x: auto;
}

.font-bold { font-weight: 700; }
.font-mono { font-family: var(--mono); }
.highlight-text { color: #fff; }

.text-success { color: var(--success); }
.text-info { color: var(--info); }
.text-danger { color: var(--danger); }

.empty-grid-row {
  color: var(--text-muted);
  font-size: 0.9rem;
  padding: 3rem 0;
}
</style>
