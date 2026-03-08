<template>
  <UtilityCard :title="entries.sensor_id" :icon="entries.icon" :value="entries.value + ' ' + entries.unit" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('sensors_name.'+entries.sensor_id)}}
      </h1>
    </template>
    <template #content>
      <LineCharts :labels="chartTime" :values="sensorsData.charts.entrance_humidity" :yUnit="entries.unit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import UtilityCard from "../common/UtilityCard.vue";
import {chartTime} from "../../data/ChartFunction.js";
import CentralModal from "../common/CentralModal.vue";
import LineCharts from "../charts/LineCharts.vue";
import {ref} from "vue";
import {useSensorsStore} from "../../stores/sensors.js";
import {useI18n} from "vue-i18n";

const openModal = ref(null)

const sensorsData = useSensorsStore()

const {t} = useI18n();

const props = defineProps({
  entries: Object
})

const openChart = ()=>{
  openModal.value.open()
}

</script>