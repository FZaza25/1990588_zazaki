<template>
  <StreamCard :title="props.entries.source_id" :icon="props.entries.icon" :value="props.entries.value + ' ' + props.entries.unit" :openChart="()=>openChart()"/>
  <CentralModal ref="openModal">
    <template #header>
      <h1>
        {{t('stream_name.'+props.entries.sensor_id)}}
      </h1>
    </template>
    <template #content>
      <GaugeChart :value="stream.charts.life_support" :min="0" :max="100" :unit="props.entries.unit"/>
    </template>
  </CentralModal>
</template>

<script setup>

import CentralModal from "../common/CentralModal.vue";
import {ref} from "vue";
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

const openChart = ()=>{
  openModal.value.open()
}

</script>