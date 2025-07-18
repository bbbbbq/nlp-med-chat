<template>
  <div class="stats-container">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载统计数据...</p>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="fetchStatistics" class="retry-button">重试</button>
    </div>
    
    <!-- Data Display -->
    <div v-else>
      <!-- Summary Cards -->
      <div class="summary-grid">
        <div class="summary-card">
          <h4>总医生数</h4>
          <p>{{ totalDoctors }}</p>
        </div>
        <div class="summary-card">
          <h4>总患者数</h4>
          <p>{{ totalPatients }}</p>
        </div>
        <div class="summary-card">
          <h4>总病例数</h4>
          <p>{{ totalDiagnoses }}</p>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-grid">
        <div class="chart-card">
          <h3>医生数量增长趋势</h3>
          <v-chart class="chart" :option="doctorOptions" autoresize />
        </div>
        <div class="chart-card">
          <h3>患者数量增长趋势</h3>
          <v-chart class="chart" :option="patientOptions" autoresize />
        </div>
        <div class="chart-card">
          <h3>每日病例生成趋势</h3>
          <v-chart class="chart" :option="diagnosesOptions" autoresize />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent, DataZoomComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import axios from 'axios';

use([
  CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, DataZoomComponent
]);

const doctorData = ref([]);
const patientData = ref([]);
const diagnosesData = ref([]);

const totalDoctors = computed(() => doctorData.value.reduce((sum, item) => sum + item.count, 0));
const totalPatients = computed(() => patientData.value.reduce((sum, item) => sum + item.count, 0));
const totalDiagnoses = computed(() => diagnosesData.value.reduce((sum, item) => sum + item.count, 0));

const createChartOptions = (data, color) => {
  if (!data || data.length === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: { color: '#999', fontSize: 16 }
      }
    };
  }
  
  const dates = data.map(item => {
    const date = new Date(item.date);
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  });
  const counts = data.map(item => item.count);

  return {
    grid: { top: 40, right: 40, bottom: 60, left: 50 },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: '#333', textStyle: { color: '#fff' } },
    xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#ccc' } }, axisLabel: { color: '#555' } },
    yAxis: { type: 'value', axisLine: { show: true, lineStyle: { color: '#ccc' } }, splitLine: { lineStyle: { type: 'dashed' } } },
    dataZoom: [{ type: 'inside', start: 0, end: 100 }, { type: 'slider', height: 20, start: 0, end: 100 }],
    series: [{
      data: counts,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: color.line },
      lineStyle: { width: 3, color: color.line },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: color.areaStart }, { offset: 1, color: color.areaEnd }]
        }
      }
    }]
  };
};

const doctorOptions = computed(() => createChartOptions(doctorData.value, { line: '#5470C6', areaStart: 'rgba(84, 112, 198, 0.3)', areaEnd: 'rgba(84, 112, 198, 0)' }));
const patientOptions = computed(() => createChartOptions(patientData.value, { line: '#91CC75', areaStart: 'rgba(145, 204, 117, 0.3)', areaEnd: 'rgba(145, 204, 117, 0)' }));
const diagnosesOptions = computed(() => createChartOptions(diagnosesData.value, { line: '#FAC858', areaStart: 'rgba(250, 200, 88, 0.3)', areaEnd: 'rgba(250, 200, 88, 0)' }));

const loading = ref(true);
const error = ref(null);

const fetchStatistics = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const response = await axios.get('http://127.0.0.1:3000/statistics');
    if (response.data.success) {
      doctorData.value = response.data.doctors || [];
      patientData.value = response.data.patients || [];
      diagnosesData.value = response.data.diagnoses || [];
      
      console.log('Statistics loaded:', {
        doctors: doctorData.value.length,
        patients: patientData.value.length,
        diagnoses: diagnosesData.value.length
      });
    } else {
      error.value = '获取统计数据失败';
    }
  } catch (err) {
    console.error('Error fetching statistics:', err);
    error.value = '网络错误，无法获取统计数据';
  } finally {
    loading.value = false;
  }
};

onMounted(fetchStatistics);
</script>

<style scoped>
.stats-container {
  padding: 2rem;
  background-color: #f0f2f5;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #5470C6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #666;
}

.error-message {
  color: #ff4d4f;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.retry-button {
  background: #5470C6;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background: #4c63d2;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.summary-card {
  background: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.summary-card h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #666;
  font-weight: 600;
}

.summary-card p {
  margin: 0;
  font-size: 2.25rem;
  font-weight: 700;
  color: #333;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.chart-card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.chart-card h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.chart {
  height: 350px;
}
</style>
