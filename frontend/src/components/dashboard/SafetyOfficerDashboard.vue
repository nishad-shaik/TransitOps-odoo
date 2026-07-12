<template>
  <div class="dashboard-container safety-theme">
    <div class="page-header">
      <div>
        <h1>Safety &amp; Compliance Portal</h1>
        <p class="subtitle">License compliance auditing and driver risk anomaly checks</p>
      </div>
    </div>

    <!-- Actionable Alert Anomaly Banner (Dynamic filtration) -->
    <div class="anomaly-banner" v-if="flaggedDrivers.length > 0">
      <div class="banner-header">
        <span class="alert-pulse">🚨</span>
        <h3>Actionable Alert Anomaly Banner</h3>
        <span class="anomaly-count">{{ flaggedDrivers.length }} Flags Detected</span>
      </div>
      <div class="anomaly-list">
        <div class="anomaly-card" v-for="driver in flaggedDrivers" :key="driver.license_number">
          <div class="card-details">
            <span class="driver-name font-bold">{{ driver.name }}</span>
            <span class="issue-tag font-mono">{{ driver.issue }}</span>
          </div>
          <div class="card-actions">
            <span class="badge" :class="trafficLightBadgeClass(driver.severity)">
              {{ driver.severity === 'Red' ? 'Expired/Disabled' : 'Expiring Soon/Low Score' }}
            </span>
            <button @click="resolveDriver(driver)" class="btn-sm btn-accent">Mute Flag</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Safety KPIs -->
    <div class="kpi-grid">
      <div class="kpi-card" @click="handleSafetyKpiClick('All')">
        <div class="kpi-header">
          <span class="kpi-icon">👥</span>
          <span class="kpi-label">Total Drivers</span>
        </div>
        <div class="kpi-body">
          <span class="kpi-value">5</span>
          <span class="kpi-subtext">Click to view all registry logs</span>
        </div>
        <div class="kpi-border"></div>
      </div>
      
      <div class="kpi-card" @click="handleSafetyKpiClick('Red')">
        <div class="kpi-header">
          <span class="kpi-icon">❌</span>
          <span class="kpi-label">Expired/Suspended</span>
        </div>
        <div class="kpi-body">
          <span class="kpi-value text-danger">2</span>
          <span class="kpi-subtext">Requires immediate intervention</span>
        </div>
        <div class="kpi-border-red"></div>
      </div>

      <div class="kpi-card" @click="handleSafetyKpiClick('Orange')">
        <div class="kpi-header">
          <span class="kpi-icon">⚠️</span>
          <span class="kpi-label">Expiring Soon/Risk</span>
        </div>
        <div class="kpi-body">
          <span class="kpi-value text-warning">2</span>
          <span class="kpi-subtext">Safety score &lt; 70 or expiring license</span>
        </div>
        <div class="kpi-border-orange"></div>
      </div>
    </div>

    <!-- Virtualized Historical Driver Logs Table -->
    <div class="card logs-card">
      <div class="card-header-logs">
        <div>
          <h3>Audit Log Archive (Virtualized View)</h3>
          <p class="card-subtitle font-bold text-secondary">Instantly scrolling through 2,000 audit records with zero latency</p>
        </div>
        <span class="logs-stats">Logs: {{ filteredHistoricalLogs.length }} | Rendered: {{ visibleLogs.length }}</span>
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from '../../composables/useToast';

const { showToast } = useToast();

const driversPool = ref([
  { name: 'Jack Torrance', license_number: 'DL-66611', safety_score: 45, license_expiry_date: '2026-01-15', status: 'Suspended' },
  { name: 'Bruce Wayne', license_number: 'DL-00707', safety_score: 88, license_expiry_date: '2026-08-01', status: 'Active' },
  { name: 'Peter Parker', license_number: 'DL-12290', safety_score: 68, license_expiry_date: '2027-04-10', status: 'Active' },
  { name: 'Alex Johnson', license_number: 'DL-55291', safety_score: 92, license_expiry_date: '2026-12-15', status: 'Active' },
  { name: 'Sarah Connor', license_number: 'DL-44011', safety_score: 98, license_expiry_date: '2026-05-10', status: 'Active' }
]);

