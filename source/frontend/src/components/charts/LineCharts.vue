<template>
  <div style="height: 300px">
    <Line :data="data" :options="options" />
  </div>
</template>

<script setup>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] }
})

const data = {
  labels: props.labels,
  datasets: [
    {
      label: 'Telemetry',
      data: props.values,
      borderColor: '#0B304F',
      backgroundColor: 'rgba(11,48,79,0.2)',
      tension: 0.3
    }
  ]
}

const options = {
  responsive: true,
  maintainAspectRatio: false
}
</script>

