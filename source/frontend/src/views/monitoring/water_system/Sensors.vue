<template>
  <div class="title">
    <h2>{{ t('sensors') }}</h2>
    <div class="d-flex flex-column">
      <div class="d-flex ga-2">
        <HydroponicPH :entries="sensorsData?.sensorsList?.hydroponic_ph" />
        <WaterTankLevel :entries="sensorsData?.sensorsList?.water_tank_level"/>
      </div>
    </div>


  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {onMounted,onUnmounted} from "vue";
import { api } from '../../../api/Request.js'
import HydroponicPH from "../../../components/water_systems/HydroponicPH.vue";
import WaterTankLevel from "../../../components/water_systems/WaterTankLevel.vue";
import {useLoadingStore} from "../../../stores/loading.js";
import {useSensorsStore} from "../../../stores/sensors.js";
import {CHART_MAX_POINTS} from "../../../data/ChartFunction.js";

const sensorsData = useSensorsStore()

const loaded = useLoadingStore()

const {t} = useI18n();

let intervalId

const handleData = (data) => {
  data.map(sensor => {
    if(sensor.series_id === 'air_quality_pm25:pm1' || sensor.series_id === 'air_quality_pm25:pm10' || sensor.series_id === 'air_quality_voc:co2e_ppm') return;

    if(sensor.source_id in sensorsData.sensorsList){
      if(sensor.series_id !== 'water_tank_level:level_pct'){
        sensorsData.sensorsList[sensor.source_id] = {
          ...sensor,
          icon: sensorsData.sensorsList[sensor.source_id].icon,
        };
      }


      if(sensor.source_id !== 'air_quality_voc' && sensor.source_id !== 'water_tank_level'){
        if(sensorsData.charts[sensor.source_id].length >= CHART_MAX_POINTS){
          sensorsData.charts[sensor.source_id].shift()
          sensorsData.charts[sensor.source_id].push(sensor.value)
        } else {
          sensorsData.charts[sensor.source_id].push(sensor.value)
        }
      } else {
        if(sensor.source_id === 'water_tank_level'){
          sensorsData.charts[sensor.source_id] = Number(sensor.value)
        } else {
          const numericValue = Number(sensor.value)
          sensorsData.charts[sensor.source_id] = Number.isFinite(numericValue) ? numericValue : 0
        }

      }
    }
  })
  if(data.length > 0){
    loaded.loading = true
  }

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
