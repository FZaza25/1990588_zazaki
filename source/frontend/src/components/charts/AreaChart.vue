<template>
  <div style="height: 300px;">
    <Line :data="data" :options="options" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
} from 'chart.js'

ChartJS.register(
    Title,
    Tooltip,
    Legend,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Filler
)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  datasetLabel: { type: String, default: 'Telemetry' },
  yUnit: { type: String, default: '' },
  xUnit: { type: String, default: 's' },
  borderColor: { type: String, default: '#0B304F' },
  fillColor: { type: String, default: 'rgba(11, 48, 79, 0.22)' }
})

const data = computed(() => ({
  labels: [...props.labels],
  datasets: [
    {
      label: props.datasetLabel,
      data: [...props.values],
      borderColor: props.borderColor,
      backgroundColor: props.fillColor,
      fill: true,
      tension: 0.35,
      pointRadius: 2,
      pointHoverRadius: 4
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
      ticks: {
        callback: (v) => `${v}${props.yUnit ? ` ${props.yUnit}` : ''}`
      }
    }
  }
}))
</script>
