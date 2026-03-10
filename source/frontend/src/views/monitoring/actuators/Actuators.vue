<template>
  <div>
    <CoolingFanTable :header="headers" :items="tables.cooling_fan"/>
    <HabitatHeaterTable :header="headers" :items="tables.habitat_heater" />
    <EntranceHumidifierTable :header="headers" :items="tables.entrance_humidifier" />
    <HallVentilationTable :header="headers" :items="tables.hall_ventilation" />
  </div>
</template>

<script setup>
import {onMounted, ref} from "vue";
import {api} from "../../../api/Request.js";
import CoolingFanTable from "../../../components/actuators/CoolingFanTable.vue";
import HabitatHeaterTable from "../../../components/actuators/HabitatHeaterTable.vue";
import EntranceHumidifierTable from "../../../components/actuators/EntranceHumidifierTable.vue";
import HallVentilationTable from "../../../components/actuators/HallVentilationTable.vue";

const tables = ref({
  cooling_fan: [],
  habitat_heater: [],
  hall_ventilation: [],
  entrance_humidifier: [],
})

const headers = [
  { title: "Sensor", key: "sensor_name" },
  { title: "Operator", key: "operator" },
  { title: "Threshold", key: "threshold_value" },
  { title: "Target State", key: "target_state" },
]

function distributeRulesByActuator(rules = []) {
  Object.keys(tables.value).forEach((actuatorKey) => {
    tables.value[actuatorKey] = []
  })

  rules.forEach((rule) => {
    const actuatorKey = rule?.actuator_name
    if (!actuatorKey || !(actuatorKey in tables.value)) return
    tables.value[actuatorKey].push(rule)
  })
}


onMounted(async ()=>{
  try{
    const response = await api.get('/api/rules')
    const rules = Array.isArray(response)
      ? response
      : Array.isArray(response?.data)
        ? response.data
        : []
    distributeRulesByActuator(rules)
    console.log(tables.value)
  }catch(err){
    console.log(err);
  }
})


</script>
