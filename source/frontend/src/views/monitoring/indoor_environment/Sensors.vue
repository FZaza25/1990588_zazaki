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
    if(sensor.sensor_id in sensorsData.sensorsList){
      sensorsData.sensorsList[sensor.sensor_id] = {
        ...sensor,
        icon: sensorsData.sensorsList[sensor.sensor_id].icon,
      };
      if(sensorsData.charts[sensor.sensor_id].length > 10){
        sensorsData.charts[sensor.sensor_id].shift()
        sensorsData.charts[sensor.sensor_id].push(sensor.value)
      } else {
        sensorsData.charts[sensor.sensor_id].push(sensor.value)
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