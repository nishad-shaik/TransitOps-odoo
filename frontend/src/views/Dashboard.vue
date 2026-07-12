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

    <!-- KPI Cards Grid -->
    <div class="kpi-grid">
      <div class="kpi-card" v-for="kpi in kpis" :key="kpi.title">
        <span class="kpi-label">{{ kpi.title }}</span>
        <span class="kpi-value">{{ kpi.value }}</span>
        <span class="kpi-subtext">{{ kpi.subtext }}</span>
      </div>
    </div>

    <!-- Main Content Layout -->
    <div class="content-row">
      <!-- Recent Trips Table -->
      <div class="card recent-trips">
        <div class="card-header">
          <h3>Recent Trips</h3>
          <router-link to="/trips" class="link-more">Manage Trips &rarr;</router-link>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Trip ID</th>
              <th>Vehicle</th>
              <th>Driver</th>
              <th>Cargo</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trip in recentTrips" :key="trip.id">
              <td>#{{ trip.id }}</td>
              <td>{{ trip.vehicle || 'Awaiting vehicle' }}</td>
              <td>{{ trip.driver || 'Awaiting driver' }}</td>
              <td>{{ trip.cargoWeight }} kg</td>
              <td>
                <span class="badge" :class="trip.status.toLowerCase()">
                  {{ trip.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Fleet Distribution Chart/Proportional Bars -->
      <div class="card fleet-status">
        <h3>Fleet Status Distribution</h3>
        <div class="status-distribution">
          <div class="dist-bar">
            <div class="bar-segment available" style="width: 50%" title="Available: 50%"></div>
            <div class="bar-segment ontrip" style="width: 30%" title="On Trip: 30%"></div>
            <div class="bar-segment inshop" style="width: 15%" title="In Shop: 15%"></div>
            <div class="bar-segment retired" style="width: 5%" title="Retired: 5%"></div>
          </div>
          <div class="dist-legend">
            <div class="legend-item"><span class="dot available"></span> Available (50%)</div>
            <div class="legend-item"><span class="dot ontrip"></span> On Trip (30%)</div>
            <div class="legend-item"><span class="dot inshop"></span> In Shop (15%)</div>
            <div class="legend-item"><span class="dot retired"></span> Retired (5%)</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const filters = reactive({
  type: 'All',
  status: 'All'
});

const kpis = ref([
  { title: 'Active Vehicles', value: '18', subtext: 'Out of 24 total' },
  { title: 'Available Vehicles', value: '12', subtext: 'Ready for dispatch' },
  { title: 'Vehicles in Maintenance', value: '3', subtext: 'Currently in shop' },
  { title: 'Active Trips', value: '8', subtext: 'On road' },
  { title: 'Pending Trips', value: '2', subtext: 'Awaiting dispatch' },
  { title: 'Drivers On Duty', value: '15', subtext: 'Out of 20 total' },
  { title: 'Fleet Utilization', value: '75%', subtext: 'Target is 85%' }
]);

const recentTrips = ref([
  { id: 1045, vehicle: 'Van-05', driver: 'Alex Johnson', cargoWeight: 450, status: 'Dispatched' },
  { id: 1044, vehicle: 'Truck-02', driver: 'Sarah Connor', cargoWeight: 2200, status: 'Completed' },
  { id: 1043, vehicle: 'Sedan-01', driver: 'Bruce Wayne', cargoWeight: 150, status: 'Completed' },
  { id: 1042, vehicle: null, driver: null, cargoWeight: 800, status: 'Draft' },
  { id: 1041, vehicle: 'Truck-04', driver: 'Clark Kent', cargoWeight: 1800, status: 'Cancelled' }
]);
</script>

<style scoped>
.dashboard-container {
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

.filters {
  display: flex;
  gap: 1rem;
}

.filters select {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  background-color: var(--bg);
  color: var(--text-h);
  font-size: 0.9rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.kpi-card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
}

.kpi-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-h);
  margin: 0.25rem 0;
}

.kpi-subtext {
  font-size: 0.75rem;
  color: var(--text);
}

.content-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 1.25rem;
  box-shadow: var(--shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  color: var(--text-h);
}

.link-more {
  color: var(--accent);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.data-table th {
  color: var(--text);
  font-weight: 600;
}

.data-table td {
  color: var(--text-h);
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge.dispatched {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.badge.completed {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.badge.draft {
  background-color: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.badge.cancelled {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-distribution {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
}

.dist-bar {
  display: flex;
  height: 1.5rem;
  border-radius: 0.375rem;
  overflow: hidden;
}

.bar-segment {
  height: 100%;
}

.bar-segment.available { background-color: #10b981; }
.bar-segment.ontrip { background-color: #3b82f6; }
.bar-segment.inshop { background-color: #f59e0b; }
.bar-segment.retired { background-color: #ef4444; }

.dist-legend {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-h);
}

.dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  display: inline-block;
}

.dot.available { background-color: #10b981; }
.dot.ontrip { background-color: #3b82f6; }
.dot.inshop { background-color: #f59e0b; }
.dot.retired { background-color: #ef4444; }

@media (max-width: 1024px) {
  .content-row {
    grid-template-columns: 1fr;
  }
}
</style>
