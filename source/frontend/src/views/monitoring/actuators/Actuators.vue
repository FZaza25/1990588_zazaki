<template>
  <div class="tables-wrapper">
    <ActuatorsTable
        actuator-name="cooling_fan"
        :actuator-state="actuatorsState.cooling_fan"
        :pending="pendingByActuator.cooling_fan"
        :sensor-readings="sensorReadings"
        :loading="rulesLoading"
        :header="headers"
        :items="tables.cooling_fan"
        @update-mode="(value) => updateActuatorMode('cooling_fan', value)"
        @update-status="(value) => updateActuatorStatus('cooling_fan', value)"
        @rule-created="appendRule"
        @rule-updated="updateRule"
        @delete-rule="deleteRule"
    />
    <ActuatorsTable
        actuator-name="habitat_heater"
        :actuator-state="actuatorsState.habitat_heater"
        :pending="pendingByActuator.habitat_heater"
        :sensor-readings="sensorReadings"
        :loading="rulesLoading"
        :header="headers"
        :items="tables.habitat_heater"
        @update-mode="(value) => updateActuatorMode('habitat_heater', value)"
        @update-status="(value) => updateActuatorStatus('habitat_heater', value)"
        @rule-created="appendRule"
        @rule-updated="updateRule"
        @delete-rule="deleteRule"
    />
    <ActuatorsTable
        actuator-name="entrance_humidifier"
        :actuator-state="actuatorsState.entrance_humidifier"
        :pending="pendingByActuator.entrance_humidifier"
        :sensor-readings="sensorReadings"
        :loading="rulesLoading"
        :header="headers"
        :items="tables.entrance_humidifier"
        @update-mode="(value) => updateActuatorMode('entrance_humidifier', value)"
        @update-status="(value) => updateActuatorStatus('entrance_humidifier', value)"
        @rule-created="appendRule"
        @rule-updated="updateRule"
        @delete-rule="deleteRule"
    />
    <ActuatorsTable
        actuator-name="hall_ventilation"
        :actuator-state="actuatorsState.hall_ventilation"
        :pending="pendingByActuator.hall_ventilation"
        :sensor-readings="sensorReadings"
        :loading="rulesLoading"
        :header="headers"
        :items="tables.hall_ventilation"
        @update-mode="(value) => updateActuatorMode('hall_ventilation', value)"
        @update-status="(value) => updateActuatorStatus('hall_ventilation', value)"
        @rule-created="appendRule"
        @rule-updated="updateRule"
        @delete-rule="deleteRule"
    />
  </div>
</template>

<script setup>
import {onMounted, onUnmounted, ref} from "vue";
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
const pendingByActuator = ref({
  cooling_fan: false,
  habitat_heater: false,
  hall_ventilation: false,
  entrance_humidifier: false,
})
const sensorReadings = ref({})
const rulesLoading = ref(true)

const headers = [
  { title: "Sensor", key: "sensor_name" },
  { title: "Sensor Value", key: "current_sensor_value" },
  { title: "Operator", key: "operator" },
  { title: "Threshold", key: "threshold_value" },
  { title: "Target State", key: "target_state" },
  { title: "Actions", key: "actions" }
]
let actuatorsPollingId = null
let sensorsPollingId = null

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

async function refreshActuatorsState() {
  try {
    const actuators = await api.get('/api/actuators')
    handleActuators(actuators)
  } catch (err) {
    console.log(err)
  }
}

function handleSensorState(state = []) {
  const nextReadings = {}
  state.forEach((sensor) => {
    const sourceId = sensor?.source_id
    if (!sourceId) return
    if (
      sensor?.series_id === 'air_quality_pm25:pm1' ||
      sensor?.series_id === 'air_quality_pm25:pm10' ||
      sensor?.series_id === 'air_quality_voc:co2e_ppm' ||
      sensor?.series_id === 'water_tank_level:level_pct'
    ) return

    const value = sensor?.value
    const unit = sensor?.unit
    const display = value == null ? undefined : `${value}${unit ? ` ${unit}` : ''}`
    if (!display) return
    nextReadings[sourceId] = display
  })
  sensorReadings.value = nextReadings
}

