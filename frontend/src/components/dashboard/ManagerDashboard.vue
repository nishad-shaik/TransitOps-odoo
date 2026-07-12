<template>
  <div class="dashboard-container">
    <div class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p class="subtitle">Overview of fleet operations and utilization</p>
      </div>
      <div class="filters">
        <select v-model="filters.type">
          <option value="All">All Types</option>
          <option value="Truck">Truck</option>
          <option value="Van">Van</option>
          <option value="Sedan">Sedan</option>
        </select>
        <select v-model="filters.status">
          <option value="All">All Statuses</option>
          <option value="Available">Available</option>
          <option value="On Trip">On Trip</option>
          <option value="In Shop">In Shop</option>
        </select>
      </div>
    </div>

    <!-- Bento Grid matrix holding metric cards -->
    <div class="bento-grid">
      <div 
        class="kpi-card cursor-pointer bento-card-span-1" 
        v-for="kpi in kpis" 
        :key="kpi.title"
        @click="handleKpiClick(kpi.title)"
        :class="{ 'bento-card-span-2': kpi.title === 'Fleet Utilization', 'border-[#06B6D4]': activeKpiFilter === kpi.filterVal }"
      >
        <div class="kpi-header">
          <component :is="kpi.icon" class="kpi-icon-svg text-primary" />
          <span class="kpi-label">{{ kpi.title }}</span>
        </div>
        <div class="kpi-body-wrapper">
          <div class="kpi-body">
            <span class="kpi-value">{{ kpi.value }}</span>
            <span class="kpi-subtext">{{ kpi.subtext }}</span>
          </div>
          <!-- Signature Radial Gauge for Fleet Utilization % -->
          <div class="kpi-gauge-wrapper" v-if="kpi.value.includes('%')">
            <svg class="radial-gauge" viewBox="0 0 36 36">
              <path
                class="gauge-bg"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                class="gauge-fill"
                :stroke-dasharray="statsData?.utilizationRate ? parseFloat(statsData.utilizationRate) + ', 100' : '0, 100'"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
          </div>
        </div>
        <div class="kpi-border"></div>
      </div>
    </div>

    <!-- Main Content Layout Grid -->
    <div class="content-row">
      <!-- Recent Trips Table with KPI filtrations -->
      <div class="card recent-trips">
        <div class="card-header">
          <div>
            <h3>Active &amp; Recent Dispatches</h3>
            <p class="card-subtitle" v-if="activeKpiFilter !== 'All'">
              Filtering for: <span class="badge badge-info">{{ activeKpiFilter }}</span>
            </p>
            <p class="card-subtitle" v-else>Real-time status of dispatch operations</p>
          </div>
          <router-link to="/trips" class="link-more">Manage Trips &rarr;</router-link>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Trip ID</th>
              <th>Vehicle</th>
              <th>Driver</th>
              <th>Cargo Load</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trip in filteredRecentTrips" :key="trip.id">
              <td class="font-mono">#{{ trip.id }}</td>
              <td>{{ trip.vehicle_id || 'Awaiting vehicle' }}</td>
              <td>{{ trip.driver_id || 'Awaiting driver' }}</td>
              <td>{{ trip.cargo_weight }} kg</td>
              <td>
                <span class="badge" :class="badgeClass(trip.status)">
                  {{ trip.status }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredRecentTrips.length === 0">
              <td colspan="5" class="text-center empty-row">No records match the active filter constraints.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Fleet Distribution Chart/Proportional Bars -->
      <div class="card fleet-status">
        <div class="card-header">
          <h3>Fleet Distribution</h3>
          <p class="card-subtitle">Active vehicles status split</p>
        </div>
        <div class="status-distribution">
          <div class="dist-bar">
            <div class="bar-segment available" :style="{ width: distributionPercent('available') + '%' }" :title="'Available: ' + distributionPercent('available') + '%'"></div>
            <div class="bar-segment ontrip" :style="{ width: distributionPercent('on_trip') + '%' }" :title="'On Trip: ' + distributionPercent('on_trip') + '%'"></div>
            <div class="bar-segment inshop" :style="{ width: distributionPercent('maintenance') + '%' }" :title="'In Shop: ' + distributionPercent('maintenance') + '%'"></div>
            <div class="bar-segment retired" :style="{ width: distributionPercent('retired') + '%' }" :title="'Retired: ' + distributionPercent('retired') + '%'"></div>
          </div>
          <div class="dist-legend">
            <div class="legend-item"><span class="dot available"></span> Available ({{ distributionPercent('available') }}%)</div>
            <div class="legend-item"><span class="dot ontrip"></span> On Trip ({{ distributionPercent('on_trip') }}%)</div>
            <div class="legend-item"><span class="dot inshop"></span> In Shop ({{ distributionPercent('maintenance') }}%)</div>
            <div class="legend-item"><span class="dot retired"></span> Retired ({{ distributionPercent('retired') }}%)</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Compass, Hourglass, BarChart3, Wrench } from '@lucide/vue';
import { useToast } from '../../composables/useToast';
import { useApiResource } from '../../composables/useApiResource';

