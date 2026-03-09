<template>
  <div class="utility-card">
    <div class="d-flex flex-column">
      <div class="d-flex align-center justify-lg-space-between justify-center flex-wrap">
        <v-icon :icon="props.icon" size="40" class="mr-2"/>
        <h2 class="">{{ t('stream_name.'+props.title) }}</h2>

      </div>
      <div class="d-flex justify-center text-size-large">
        <div  v-if="loaded.loading" class="d-flex justify-lg-space-between justify-center w-100 align-center">
          <div class="d-flex flex-column">
            <h2>{{ t('metrics.'+selectedMetric.value?.metric)}}</h2>
            <h2>{{ selectedMetric.value.value+ ' '+ selectedMetric.value.unit}}</h2>
          </div>
          <div class="d-flex flex-column h-100 py-4" :class="metrics.length > 1?'justify-space-between':'justify-end'">
            <v-icon v-if="metrics.length >1" icon="mdi-swap-horizontal" @click="()=>changeMetrics()" class="icon-hover ml-2" size="40"/>
            <v-icon v-if="props.openChart" icon="mdi-chart-areaspline" @click="props.openChart" class="icon-hover ml-2" size="40"/>
          </div>

        </div>

        <v-progress-circular indeterminate color="primary" v-else/>
      </div>
    </div>

  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {useLoadingStore} from "../../stores/loading.js";
import {ref, watch} from "vue";

const {t} = useI18n();

const loaded = useLoadingStore()

const props = defineProps({
  title: String,
  icon: String,
  value: String,
  openChart: {
    type: Function,
    default: null
  }
})

const metrics = ref([])

const selectedMetric = ref({
  index: null,
  value: null
})

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

watch(()=>metrics.value, ()=> {
  if (metrics.value.length > 0 && selectedMetric.value.value !== null) {
    selectedMetric.value = {
     ...selectedMetric.value,
      value: metrics.value[selectedMetric.value.index],
    }
  }
})

watch(()=>props.value, ()=> {
  const {title, icon, ...metricsValue} = props.value
  metrics.value = Object.values(metricsValue)

  if (metrics.value.length > 0 && selectedMetric.value.value === null) {
    selectedMetric.value = {
      index: 0,
      value: metrics.value[0]
    }
  }
},{deep:true})


</script>