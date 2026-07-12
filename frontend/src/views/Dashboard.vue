<template>
  <div>
    <!-- SAFETY OFFICER SPECIALIZED VIEW -->
    <div class="dashboard-container safety-theme" v-if="userRole === 'Safety Officer'">
      <div class="page-header">
        <div>
          <h1>Safety &amp; Compliance Portal</h1>
          <p class="subtitle">License compliance auditing and driver risk anomaly checks</p>
        </div>
      </div>

      <!-- Actionable Alert Anomaly Banner -->
      <div class="anomaly-banner" v-if="flaggedDrivers.length > 0">
        <div class="banner-header">
          <span class="alert-pulse">🔔</span>
          <h3>Compliance Actionable Alerts</h3>
          <span class="anomaly-count">{{ flaggedDrivers.length }} Flagged Drivers</span>
        </div>
        <div class="anomaly-list">
          <div class="anomaly-card" v-for="driver in flaggedDrivers" :key="driver.licenseNo">
            <div class="card-details">
              <span class="driver-name font-bold">{{ driver.name }}</span>
              <span class="issue-tag font-mono">{{ driver.issue }}</span>
            </div>
            <div class="card-actions">
              <span class="badge" :class="trafficLightBadgeClass(driver.severity)">
                {{ driver.severity }}
              </span>
              <button @click="resolveDriver(driver)" class="btn-sm btn-accent">Flag Resolved</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Safety KPIs -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-icon">👤</span>
            <span class="kpi-label">Compliant Drivers</span>
          </div>
          <div class="kpi-body">
            <span class="kpi-value text-success">14</span>
            <span class="kpi-subtext">Active &amp; valid licenses</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-icon">⚠️</span>
            <span class="kpi-label">Flagged Licenses</span>
          </div>
          <div class="kpi-body">
            <span class="kpi-value text-warning">2</span>
            <span class="kpi-subtext">Expiring within 30 days</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-icon">❌</span>
            <span class="kpi-label">Suspended Drivers</span>
          </div>
          <div class="kpi-body">
            <span class="kpi-value text-danger">2</span>
            <span class="kpi-subtext">Requires retraining</span>
          </div>
        </div>
      </div>

      <!-- Virtualized Historical Driver Logs Table -->
      <div class="card logs-card">
        <div class="card-header-logs">
          <div>
            <h3>Audit Log Archive (Virtualized View)</h3>
            <p class="card-subtitle font-bold">Instantly scrolling through 2,000 audit records with zero lag</p>
          </div>
          <span class="logs-stats">Total Logs: {{ historicalLogs.length }} | Rendered: {{ visibleLogs.length }}</span>
        </div>

        <!-- Virtual Scroll Viewport -->
        <div class="virtual-scroll-viewport" @scroll="handleScroll">
          <div class="virtual-scroll-spacer" :style="{ height: totalListHeight + 'px' }">
            <table class="data-table virtual-table" :style="{ transform: `translateY(${offsetY}px)` }">
              <thead>
                <tr>
                  <th>Audit ID</th>
                  <th>Driver Name</th>
                  <th>Incident / Event</th>
                  <th>Safety Score</th>
                  <th>Compliance Check</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in visibleLogs" :key="log.id" style="height: 55px;">
                  <td class="font-mono">#{{ log.id }}</td>
                  <td class="font-bold highlight-text">{{ log.driver }}</td>
                  <td>{{ log.event }}</td>
                  <td>
                    <span class="safety-score-label" :class="getSafetyClass(log.score)">
                      {{ log.score }}/100
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="complianceBadgeClass(log.compliance)">
                      {{ log.compliance }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- DRIVER SPECIALIZED VIEW -->
    <div class="dashboard-container driver-theme" v-else-if="userRole === 'Driver'">
      <div class="page-header">
        <div>
          <h1>My Active Dispatches</h1>
          <p class="subtitle">Real-time status updates and trip logging</p>
        </div>
      </div>

      <!-- Linear Workflow Stepper Widget -->
      <div class="card stepper-card">
        <div class="card-header">
          <h3>Workflow Actions</h3>
          <span v-if="activeTrip" class="badge badge-info">Trip #{{ activeTrip.id }}</span>
        </div>

        <div v-if="activeTrip" class="stepper-widget">
          <!-- Horizontal Stepper Bar -->
          <div class="stepper-steps">
            <div class="step-item" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
              <span class="step-num">1</span>
              <span class="step-text">Assigned</span>
            </div>
            <div class="step-divider" :class="{ active: currentStep > 1 }"></div>
            <div class="step-item" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
              <span class="step-num">2</span>
              <span class="step-text">On Road</span>
            </div>
            <div class="step-divider" :class="{ active: currentStep > 2 }"></div>
            <div class="step-item" :class="{ active: currentStep >= 3 }">
              <span class="step-num">3</span>
              <span class="step-text">Finished</span>
            </div>
          </div>

          <!-- Trip details container -->
          <div class="active-trip-details">
            <div class="detail-row">
              <div>
                <span class="label">Route</span>
                <span class="value">{{ activeTrip.source }} &rarr; {{ activeTrip.destination }}</span>
              </div>
              <div>
                <span class="label">Cargo Weight</span>
                <span class="value font-mono">{{ activeTrip.cargoWeight }} kg</span>
              </div>
              <div>
                <span class="label">Distance</span>
                <span class="value font-mono">{{ activeTrip.plannedDistance }} km</span>
              </div>
            </div>

            <!-- Stepper Actions Context -->
            <div class="workflow-actions">
              <!-- Step 1: Draft -> Dispatch -->
              <div v-if="activeTrip.status === 'Draft'" class="action-block">
                <p>Verify cargo loading limits and click to declare departure.</p>
                <button @click="startTrip" class="btn-primary">
                  🚀 Start Departure
                </button>
              </div>

              <!-- Step 2: Dispatched -> Complete -->
              <div v-else-if="activeTrip.status === 'Dispatched'" class="action-block">
                <p class="warning-text">Enter trip closing values to complete this dispatch.</p>
                <div class="form-row">
                  <div class="form-group">
                    <label>Actual Distance Traveled (km)</label>
                    <input type="number" v-model.number="completionData.actualDistance" required />
                  </div>
                  <div class="form-group">
                    <label>Logged Fuel Cost ($)</label>
                    <input type="number" v-model.number="completionData.fuelCost" required />
                  </div>
                </div>
                <button @click="finishTrip" class="btn-primary" :disabled="!completionData.actualDistance || !completionData.fuelCost">
                  ✅ Complete Trip
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- No active dispatches placeholder -->
        <div v-else class="empty-dispatcher">
          <span class="dispatcher-icon">🌟</span>
          <h4>No Active Dispatches</h4>
          <p>You have completed all assigned routes. Awaiting dispatcher scheduling.</p>
        </div>
      </div>

      <!-- Historical Trips Card -->
      <div class="card">
        <div class="card-header">
          <h3>My Completed Shifts</h3>
          <p class="card-subtitle">Historical dispatches records</p>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Trip ID</th>
              <th>Route</th>
              <th>Cargo</th>
              <th>Distance</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in driverTrips" :key="t.id">
              <td class="font-mono">#{{ t.id }}</td>
              <td>{{ t.source }} &rarr; {{ t.destination }}</td>
              <td>{{ t.cargoWeight }} kg</td>
              <td>{{ t.plannedDistance }} km</td>
              <td>
                <span class="badge badge-success">Completed</span>
              </td>
            </tr>
            <tr v-if="driverTrips.length === 0">
              <td colspan="5" class="text-center empty-row">No completed dispatches logged.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- STANDARD MANAGER / DISPATCHER VIEW -->
    <div class="dashboard-container" v-else>
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
          <div class="kpi-header">
            <span class="kpi-icon">{{ kpi.icon }}</span>
            <span class="kpi-label">{{ kpi.title }}</span>
          </div>
          <div class="kpi-body">
            <span class="kpi-value">{{ kpi.value }}</span>
            <span class="kpi-subtext">{{ kpi.subtext }}</span>
          </div>
          <div class="kpi-border"></div>
        </div>
      </div>

      <!-- Main Content Layout Grid -->
      <div class="content-row">
        <!-- Recent Trips Table -->
        <div class="card recent-trips">
          <div class="card-header">
            <div>
              <h3>Active &amp; Recent Dispatches</h3>
              <p class="card-subtitle">Real-time status of dispatch operations</p>
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
              <tr v-for="trip in recentTrips" :key="trip.id">
                <td class="font-mono">#{{ trip.id }}</td>
                <td>{{ trip.vehicle || 'Awaiting vehicle' }}</td>
                <td>{{ trip.driver || 'Awaiting driver' }}</td>
                <td>{{ trip.cargoWeight }} kg</td>
                <td>
                  <span class="badge" :class="badgeClass(trip.status)">
                    {{ trip.status }}
                  </span>
                </td>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useToast } from '../composables/useToast';

