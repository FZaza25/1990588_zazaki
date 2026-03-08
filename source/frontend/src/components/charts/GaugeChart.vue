<template>
  <div style="height: 260px; position: relative;">
    <Doughnut :data="data" :options="options" />
    <div
        style="
        position: absolute;
        left: 50%;
        bottom: 22px;
        transform: translateX(-50%);
        text-align: center;
      "
    >
      <div style="font-size: 28px; font-weight: 700; line-height: 1;">
        {{ displayValue }}
      </div>
      <div style="font-size: 12px; opacity: 0.75;">
        {{ unit }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  value: { type: Number, default: 0 },
  min: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  unit: { type: String, default: '' },
  decimals: { type: Number, default: 1 },
  color: { type: String, default: '#0B304F' },
  trackColor: { type: String, default: 'rgba(11, 48, 79, 0.15)' }
})

console.log(props.value)

const clamped = computed(() => {
  const v = Number(props.value)
  if (!Number.isFinite(v)) return props.min
  return Math.min(props.max, Math.max(props.min, v))
})

const range = computed(() => Math.max(1, props.max - props.min))
const progress = computed(() => clamped.value - props.min)
const remaining = computed(() => range.value - progress.value)

const data = computed(() => ({
  labels: ['Value', 'Remaining'],
  datasets: [
    {
      data: [progress.value, remaining.value],
      backgroundColor: [props.color, props.trackColor],
      borderWidth: 0,
      cutout: '75%',
      circumference: 180,
      rotation: 270
    }
  ]
}))

const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false }
  }
}))

const displayValue = computed(() => clamped.value.toFixed(props.decimals))
const unit = computed(() => props.unit)
</script>
