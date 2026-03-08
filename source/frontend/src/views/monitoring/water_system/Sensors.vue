<template>
  <div class="title">
    <h2>{{ t('sensors') }}</h2>
    <div class="d-flex flex-column">
      <div class="d-flex ga-4">
        <HydroponicPH :entries="sensorsData?.hydroponic_ph" />
        <WaterTankLevel :entries="sensorsData?.water_tank_level"/>
      </div>
    </div>


  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {onMounted,onUnmounted, ref} from "vue";
import { api } from '../../../api/Request.js'
import HydroponicPH from "../../../components/water_systems/HydroponicPH.vue";
import WaterTankLevel from "../../../components/water_systems/WaterTankLevel.vue";
import {useLoadingStore} from "../../../stores/loading.js";

const sensorsData = ref({
  hydroponic_ph: {
    icon: 'mdi-ph'
  },
  water_tank_level: {
    icon: 'mdi-chart-waterfall'
  }
})

const loaded = useLoadingStore()

const {t} = useI18n();

let intervalId

const handleData = (data) => {
  data.map(sensor => {
    if(sensor.sensor_id in sensorsData.value){
      sensorsData.value[sensor.sensor_id] = {
        ...sensor,
        icon: sensorsData.value[sensor.sensor_id].icon,
      };
    }
  })
  loaded.loading = true;
}

const get = async () => {
  try {
    const response = await api.get('/api/state')
    handleData(response)
  }catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  await get()

  intervalId = setInterval(async () => {
    await get()
  }, 5000)

})

onUnmounted(() => {
  clearInterval(intervalId)
})


</script>