const { showToast } = useToast();
const userRole = ref('Fleet Manager');

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('transitops_user') || '{}');
  if (user.role) userRole.value = user.role;
  generateHistoricalLogs();
});

// SAFETY OFFICER: Flags & Anomalies list
const flaggedDrivers = ref([
  { name: 'Jack Torrance', licenseNo: 'DL-66611', issue: 'Safety score critically low (45/100)', severity: 'Red' },
  { name: 'Bruce Wayne', licenseNo: 'DL-00707', issue: 'License expires within 30 days (expiring 2026-02-15)', severity: 'Orange' },
  { name: 'Peter Parker', licenseNo: 'DL-12290', issue: 'Over-speed event logged', severity: 'Orange' }
]);

const resolveDriver = (driver) => {
  flaggedDrivers.value = flaggedDrivers.value.filter(d => d.licenseNo !== driver.licenseNo);
  showToast(`Compliance issue flagged for ${driver.name} marked as resolved!`, 'success');
};

const trafficLightBadgeClass = (severity) => {
  if (severity === 'Red') return 'badge-danger';
  if (severity === 'Orange') return 'badge-warning';
  return 'badge-success';
};

// SAFETY OFFICER: Virtual Scroll historical compliance audit logs
const historicalLogs = ref([]);
const scrollTop = ref(0);
const rowHeight = 55; // pixels per row
const viewportHeight = 350; // height of viewport container