async function refreshSensorReadings() {
  try {
    const state = await api.get('/api/state')
    if (Array.isArray(state)) {
      handleSensorState(state)
    }
  } catch (err) {
    console.log(err)
  }
}

function hasAnyAutoActuator() {
  return Object.values(actuatorsState.value).some((actuator) => actuator?.mode === 'AUTO')
}

function startAutoPollingIfNeeded() {
  if (!hasAnyAutoActuator()) return
  if (actuatorsPollingId) return
  actuatorsPollingId = setInterval(async () => {
    if (!hasAnyAutoActuator()) {
      clearInterval(actuatorsPollingId)
      actuatorsPollingId = null
      return
    }
    await refreshActuatorsState()
  }, 5000)
}

async function updateActuatorMode(actuatorName, isAuto) {
  const current = actuatorsState.value[actuatorName]
  if (!current) return

  const nextMode = isAuto ? 'AUTO' : 'MANUAL'
  current.mode = nextMode
  pendingByActuator.value[actuatorName] = true

  try {
    actuatorsState.value[actuatorName] = await api.patch(`/api/actuators/${actuatorName}/mode`, {mode: nextMode})
    if (isAuto) {
      await refreshActuatorsState()
    }
    startAutoPollingIfNeeded()
  } catch (err) {
    console.log(err)
  } finally {
    pendingByActuator.value[actuatorName] = false
  }
}

async function updateActuatorStatus(actuatorName, isOn) {
  const current = actuatorsState.value[actuatorName]
  if (!current) return
  const nextStatus = isOn ? 'ON' : 'OFF'
  current.status = nextStatus
  pendingByActuator.value[actuatorName] = true

  try {
    actuatorsState.value[actuatorName] = await api.patch(
      `/api/actuators/${actuatorName}/status`,
      { status: nextStatus }
    )
  } catch (err) {
    console.log(err)
  } finally {
    pendingByActuator.value[actuatorName] = false
  }
}

async function appendRule(rule) {
  const actuatorKey = rule?.actuator_name
  if (!actuatorKey || !(actuatorKey in tables.value)) return
  tables.value[actuatorKey].push(rule)
  await refreshActuatorsState()
}

async function updateRule(updatedRule) {
  if (!updatedRule?.id) return
  Object.keys(tables.value).forEach((actuatorKey) => {
    tables.value[actuatorKey] = tables.value[actuatorKey].map((rule) =>
      rule.id === updatedRule.id ? updatedRule : rule
    )
  })
  await refreshActuatorsState()
}

async function deleteRule(ruleId) {
  if (!ruleId) return

  try {
    await api.delete(`/api/rules/${ruleId}`)
    Object.keys(tables.value).forEach((actuatorKey) => {
      tables.value[actuatorKey] = tables.value[actuatorKey].filter((rule) => rule.id !== ruleId)
    })
    await refreshActuatorsState()
  } catch (err) {
    console.log(err)
  }
}

onMounted(async ()=>{
  try{
    await refreshActuatorsState()
    await refreshSensorReadings()
    const response = await api.get('/api/rules')
    const rules = Array.isArray(response)
      ? response
      : Array.isArray(response?.data)
        ? response.data
        : []
    distributeRulesByActuator(rules)
    startAutoPollingIfNeeded()

  }catch(err){
    console.log(err);
  } finally {
    rulesLoading.value = false
  }

  sensorsPollingId = setInterval(async () => {
    await refreshSensorReadings()
  }, 5000)
})

onUnmounted(() => {
  if (actuatorsPollingId) {
    clearInterval(actuatorsPollingId)
    actuatorsPollingId = null
  }
  if (sensorsPollingId) {
    clearInterval(sensorsPollingId)
    sensorsPollingId = null
  }
})


</script>
