<template>
  <StreamCard :title="props.entries.title" :icon="props.entries.icon" :value="props.entries" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('stream_name.'+props.entries.title)}}
      </h1>
    </template>
    <template #content>
      <GaugeChart :value="selectedGaugeValue" :min="0" :max="100" :unit="selectedUnit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import CentralModal from "../common/CentralModal.vue";
import {computed, ref} from "vue";
import {useI18n} from "vue-i18n";
import {useStreamsStore} from "../../stores/streams.js";
import StreamCard from "../common/StreamCard.vue";
import GaugeChart from "../charts/GaugeChart.vue";

const openModal = ref(null)

const stream = useStreamsStore()

const {t} = useI18n();

const props = defineProps({
  entries: Object
})

const selectedMetric = computed(() => props.entries?.selected?.value?.metric)
const selectedUnit = computed(() => props.entries?.selected?.value?.unit ?? '')
const selectedGaugeValue = computed(() => {
  const metric = selectedMetric.value
  if (!metric) return 0

  const sourceCharts = stream.charts?.[props.entries?.title]
  const chartValue = sourceCharts?.[metric]
  if (typeof chartValue === 'number') return chartValue
  if (Array.isArray(chartValue) && chartValue.length > 0) {
    const last = chartValue[chartValue.length - 1]
    return Number.isFinite(Number(last)) ? Number(last) : 0
  }

  const selectedValue = props.entries?.selected?.value?.value
  return Number.isFinite(Number(selectedValue)) ? Number(selectedValue) : 0
})

const openChart = ()=>{
  openModal.value.open()
}

</script>
