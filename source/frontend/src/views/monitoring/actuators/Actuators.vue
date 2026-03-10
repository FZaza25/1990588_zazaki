<template>
  <div class="tables-wrapper">
    <ActuatorsTable
        actuator-name="cooling_fan"
        :actuator-state="actuatorsState.cooling_fan"
        :header="headers"
        :items="tables.cooling_fan"
        @update-mode="(value) => updateActuatorMode('cooling_fan', value)"
        @update-status="(value) => updateActuatorStatus('cooling_fan', value)"
    />
    <ActuatorsTable
        actuator-name="habitat_heater"
        :actuator-state="actuatorsState.habitat_heater"
        :header="headers"
        :items="tables.habitat_heater"
        @update-mode="(value) => updateActuatorMode('habitat_heater', value)"
        @update-status="(value) => updateActuatorStatus('habitat_heater', value)"
    />
    <ActuatorsTable
        actuator-name="entrance_humidifier"
        :actuator-state="actuatorsState.entrance_humidifier"
        :header="headers"
        :items="tables.entrance_humidifier"
        @update-mode="(value) => updateActuatorMode('entrance_humidifier', value)"
        @update-status="(value) => updateActuatorStatus('entrance_humidifier', value)"
    />
    <ActuatorsTable
        actuator-name="hall_ventilation"
        :actuator-state="actuatorsState.hall_ventilation"
        :header="headers"
        :items="tables.hall_ventilation"
        @update-mode="(value) => updateActuatorMode('hall_ventilation', value)"
        @update-status="(value) => updateActuatorStatus('hall_ventilation', value)"
    />
  </div>
</template>

<script setup>
import {onMounted, ref} from "vue";
import {api} from "../../../api/Request.js";
import ActuatorsTable from "../../../components/actuators/ActuatorsTable.vue";

const tables = ref({
  cooling_fan: [],
  habitat_heater: [],
  hall_ventilation: [],
  entrance_humidifier: [],
})

const actuatorsState = ref({
  cooling_fan: null,
  habitat_heater: null,
  hall_ventilation: null,
  entrance_humidifier: null,
})

const headers = [
  { title: "Sensor", key: "sensor_name" },
  { title: "Operator", key: "operator" },
  { title: "Threshold", key: "threshold_value" },
  { title: "Target State", key: "target_state" },
  { title: "Actions", key: "actions" }
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

function handleActuators(actuators) {
  actuators.map(actuator => {
    actuatorsState.value[actuator.name] = actuator
  })
}

async function updateActuatorMode(actuatorName, isAuto) {
  const current = actuatorsState.value[actuatorName]
  if (!current) return

  const nextMode = isAuto ? 'AUTO' : 'MANUAL'
  current.mode = nextMode

  try {
    actuatorsState.value[actuatorName] = await api.patch(`/api/actuators/${actuatorName}/mode`, {mode: nextMode})
  } catch (err) {
    console.log(err)
  }
}

function updateActuatorStatus(actuatorName, isOn) {
  const current = actuatorsState.value[actuatorName]
  if (!current) return
  current.status = isOn ? 'ON' : 'OFF'
}

onMounted(async ()=>{
  try{
    const actuators = await api.get('/api/actuators')
    handleActuators(actuators)
    const response = await api.get('/api/rules')
    const rules = Array.isArray(response)
      ? response
      : Array.isArray(response?.data)
        ? response.data
        : []
    distributeRulesByActuator(rules)

  }catch(err){
    console.log(err);
  }
})


</script>
