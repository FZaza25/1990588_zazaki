<template>
  <StreamCard :title="props.entries.title" :icon="props.entries.icon" :value="props.entries" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('stream_name.'+props.entries.title)}}
      </h1>
    </template>
    <template #content>
      <LineCharts :labels="chartTime" :values="stream.charts.radiation" :yUnit="props.entries.unit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import {chartTime} from "../../data/ChartFunction.js";
import CentralModal from "../common/CentralModal.vue";
import {ref, watch} from "vue";
import {useI18n} from "vue-i18n";
import BarChart from "../charts/BarChart.vue";
import {useStreamsStore} from "../../stores/streams.js";
import StreamCard from "../common/StreamCard.vue";
import LineCharts from "../charts/LineCharts.vue";

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