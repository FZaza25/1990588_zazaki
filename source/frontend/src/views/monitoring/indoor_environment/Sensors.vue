<template>
  <div class="title">
    <h2>{{ t('sensors') }}</h2>
    <div class="d-flex flex-column">
      <div class="d-flex ga-2">
        <GreenhouseTemp :entries="sensorsData?.sensorsList?.greenhouse_temperature" />
        <Humidity :entries="sensorsData?.sensorsList?.entrance_humidity"/>
        <Co2Hall :entries="sensorsData?.sensorsList?.co2_hall"/>
      </div>
      <div class="d-flex ga-2 pt-4">
        <CorridorPressure :entries="sensorsData?.sensorsList?.corridor_pressure" />
        <AirQualityPM25 :entries="sensorsData?.sensorsList?.air_quality_pm25"/>
        <AirQualityVoc :entries="sensorsData?.sensorsList?.air_quality_voc"/>
      </div>
    </div>


  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {onMounted,onUnmounted} from "vue";
import { api } from '../../../api/Request.js'
import GreenhouseTemp from "../../../components/indoor_environment/GreenhouseTemp.vue";
import Humidity from "../../../components/indoor_environment/Humidity.vue";
import Co2Hall from "../../../components/indoor_environment/Co2Hall.vue";
import CorridorPressure from "../../../components/indoor_environment/CorridorPressure.vue";
import AirQualityPM25 from "../../../components/indoor_environment/AirQualityPM25.vue";
import AirQualityVoc from "../../../components/indoor_environment/AirQualityVoc.vue";
import {useLoadingStore} from "../../../stores/loading.js";
import {useSensorsStore} from "../../../stores/sensors.js";

const sensorsData = useSensorsStore()

const {t} = useI18n();

let intervalId

const loaded = useLoadingStore()

const handleData = (data) => {
  data.map(sensor => {
    if(sensor.series_id === 'air_quality_pm25:pm1' || sensor.series_id === 'air_quality_pm25:pm10' || sensor.series_id === 'air_quality_voc:co2e_ppm') return;

    if(sensor.source_id in sensorsData.sensorsList){
      sensorsData.sensorsList[sensor.source_id] = {
        ...sensor,
        icon: sensorsData.sensorsList[sensor.source_id].icon,
      };

      if(sensor.source_id !== 'air_quality_voc' && sensor.source_id !== 'water_tank_level'){
        if(sensorsData.charts[sensor.source_id].length > 10){
          sensorsData.charts[sensor.source_id].shift()
          sensorsData.charts[sensor.source_id].push(sensor.value)
        } else {
          sensorsData.charts[sensor.source_id].push(sensor.value)
        }
      } else {
        if(sensor.source_id !== 'water_tank_level'){
          if(sensor.unit === 'L'){
            sensorsData.charts[sensor.source_id] = {
              ...sensorsData.charts[sensor.source_id],
              liters: sensorsData.charts[sensor.source_id].liters.push(sensor.value)
            }
          }else{
            sensorsData.charts[sensor.source_id] = {
              ...sensorsData.charts[sensor.source_id],
              pct: sensorsData.charts[sensor.source_id].pct.push(Number(sensor.value))
            }
          }
        }else{
          sensorsData.charts[sensor.source_id] = Number(sensor.value)
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