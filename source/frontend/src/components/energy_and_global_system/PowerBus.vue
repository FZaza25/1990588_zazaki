<template>
  <StreamCard :title="entries.sensor_id" :icon="entries.icon" :value="entries.value + ' ' + entries.unit" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('sensors_name.'+entries.sensor_id)}}
      </h1>
    </template>
    <template #content>
      <BarChart :labels="chartTime" :values="stream.charts.air_quality_pm25" :yUnit="entries.unit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import UtilityCard from "../common/UtilityCard.vue";
import {chartTime} from "../../data/ChartFunction.js";
import CentralModal from "../common/CentralModal.vue";
import {ref} from "vue";
import {useI18n} from "vue-i18n";
import BarChart from "../charts/BarChart.vue";
import {useStreamsStore} from "../../stores/streams.js";
import StreamCard from "../common/StreamCard.vue";

const openModal = ref(null)

const stream = useStreamsStore()

const {t} = useI18n();

const props = defineProps({
  entries: Object
})

const openChart = ()=>{
  openModal.value.open()
}

</script>