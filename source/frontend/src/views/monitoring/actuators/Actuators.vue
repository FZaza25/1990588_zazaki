<template>
  <div class="tables-wrapper">
    <ActuatorsTable
        actuator-name="cooling_fan"
        :actuator-state="actuatorsState.cooling_fan"
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
const rulesLoading = ref(true)

const headers = [
  { title: "Sensor", key: "sensor_name" },
  { title: "Operator", key: "operator" },
  { title: "Threshold", key: "threshold_value" },
  { title: "Target State", key: "target_state" },
  { title: "Actions", key: "actions" }
]
let actuatorsPollingId = null

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

  try {
    actuatorsState.value[actuatorName] = await api.patch(`/api/actuators/${actuatorName}/mode`, {mode: nextMode})
    if (isAuto) {
      await refreshActuatorsState()
    }
    startAutoPollingIfNeeded()
  } catch (err) {
    console.log(err)
  }
}

async function updateActuatorStatus(actuatorName, isOn) {
  const current = actuatorsState.value[actuatorName]
  if (!current) return
  const nextStatus = isOn ? 'ON' : 'OFF'
  current.status = nextStatus

  try {
    actuatorsState.value[actuatorName] = await api.patch(
      `/api/actuators/${actuatorName}/status`,
      { status: nextStatus }
    )
  } catch (err) {
    console.log(err)
  }
}

function appendRule(rule) {
  const actuatorKey = rule?.actuator_name
  if (!actuatorKey || !(actuatorKey in tables.value)) return
  tables.value[actuatorKey].push(rule)
}

function updateRule(updatedRule) {
  if (!updatedRule?.id) return
  Object.keys(tables.value).forEach((actuatorKey) => {
    tables.value[actuatorKey] = tables.value[actuatorKey].map((rule) =>
      rule.id === updatedRule.id ? updatedRule : rule
    )
  })
}

async function deleteRule(ruleId) {
  if (!ruleId) return

  try {
    await api.delete(`/api/rules/${ruleId}`)
    Object.keys(tables.value).forEach((actuatorKey) => {
      tables.value[actuatorKey] = tables.value[actuatorKey].filter((rule) => rule.id !== ruleId)
    })
  } catch (err) {
    console.log(err)
  }
}

onMounted(async ()=>{
  try{
    await refreshActuatorsState()
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
})

onUnmounted(() => {
  if (actuatorsPollingId) {
    clearInterval(actuatorsPollingId)
    actuatorsPollingId = null
  }
})


</script>
