<template>
  <div class="analytics-container">
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
        <span class="label">{{ metric.title }}</span>
        <span class="value">{{ metric.value }}</span>
        <span class="description">{{ metric.desc }}</span>
      </div>
    </div>

    <!-- Charts / Analysis Blocks -->
    <div class="analytics-grid">
      <!-- Vehicle ROI & Efficiency Registry -->
      <div class="card grid-card">
        <h3>Vehicle ROI &amp; Performance Ranking</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Revenue</th>
              <th>Expenses (Fuel+Maint)</th>
              <th>Acquisition Cost</th>
              <th>ROI %</th>
              <th>Efficiency</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vehicle in roiData" :key="vehicle.regNo">
              <td class="font-bold">{{ vehicle.regNo }}</td>
              <td>${{ vehicle.revenue.toLocaleString() }}</td>
              <td>${{ vehicle.expenses.toLocaleString() }}</td>
              <td>${{ vehicle.acqCost.toLocaleString() }}</td>
              <td class="font-bold" :class="getRoiClass(vehicle.roi)">
                {{ vehicle.roi }}%
              </td>
              <td>{{ vehicle.efficiency }} km/L</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cost Breakdowns -->
      <div class="card cost-breakdown">
        <h3>Top Operational Expenses</h3>
        <div class="bar-chart-simulated">
          <div class="bar-item" v-for="item in expenseItems" :key="item.label">
            <span class="bar-label">{{ item.label }}</span>
            <div class="bar-wrapper">
              <div class="bar-fill" :style="{ width: item.percentage + '%' }"></div>
            </div>
            <span class="bar-value">${{ item.value.toLocaleString() }}</span>
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
  return roi >= 25 ? 'high' : 'medium';
};

const downloadCSV = () => {
  // Generate simple CSV content in browser
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.kpi-card {
  background-color: var(--bg);
  border: 1px solid var(--border);
  padding: 1.25rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
}

.kpi-card .label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text);
  text-transform: uppercase;
}

.kpi-card .value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-h);
  margin: 0.5rem 0;
}

.kpi-card .description {
  font-size: 0.75rem;
  color: var(--text);
}

.analytics-grid {
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

.card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-h);
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

.font-bold { font-weight: 600; }

.font-bold.high { color: #10b981; }
.font-bold.medium { color: #3b82f6; }

.bar-chart-simulated {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.85rem;
}

.bar-label {
  width: 120px;
  color: var(--text-h);
}

.bar-wrapper {
  flex: 1;
  height: 0.75rem;
  background-color: var(--social-bg);
  border-radius: 0.375rem;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background-color: var(--accent);
  border-radius: 0.375rem;
}

.bar-value {
  width: 70px;
  text-align: right;
  font-weight: 600;
  color: var(--text-h);
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

@media (max-width: 1024px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
