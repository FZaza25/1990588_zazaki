<template>
  <div class="title">
    <h2>{{ t('sensors') }}</h2>
    <div class="d-flex flex-column">
      <div class="d-flex ga-4">
        <GreenhouseTemp :entries="sensorsData?.greenhouse_temperature" />
        <Humidity :entries="sensorsData?.entrance_humidity"/>
        <Co2Hall :entries="sensorsData?.co2_hall"/>
      </div>
      <div class="d-flex ga-4 pt-4">
        <CorridorPressure :entries="sensorsData?.corridor_pressure" />
        <AirQualityPM25 :entries="sensorsData?.air_quality_pm25"/>
        <AirQualityVoc :entries="sensorsData?.air_quality_voc"/>
      </div>
    </div>


  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {onMounted,onUnmounted, ref} from "vue";
import { api } from '../../../api/Request.js'
import GreenhouseTemp from "../../../components/indoor_environment/GreenhouseTemp.vue";
import Humidity from "../../../components/indoor_environment/Humidity.vue";
import Co2Hall from "../../../components/indoor_environment/Co2Hall.vue";
import CorridorPressure from "../../../components/indoor_environment/CorridorPressure.vue";
import AirQualityPM25 from "../../../components/indoor_environment/AirQualityPM25.vue";
import AirQualityVoc from "../../../components/indoor_environment/AirQualityVoc.vue";

const sensorsData = ref({
  corridor_pressure: {
    icon: 'mdi-car-brake-low-pressure'
  },
  co2_hall: {
    icon: 'mdi-molecule-co2'
  },
  greenhouse_temperature: {
    icon: 'mdi-thermometer'
  },
  air_quality_pm25: {
    icon: 'mdi-weather-cloudy'
  },
  air_quality_voc: {
    icon: 'mdi-weather-cloudy'
  },
  entrance_humidity: {
    icon: 'mdi-water-percent'
  },
})

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
  console.log(sensorsData.value)
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