<template>
  <StreamCard :title="props.entries.title" :icon="props.entries.icon" :value="props.entries" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{ selectedMetric ? t('metrics.' + selectedMetric) : '' }}
      </h1>
    </template>
    <template #content>
      <AreaChart :labels="chartTime" :values="selectedChartValues" :yUnit="selectedUnit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import {chartTime} from "../../data/ChartFunction.js";
import CentralModal from "../common/CentralModal.vue";
import {computed, ref} from "vue";
import {useI18n} from "vue-i18n";
import {useStreamsStore} from "../../stores/streams.js";
import StreamCard from "../common/StreamCard.vue";
import AreaChart from "../charts/AreaChart.vue";

const openModal = ref(null)

const stream = useStreamsStore()

const {t} = useI18n();

const props = defineProps({
  entries: Object
})

const selectedMetric = computed(() => props.entries?.selected?.value?.metric)
const selectedUnit = computed(() => props.entries?.selected?.value?.unit ?? '')
const selectedChartValues = computed(() => {
  const metric = selectedMetric.value
  if (!metric) return []
  const series = stream.charts?.[props.entries?.title]?.[metric]
  return Array.isArray(series) ? series : []
})

const openChart = ()=>{
  openModal.value.open()
}

</script>