const generateHistoricalLogs = () => {
  const driversPool = ['Sarah Connor', 'Bruce Wayne', 'Alex Johnson', 'Peter Parker', 'Jack Torrance', 'Diana Prince', 'Clark Kent'];
  const events = ['Speeding Alert', 'License Audit Completed', 'Seatbelt Unbuckled Check', 'Fatigue Warning Sensor', 'Route Deviation Checked', 'Brake G-Force Alert'];
  const complianceStatus = ['Pass', 'Warn', 'Fail'];

  const logs = [];
  for (let i = 1; i <= 2000; i++) {
    const score = Math.floor(Math.random() * 45) + 55; // 55 to 100
    const compliance = score >= 90 ? 'Pass' : (score >= 70 ? 'Warn' : 'Fail');
    logs.push({
      id: 5000 + i,
      driver: driversPool[i % driversPool.length],
      event: events[i % events.length],
      score: score,
      compliance: compliance
    });
  }
  historicalLogs.value = logs;
};

const handleScroll = (e) => {
  scrollTop.value = e.target.scrollTop;
};

// List Virtualization Computed Values
const totalListHeight = computed(() => {
  return historicalLogs.value.length * rowHeight;
});

const visibleCount = computed(() => {
  return Math.ceil(viewportHeight / rowHeight) + 2;
});

const startIndex = computed(() => {
  return Math.floor(scrollTop.value / rowHeight);
});

const endIndex = computed(() => {
  return startIndex.value + visibleCount.value;
});

const visibleLogs = computed(() => {
  return historicalLogs.value.slice(startIndex.value, endIndex.value);
});

const offsetY = computed(() => {
  return startIndex.value * rowHeight;
});

const complianceBadgeClass = (status) => {
  if (status === 'Pass') return 'badge-success';
  if (status === 'Warn') return 'badge-warning';
  return 'badge-danger';
};

// Stepper workflow tracking for Driver
const activeTrip = ref({
  id: 1046,
  source: 'Retail Hub A',
  destination: 'Storage Yard West',
  cargoWeight: 420,
  plannedDistance: 95,
  status: 'Draft'
});

const currentStep = computed(() => {
  if (!activeTrip.value) return 3;
  if (activeTrip.value.status === 'Draft') return 1;
  if (activeTrip.value.status === 'Dispatched') return 2;
  return 3;
});

const completionData = reactive({
  actualDistance: 95,
  fuelCost: 120
});

const driverTrips = ref([
  { id: 1042, source: 'Depot North', destination: 'Storage Yard West', cargoWeight: 380, plannedDistance: 80, status: 'Completed' },
  { id: 1039, source: 'Client Yard B', destination: 'Central Depot', cargoWeight: 410, plannedDistance: 110, status: 'Completed' }
]);

const startTrip = () => {
  activeTrip.value.status = 'Dispatched';
  showToast('Departure declared! Drive safely.', 'success');
};

const finishTrip = () => {
  driverTrips.value.unshift({
    id: activeTrip.value.id,
    source: activeTrip.value.source,
    destination: activeTrip.value.destination,
    cargoWeight: activeTrip.value.cargoWeight,
    plannedDistance: completionData.actualDistance,
    status: 'Completed'
  });

  activeTrip.value = null;
  showToast('Trip dispatches completed successfully and logged!', 'success');
};

// MANAGER VIEWS STATS
const filters = reactive({
  type: 'All',
  status: 'All'
});

