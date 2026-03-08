<template>
  <UtilityCard :title="entries.sensor_id" :icon="entries.icon" :value="entries.value + ' ' + entries.unit" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('sensors_name.'+entries.sensor_id)}}
      </h1>
    </template>
    <template #content>
      <LineCharts :labels="chartTime" :values="sensorsData.charts.greenhouse_temperature"/>
    </template>
  </CentralModal>
</template>

<script setup>

import UtilityCard from "../common/UtilityCard.vue";
import CentralModal from "../common/CentralModal.vue";
import {ref, watchEffect} from "vue";
import {useI18n} from "vue-i18n";
import LineCharts from "../charts/LineCharts.vue";
import {computeTime} from "../../data/ChartFunction.js";
import {useSensorsStore} from "../../stores/sensors.js";



const openModal = ref(null)

const chartTime = ref(null)

const sensorsData = useSensorsStore()

const {t} = useI18n();

const props = defineProps({
  entries: Object
})

const openChart = ()=>{
  chartTime.value = computeTime(sensorsData.charts.greenhouse_temperature)
  openModal.value.open()
}

watchEffect(()=>{
  console.log(sensorsData.charts.greenhouse_temperature)
  console.log(computeTime(sensorsData.charts.greenhouse_temperature))
})
</script>