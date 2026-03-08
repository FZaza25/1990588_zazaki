<template>
  <UtilityCard :title="entries.sensor_id" :icon="entries.icon" :value="entries.value + ' ' + entries.unit" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('sensors_name.'+entries.sensor_id)}}
      </h1>
    </template>
    <template #content>
      <GaugeChart :value="sensorsData.charts.water_tank_level" :min="0" :max="4000" :unit="entries.unit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import UtilityCard from "../common/UtilityCard.vue";
import CentralModal from "../common/CentralModal.vue";
import {ref} from "vue";
import {useSensorsStore} from "../../stores/sensors.js";
import {useI18n} from "vue-i18n";
import GaugeChart from "../charts/GaugeChart.vue";

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