const { showToast } = useToast();

const filters = reactive({
  type: 'All',
  status: 'All'
});

const activeKpiFilter = ref('All');

const { data: statsData, fetch: fetchStats } = useApiResource('/dashboard/stats');
const { data: apiVehicles, fetch: fetchVehicles } = useApiResource('/vehicles');

onMounted(() => {
  fetchStats();
  fetchVehicles();
});

const kpis = computed(() => [
  { title: 'Active Trips', value: String(statsData.value?.activeTrips ?? 0), subtext: 'Click to filter ongoing', icon: Compass, filterVal: 'Dispatched' },
  { title: 'Pending Trips', value: String(statsData.value?.pendingTrips ?? 0), subtext: 'Click to filter pending', icon: Hourglass, filterVal: 'Draft' },
  { title: 'In Shop Vehicles', value: String(statsData.value?.distribution?.maintenance ?? 0), subtext: 'Click to filter workshop', icon: Wrench, filterVal: 'In Shop' },
  { title: 'Fleet Utilization', value: statsData.value?.utilizationRate ?? '0%', subtext: 'Click to reset filter', icon: BarChart3, filterVal: 'All' }
]);

const handleKpiClick = (title) => {
  if (title === 'Active Trips') {
    activeKpiFilter.value = 'Dispatched';
    showToast('KPI Filter: Showing Dispatched/Ongoing Trips', 'info');
  } else if (title === 'Pending Trips') {
    activeKpiFilter.value = 'Draft';
    showToast('KPI Filter: Showing Draft/Scheduled Trips', 'info');
  } else if (title === 'In Shop Vehicles') {
    activeKpiFilter.value = 'In Shop';
    showToast('KPI Filter: Showing In Shop/Maintenance Vehicles', 'info');
  } else {
    activeKpiFilter.value = 'All';
    showToast('KPI Filter Reset: Showing all dispatches', 'info');
  }
};

const recentTrips = computed(() => statsData.value?.recentTrips ?? []);

const distributionPercent = (key) => {
  const total = statsData.value?.distribution?.total ?? 0;
  if (total === 0) return 0;
  const val = statsData.value?.distribution?.[key] ?? 0;
  return Math.round((val / total) * 100);
};

const filteredRecentTrips = computed(() => {
  return recentTrips.value.filter(trip => {
    if (activeKpiFilter.value === 'Dispatched') {
      return trip.status === 'Dispatched' || trip.status === 'Completed' || trip.status === 'Ongoing';
    }
    if (activeKpiFilter.value === 'Draft') {
      return trip.status === 'Draft' || trip.status === 'Scheduled';
    }
    if (activeKpiFilter.value === 'In Shop') {
      return trip.vehicle_id && (apiVehicles.value || []).find(v => v.registration_number === trip.vehicle_id)?.status === 'In Shop';
    }
    const matchesType = filters.type === 'All' || trip.type === filters.type;
    const matchesStatus = filters.status === 'All' || trip.status === filters.status;
    return matchesType && matchesStatus;
  });
});

const badgeClass = (status) => {
  if (status === 'Dispatched' || status === 'Ongoing') return 'badge-info';
  if (status === 'Completed') return 'badge-success';
  if (status === 'Draft') return 'badge-warning';
  return 'badge-danger';
};
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
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

.filters {
  display: flex;
  gap: 0.75rem;
}

.filters select {
  padding: 0.6rem 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background-color: var(--panel-bg);
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.bento-card-span-1 {
  grid-column: span 1;
}

.bento-card-span-2 {
  grid-column: span 1; /* Fallback for small screens */
}

@media (min-width: 768px) {
  .bento-card-span-2 {
    grid-column: span 2;
  }
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
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease;
  cursor: pointer;
}

.kpi-card:hover {
  transform: translateY(-3px);
  border-color: var(--border-hover);
}

.kpi-card:hover .kpi-border {
  opacity: 1;
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.kpi-icon {
  font-size: 1.25rem;
}

.kpi-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-body {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-size: 2.25rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.1;
}

.kpi-subtext {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.kpi-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary) 0%, #7c3aed 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.content-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.75rem;
}

.card-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.link-more {
  color: var(--primary);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 700;
  transition: color 0.2s ease;
}

.link-more:hover {
  color: var(--primary-hover);
}

.status-distribution {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.dist-bar {
  display: flex;
  height: 1.5rem;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.bar-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.bar-segment.available { background-color: var(--success); }
.bar-segment.ontrip { background-color: var(--info); }
.bar-segment.inshop { background-color: var(--warning); }
.bar-segment.retired { background-color: var(--danger); }

.dist-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: var(--text-primary);
}

.dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  display: inline-block;
}

.dot.available { background-color: var(--success); }
.dot.ontrip { background-color: var(--info); }
.dot.inshop { background-color: var(--warning); }
.dot.retired { background-color: var(--danger); }

.font-mono { font-family: var(--mono); }
.font-bold { font-weight: 700; }
.highlight-text { color: #fff; }

@media (max-width: 1100px) {
  .content-row {
    grid-template-columns: 1fr;
  }
}
</style>
