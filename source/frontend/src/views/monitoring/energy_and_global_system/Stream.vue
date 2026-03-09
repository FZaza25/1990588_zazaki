<template>
  <div class="title">
    <h2>{{ t('stream') }}</h2>
    <p>{{status}}</p>
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

      // if (!isTelemetryEvent(evt)) return
      // if (!(evt.tags.subsystem in stream.streamsList)) return


      stream.streamsList[evt.tags.subsystem] = {
        ...stream.streamsList[evt.tags.subsystem],
        ...evt,
        icon: stream.streamsList[evt.tags.subsystem].icon,
      }

      if(evt.tags.subsystem !== 'life_support'){
        if(stream.charts[evt.tags.subsystem].length > 10){
          stream.charts[evt.tags.subsystem].shift()
          stream.charts[evt.tags.subsystem].push(evt.value)
        } else {
          stream.charts[evt.tags.subsystem].push(evt.value)
        }
      } else {
        stream.charts[evt.tags.subsystem] = Number(evt.value)
      }

    }

  })

  socket.connect()
})


onUnmounted(() => {
  socket?.disconnect()
})
</script>
