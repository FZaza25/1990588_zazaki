<template>
  <div class="utility-card">
    <div v-if="loaded.loading" class="d-flex flex-column">
      <div  class="d-flex align-center justify-lg-space-between justify-center flex-wrap">
        <v-icon :icon="props.icon" size="40" class="mr-2"/>
        <h2 class="">{{ t('stream_name.'+props.title) }}</h2>

      </div>
      <div class="d-flex justify-center text-size-large">
        <div  class="d-flex justify-lg-space-between justify-center w-100 align-center">
          <div class="d-flex flex-column">
            <h2>{{ t('metrics.'+selectedMetric?.value?.metric)}}</h2>
            <h2>{{ selectedMetric.value?.value+ ' '+ selectedMetric.value?.unit}}</h2>
          </div>
          <div class="d-flex flex-column h-100 py-4" :class="metrics.length > 1?'justify-space-between':'justify-end'">
            <v-icon v-if="metrics.length >1" icon="mdi-swap-horizontal" @click="()=>changeMetrics()" class="icon-hover ml-2" size="40"/>
            <v-icon v-if="props.openChart" icon="mdi-chart-areaspline" @click="props.openChart" class="icon-hover ml-2" size="40"/>
          </div>

        </div>


      </div>
    </div>
    <div v-else class="d-flex justify-center align-center w-100">
      <v-progress-circular indeterminate color="primary"/>
    </div>

  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {useLoadingStore} from "../../stores/loading.js";
import {ref, watch} from "vue";
import {useStreamsStore} from "../../stores/streams.js";

const {t} = useI18n();

const loaded = useLoadingStore()
const stream = useStreamsStore()

const props = defineProps({
  title: String,
  icon: String,
  value: {
    type: Object,
    default: () => ({})
  },
  openChart: {
    type: Function,
    default: null
  }
})

const metrics = ref([])

const selectedMetric = ref({
  index: 0,
  value: null
})

watch(
  () => selectedMetric.value,
  (nextSelected) => {
    const sourceId = nextSelected?.value?.source_id
    if (!sourceId || !stream.streamsList[sourceId]) return

    const currentSelected = stream.streamsList[sourceId].selected
    const sameMetric = currentSelected?.value?.metric === nextSelected.value.metric
    const sameIndex = currentSelected?.index === nextSelected.index
    if (sameMetric && sameIndex) return

    stream.streamsList[sourceId] = {
      ...stream.streamsList[sourceId],
      selected: {
        index: nextSelected.index,
        value: nextSelected.value
      }
    }
  },
  { deep: true }
)

function changeMetrics() {
  if(selectedMetric.value.index < metrics.value.length-1){
    selectedMetric.value.index = selectedMetric.value.index+1
    selectedMetric.value = {
      ...selectedMetric.value,
      value: metrics.value[selectedMetric.value.index],
    }
  }else{
    selectedMetric.value.index = 0
    selectedMetric.value = {
      ...selectedMetric.value,
      value: metrics.value[0],
    }
  }

}

watch(
  () => props.value,
  (nextValue) => {
    const streamValue = nextValue ?? {}
    const { title, icon, selected, ...metricsValue } = streamValue

    const nextMetrics = Object.values(metricsValue).filter((item) => {
      return item && typeof item === "object" && "metric" in item && "value" in item
    })

    metrics.value = nextMetrics

    if (nextMetrics.length === 0) {
      selectedMetric.value = { index: 0, value: null }
      return
    }

    const currentMetricKey = selectedMetric.value?.value?.metric
    const foundIndex = nextMetrics.findIndex((m) => m.metric === currentMetricKey)
    const safeIndex = foundIndex >= 0
      ? foundIndex
      : Math.min(selectedMetric.value.index ?? 0, nextMetrics.length - 1)

    selectedMetric.value = {
      index: safeIndex,
      value: nextMetrics[safeIndex]
    }
  },
  { deep: true, immediate: true }
)


</script>
