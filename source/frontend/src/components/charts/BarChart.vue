
<template>
  <div style="height: 300px;">
    <Bar :data="data" :options="options" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale
)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  datasetLabel: { type: String, default: 'Telemetry' },
  yUnit: { type: String, default: '' },
  xUnit: { type: String, default: 's' },
  barColor: { type: String, default: 'rgba(11, 48, 79, 0.75)' },
  borderColor: { type: String, default: '#0B304F' }
})

const data = computed(() => ({
  labels: [...props.labels],
  datasets: [
    {
      label: props.datasetLabel,
      data: [...props.values],
      backgroundColor: props.barColor,
      borderColor: props.borderColor,
      borderWidth: 1,
      borderRadius: 6,
      maxBarThickness: 36
    }
  ]
}))

const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => {
          const v = ctx.parsed.y
          return `${v}${props.yUnit ? ` ${props.yUnit}` : ''}`
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        callback: (value, index) => {
          const l = props.labels[index]
          return `${l}${props.xUnit ? ` ${props.xUnit}` : ''}`
        }
      }
    },
    y: {
      beginAtZero: true,
      ticks: {
        callback: (v) => `${v}${props.yUnit ? ` ${props.yUnit}` : ''}`
      }
    }
  }
}))
</script>