const flaggedDrivers = computed(() => {
  const today = new Date('2026-07-12');
  const thirtyDaysLater = new Date('2026-08-11');
  
  return driversPool.value.map(driver => {
    const expiry = new Date(driver.license_expiry_date);
    const isExpired = expiry < today;
    const isExpiringSoon = expiry >= today && expiry <= thirtyDaysLater;
    const isLowScore = driver.safety_score < 70;
    const isSuspended = driver.status === 'Suspended';
    
    let issue = '';
    let severity = 'Green';
    
    if (isExpired || isSuspended) {
      severity = 'Red';
      issue = isSuspended ? 'Driver credentials Suspended' : `License Expired (${driver.license_expiry_date})`;
    } else if (isExpiringSoon || isLowScore) {
      severity = 'Orange';
      issue = isLowScore ? `Safety score low (${driver.safety_score}/100)` : `License Expiring Soon (${driver.license_expiry_date})`;
    }
    
    return {
      ...driver,
      issue,
      severity
    };
  }).filter(d => d.severity !== 'Green');
});

const resolveDriver = (driver) => {
  driversPool.value = driversPool.value.map(d => {
    if (d.license_number === driver.license_number) {
      return {
        ...d,
        status: 'Active',
        safety_score: 90,
        license_expiry_date: '2028-12-15'
      };
    }
    return d;
  });
  showToast(`Compliance flags for ${driver.name} marked as resolved!`, 'success');
};

const trafficLightBadgeClass = (severity) => {
  if (severity === 'Red') return 'badge-danger';
  if (severity === 'Orange') return 'badge-warning';
  return 'badge-success';
};

// Virtual scroll setup
const historicalLogs = ref([]);
const scrollTop = ref(0);
const rowHeight = 55; 
const viewportHeight = 350;
const safetyFilter = ref('All');

const handleSafetyKpiClick = (filter) => {
  safetyFilter.value = filter;
  showToast(`Filtering audit logs: ${filter}`, 'info');
};

onMounted(() => {
  generateHistoricalLogs();
});

const generateHistoricalLogs = () => {
  const names = ['Sarah Connor', 'Bruce Wayne', 'Alex Johnson', 'Peter Parker', 'Jack Torrance', 'Diana Prince', 'Clark Kent'];
  const events = ['Speeding Alert', 'License Audit Completed', 'Seatbelt Unbuckled Check', 'Fatigue Warning Sensor', 'Route Deviation Checked', 'Brake G-Force Alert'];

  const logs = [];
  for (let i = 1; i <= 2000; i++) {
    const score = Math.floor(Math.random() * 45) + 55;
    const compliance = score >= 90 ? 'Pass' : (score >= 70 ? 'Warn' : 'Fail');
    logs.push({
      id: 5000 + i,
      driver: names[i % names.length],
      event: events[i % events.length],
      score: score,
      compliance: compliance
    });
  }
  historicalLogs.value = logs;
};

const filteredHistoricalLogs = computed(() => {
  if (safetyFilter.value === 'All') return historicalLogs.value;
  return historicalLogs.value.filter(log => {
    if (safetyFilter.value === 'Red') return log.compliance === 'Fail';
    if (safetyFilter.value === 'Orange') return log.compliance === 'Warn';
    return log.compliance === 'Pass';
  });
});

const handleScroll = (e) => {
  scrollTop.value = e.target.scrollTop;
};

const totalListHeight = computed(() => {
  return filteredHistoricalLogs.value.length * rowHeight;
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
  return filteredHistoricalLogs.value.slice(startIndex.value, endIndex.value);
});

const offsetY = computed(() => {
  return startIndex.value * rowHeight;
});

const complianceBadgeClass = (status) => {
  if (status === 'Pass') return 'badge-success';
  if (status === 'Warn') return 'badge-warning';
  return 'badge-danger';
};

const getSafetyClass = (score) => {
  if (score >= 90) return 'excellent';
  if (score >= 70) return 'good';
  return 'risk';
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  cursor: pointer;
}

.kpi-card:hover {
  transform: translateY(-3px);
  border-color: var(--border-hover);
}

.kpi-card:hover .kpi-border,
.kpi-card:hover .kpi-border-red,
.kpi-card:hover .kpi-border-orange {
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

.kpi-border-red {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--danger);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.kpi-border-orange {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--warning);
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* Anomaly alerts */
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

/* Virtual scroll style */
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
</style>
