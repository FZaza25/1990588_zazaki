<template>
  <div class="title">
    <h2>{{ t('stream') }}</h2>
    <p>WS: {{ status }}</p>
<!--    <div class="d-flex flex-column">-->
<!--      <div class="d-flex ga-4">-->
<!--        <SolarArray/>-->
<!--        <Radation/>-->
<!--        <LifeSupport/>-->
<!--      </div>-->
<!--      <div class="d-flex ga-4">-->
<!--        <PowerBus/>-->
<!--        <PowerConsumption/>-->
<!--        <ThermalLoop/>-->
<!--      </div>-->
<!--      <div class="d-flex ga-4">-->
<!--        <AirLock/>-->
<!--      </div>-->
<!--    </div>-->

  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { TelemetrySocket,isTelemetryEvent } from '../../../api/TelemetryWebSocket.js'
import SolarArray from "../../../components/energy_and_global_system/SolarArray.vue";
import Radation from "../../../components/energy_and_global_system/Radation.vue";
import LifeSupport from "../../../components/energy_and_global_system/LifeSupport.vue";
import PowerBus from "../../../components/energy_and_global_system/PowerBus.vue";
import PowerConsumption from "../../../components/energy_and_global_system/PowerConsumption.vue";
import ThermalLoop from "../../../components/energy_and_global_system/ThermalLoop.vue";
import AirLock from "../../../components/energy_and_global_system/AirLock.vue";

const { t } = useI18n()
const status = ref('idle')
const events = ref([])

let socket = null

onMounted(() => {
  socket = new TelemetrySocket({
    onStatus: (s) => { status.value = s },
    onError: (e) => { console.error('WS error', e) },
    onMessage: (evt) => {
      if (!isTelemetryEvent(evt)) return
      events.value.unshift(evt)
      if (events.value.length > 200) events.value.pop()
    },
  })

  socket.connect()
})


onUnmounted(() => {
  socket?.disconnect()
})
</script>