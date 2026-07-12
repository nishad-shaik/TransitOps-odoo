<template>
  <div class="analytics-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Reports &amp; Analytics</h1>
        <p class="subtitle">Evaluate vehicle ROI, fuel efficiency, and download reports</p>
      </div>
      <button @click="downloadCSV" class="btn-primary">Export CSV</button>
    </div>

    <!-- Derived Metrics Cards -->
    <div class="kpi-grid">
      <div class="kpi-card" v-for="metric in metrics" :key="metric.title">
        <div class="metric-top">
          <span class="label">{{ metric.title }}</span>
        </div>
        <span class="value">{{ metric.value }}</span>
        <span class="description">{{ metric.desc }}</span>
      </div>
    </div>

    <!-- Grid Layout -->
    <div class="analytics-grid">
      <!-- Vehicle ROI & Performance Registry -->
      <div class="card grid-card">
        <h3>Vehicle ROI &amp; Performance Ranking</h3>
        <p class="card-subtitle">Detailed breakdown of acquisition costs, operational costs, and ROI metrics</p>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Revenue</th>
                <th>Expenses</th>
                <th>Acq. Cost</th>
                <th>ROI %</th>
                <th>Efficiency</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="vehicle in roiData" :key="vehicle.regNo">
                <td class="font-bold highlight-text">{{ vehicle.regNo }}</td>
                <td>${{ vehicle.revenue.toLocaleString() }}</td>
                <td>${{ vehicle.expenses.toLocaleString() }}</td>
                <td>${{ vehicle.acqCost.toLocaleString() }}</td>
                <td class="font-bold" :class="getRoiClass(vehicle.roi)">
                  {{ vehicle.roi }}%
                </td>
                <td>
                  <span class="efficiency-value">{{ vehicle.efficiency }} km/L</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Cost Breakdowns -->
      <div class="card cost-breakdown">
        <h3>Top Operational Expenses</h3>
        <p class="card-subtitle">Proportional breakdown of monthly costs</p>
        <div class="bar-chart-simulated">
          <div class="bar-item" v-for="item in expenseItems" :key="item.label">
            <div class="bar-info">
              <span class="bar-label">{{ item.label }}</span>
              <span class="bar-value">${{ item.value.toLocaleString() }}</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill" :style="{ width: item.percentage + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const metrics = ref([
  { title: 'Avg Fuel Efficiency', value: '7.8 km/L', desc: 'Combined fleet average' },
  { title: 'Active Fleet Utilization', value: '78.2%', desc: 'Assigned vs idle vehicles' },
  { title: 'Total Operational Cost', value: '$22,450', desc: 'This month rollup' },
  { title: 'Fleet Average ROI', value: '18.4%', desc: 'Based on initial costs' }
]);

const roiData = ref([
  { regNo: 'VAN-05', revenue: 12000, expenses: 950, acqCost: 35000, roi: 31.5, efficiency: 11.2 },
  { regNo: 'TRK-02', revenue: 45000, expenses: 3800, acqCost: 145000, roi: 28.4, efficiency: 4.8 },
  { regNo: 'SDN-01', revenue: 4800, expenses: 320, acqCost: 28000, roi: 16.0, efficiency: 15.6 }
]);

const expenseItems = ref([
  { label: 'Fuel Expenses', value: 12450, percentage: 85 },
  { label: 'Scheduled Maintenance', value: 3800, percentage: 40 },
  { label: 'Unscheduled Repairs', value: 2100, percentage: 22 },
  { label: 'Tolls & Fees', value: 1200, percentage: 12 }
]);

const getRoiClass = (roi) => {
  return roi >= 25 ? 'text-success' : 'text-info';
};

const downloadCSV = () => {
  let csvContent = 'data:text/csv;charset=utf-8,';
  csvContent += 'Vehicle,Revenue,Expenses,AcqCost,ROI,Efficiency\n';
  
  roiData.value.forEach(row => {
    csvContent += `${row.regNo},${row.revenue},${row.expenses},${row.acqCost},${row.roi},${row.efficiency}\n`;
  });
  
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', 'TransitOps_Performance_Report.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
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
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-hover);
}

.kpi-card .label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-card .value {
  font-size: 2.25rem;
  font-weight: 800;
  color: #fff;
  margin: 0.5rem 0;
}

.kpi-card .description {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.analytics-grid {
  display: grid;
  grid-template-columns: 1.8fr 1fr;
  gap: 1.75rem;
}

.card h3 {
  margin: 0;
}

.card-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
  margin-bottom: 1.5rem;
}

.table-wrapper {
  overflow-x: auto;
}

.font-bold { font-weight: 700; }
.highlight-text { color: #fff; }

.text-success { color: var(--success); }
.text-info { color: var(--info); }

.efficiency-value {
  background-color: rgba(255,255,255,0.03);
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
}

.bar-chart-simulated {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.bar-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bar-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.bar-label {
  color: var(--text-primary);
  font-weight: 600;
}

.bar-wrapper {
  height: 0.6rem;
  background-color: var(--border-color);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, #a855f7 100%);
  border-radius: var(--border-radius-sm);
  transition: width 1s ease-in-out;
}

.bar-value {
  font-weight: 700;
  color: #fff;
}

@media (max-width: 1100px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
