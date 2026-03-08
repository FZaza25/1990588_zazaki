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

import {computed} from 'vue'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  yUnit: { type: String, default: '' },
  xUnit: { type: String, default: 's' },
})


const data = computed(() => ({
  labels: [...props.labels],
  datasets: [
    {
      data: [...props.values],
      borderColor: '#0B304F',
      backgroundColor: 'rgba(11,48,79,0.2)',
      tension: 0.3
    }
  ]
}))

const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      ticks: {
        callback: (value, index) => `${props.labels[index]} ${props.xUnit}`.trim()
      }
    },
    y: {
      ticks: {
        callback: (v) => `${v} ${props.yUnit}`.trim()
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: (ctx) => `${ctx.parsed.y} ${props.yUnit}`.trim()
      }
    },
    legend: {
      display: false
    }

  }
}))
</script>

