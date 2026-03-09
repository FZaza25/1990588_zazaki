<template>
  <div class="title">
    <h2>{{ t('stream') }}</h2>
    <div class="d-flex flex-column overflow-hidden">
      <div class="d-flex ga-2">
        <SolarArray :entries="stream?.streamsList?.solar_array"/>
        <Radation :entries="stream?.streamsList?.radiation"/>
        <LifeSupport :entries="stream?.streamsList?.life_support"/>
      </div>
      <div class="d-flex ga-2 pt-4">
        <PowerBus :entries="stream?.streamsList?.power_bus"/>
        <PowerConsumption :entries="stream?.streamsList?.power_consumption"/>
        <ThermalLoop :entries="stream?.streamsList?.thermal_loop"/>
      </div>
      <div class="d-flex mr-7 pt-4">
        <AirLock :entries="stream?.streamsList?.airlock"/>
      </div>
    </div>

  </div>
</template>

<script setup>
import {onMounted, onUnmounted, ref, watch} from 'vue'
import { useI18n } from 'vue-i18n'
import { TelemetrySocket,isTelemetryEvent } from '../../../api/TelemetryWebSocket.js'
import SolarArray from "../../../components/energy_and_global_system/SolarArray.vue";
import Radation from "../../../components/energy_and_global_system/Radation.vue";
import LifeSupport from "../../../components/energy_and_global_system/LifeSupport.vue";
import PowerBus from "../../../components/energy_and_global_system/PowerBus.vue";
import PowerConsumption from "../../../components/energy_and_global_system/PowerConsumption.vue";
import ThermalLoop from "../../../components/energy_and_global_system/ThermalLoop.vue";
import AirLock from "../../../components/energy_and_global_system/AirLock.vue";
import {useStreamsStore} from "../../../stores/streams.js";
import {useLoadingStore} from "../../../stores/loading.js";

const { t } = useI18n()
const status = ref('idle')
const stream = useStreamsStore()

const loading = useLoadingStore()

let socket = null

onMounted(() => {
  socket = new TelemetrySocket({
    onStatus: (s) => {
      status.value = s
      loading.loading = ( s === 'open')
    },
    onError: (e) => { console.error('WS error', e) },
    onMessage: (evt) => {
    // console.log('WS message', evt)
      if (!isTelemetryEvent(evt)) return
      if (!(evt.source_id in stream.streamsList)) return

      stream.streamsList[evt.source_id] = {
        ...stream.streamsList[evt.source_id],
        [evt.metric]: {
          ...evt,
        },
        icon: stream.streamsList[evt.source_id].icon,
      }

      const sourceCharts = stream.charts?.[evt.source_id]
      if (!sourceCharts || !(evt.metric in sourceCharts)) return

      const rawValue = evt.value
      const normalizedValue =
        typeof rawValue === 'string' && rawValue.trim() !== '' && !Number.isNaN(Number(rawValue))
          ? Number(rawValue)
          : rawValue

      const currentMetricChart = sourceCharts[evt.metric]
      if (Array.isArray(currentMetricChart)) {
        const nextSeries = [...currentMetricChart, normalizedValue]
        if (nextSeries.length > 11) nextSeries.shift()

        stream.charts[evt.source_id] = {
          ...sourceCharts,
          [evt.metric]: nextSeries
        }
      } else {
        stream.charts[evt.source_id] = {
          ...sourceCharts,
          [evt.metric]: normalizedValue
        }
      }

    }

  })

  socket.connect()
})


onUnmounted(() => {
  socket?.disconnect()
})
</script>
