<template>
  <UtilityCard :title="props.entries.source_id" :icon="props.entries.icon" :value="props.entries.value + ' ' + props.entries.unit" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('sensors_name.'+props.entries.source_id)}}
      </h1>
    </template>
    <template #content>
      <GaugeChart :value="sensorsData.charts.water_tank_level" :min="0" :max="100" :unit="'%'"/>
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