const kpis = ref([
  { title: 'Active Vehicles', value: '18', subtext: 'Out of 24 total', icon: '🚚' },
  { title: 'Available Vehicles', value: '12', subtext: 'Ready for dispatch', icon: '✅' },
  { title: 'Vehicles in Maintenance', value: '3', subtext: 'Currently in shop', icon: '🔧' },
  { title: 'Active Trips', value: '8', subtext: 'On road', icon: '🗺️' },
  { title: 'Pending Trips', value: '2', subtext: 'Awaiting dispatch', icon: '⏳' },
  { title: 'Drivers On Duty', value: '15', subtext: 'Out of 20 total', icon: '👤' },
  { title: 'Fleet Utilization', value: '75%', subtext: 'Target is 85%', icon: '📈' }
]);

const recentTrips = ref([
  { id: 1045, vehicle: 'VAN-05', driver: 'Alex Johnson', cargoWeight: 450, status: 'Dispatched' },
  { id: 1044, vehicle: 'TRK-02', driver: 'Sarah Connor', cargoWeight: 2200, status: 'Completed' },
  { id: 1043, vehicle: 'SDN-01', driver: 'Bruce Wayne', cargoWeight: 350, status: 'Completed' },
  { id: 1042, vehicle: null, driver: null, cargoWeight: 800, status: 'Draft' },
  { id: 1041, vehicle: 'TRK-04', driver: 'Clark Kent', cargoWeight: 1800, status: 'Cancelled' }
]);

const badgeClass = (status) => {
  if (status === 'Dispatched') return 'badge-info';
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
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
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease;
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

/* SAFETY OFFICER STYLING */
.anomaly-banner {
  background-color: #1a0f12;
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: 0 4px 25px rgba(239, 68, 68, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.banner-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--danger);
}

.banner-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
}

.anomaly-count {
  background-color: var(--danger-glow);
  color: var(--danger);
  padding: 0.2rem 0.5rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.alert-pulse {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
}

.anomaly-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.anomaly-card {
  background-color: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.card-details {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.driver-name {
  color: #fff;
}

.issue-tag {
  color: var(--text-secondary);
  font-size: 0.85rem;
  background-color: var(--card-bg);
  padding: 0.2rem 0.6rem;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-color);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-actions .badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
}

/* Stepper widget for Drivers layout */
.stepper-card {
  border-left: 4px solid var(--primary);
}

.stepper-widget {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin: 1rem 0;
}

.stepper-steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background-color: var(--card-bg);
  padding: 1.25rem 2rem;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  background-color: var(--panel-bg);
}

.step-text {
  font-size: 0.85rem;
  font-weight: 700;
}

.step-item.active {
  color: var(--primary);
}
.step-item.active .step-num {
  border-color: var(--primary);
  box-shadow: 0 0 10px var(--primary-glow);
}

.step-item.completed {
  color: var(--success);
}
.step-item.completed .step-num {
  border-color: var(--success);
  background-color: var(--success-glow);
}

.step-divider {
  flex: 1;
  height: 2px;
  background-color: var(--border-color);
  margin: 0 1rem;
}

.step-divider.active {
  background-color: var(--primary);
}

.active-trip-details {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.detail-row .label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.detail-row .value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #fff;
}

.workflow-actions {
  border-top: 1px solid var(--border-color);
  padding-top: 1.5rem;
}

.action-block p {
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.action-block .form-row {
  margin-bottom: 1.25rem;
}

.warning-text {
  color: var(--warning);
  font-weight: 600;
}

.empty-dispatcher {
  text-align: center;
  padding: 3rem 1.5rem;
}

.dispatcher-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.empty-dispatcher h4 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.empty-dispatcher p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  max-width: 320px;
  margin: 0 auto;
}

/* Virtual scroll layout overrides */
.logs-card {
  overflow: hidden;
}

.card-header-logs {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.logs-stats {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 700;
  background-color: rgba(255,255,255,0.02);
  padding: 0.4rem 0.8rem;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-color);
}

.virtual-scroll-viewport {
  height: 350px;
  overflow-y: auto;
  position: relative;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background-color: var(--card-bg);
}

.virtual-scroll-spacer {
  position: relative;
}

.virtual-table {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.safety-score-label {
  font-weight: 700;
  font-size: 0.9rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius-sm);
}

.safety-score-label.excellent {
  color: var(--success);
  background-color: var(--success-glow);
}
.safety-score-label.good {
  color: var(--info);
  background-color: var(--info-glow);
}
.safety-score-label.risk {
  color: var(--danger);
  background-color: var(--danger-glow);
}

.font-mono { font-family: var(--mono); }
.font-bold { font-weight: 700; }
.highlight-text { color: #fff; }

.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  border-radius: var(--border-radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 700;
  transition: opacity 0.2s ease;
}

.btn-sm:hover {
  opacity: 0.9;
}

.btn-sm.btn-accent { background-color: var(--primary); color: white; }

@media (max-width: 1100px) {
  .content-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .stepper-steps {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .step-divider {
    display: none;
  }
  .step-item {
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }
}
</style>
