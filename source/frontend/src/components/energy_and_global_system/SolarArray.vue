<template>
  <StreamCard :title="props.entries.sensor_id" :icon="props.entries.icon" :value="props.entries.value + ' ' + props.entries.unit" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('sensors_name.'+props.entries.sensor_id)}}
      </h1>
    </template>
    <template #content>
      <LineCharts :labels="chartTime" :values="stream.charts.solar_array" :yUnit="props.entries.unit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import {chartTime} from "../../data/ChartFunction.js";
import CentralModal from "../common/CentralModal.vue";
import {ref} from "vue";
import {useI18n} from "vue-i18n";
import {useStreamsStore} from "../../stores/streams.js";
import StreamCard from "../common/StreamCard.vue";
import LineCharts from "../charts/LineCharts.vue";

const openModal = ref(null)

const stream = useStreamsStore()

const {t} = useI18n();

const props = defineProps({
  entries: Object
})
console.log(stream.charts)
const openChart = ()=>{
  openModal.value.open()
}

</script>