<template>
  <div class="actuators-table">
    <div class="d-flex justify-space-between">
      <h2 >{{ t('actuators.'+props.actuatorName) }}</h2>
      <div class="tooltip-container d-flex bg-background align-center justify-space-between w-50 rounded-lg my-5">
        <v-switch
            v-model="auto"
            :label="auto? 'Automatic':'Manual'"
            color="orange"
            class="w-33"
            hide-details
        />
        <v-switch
            v-if="!auto"
            v-model="isOn"
            :label="isOn? 'ON':'OFF'"
            color="orange"
            class="w-33"
            hide-details/>
        <v-tooltip text="Add rule">
          <template v-slot:activator="{ props }">
            <v-icon icon="mdi-plus" class="cursor-pointer" v-bind="props" @click="()=>openAddModal()" size="32"/>
          </template>
        </v-tooltip>

      </div>
    </div>

    <v-data-table
        :headers="props.header"
        :items="props.items"
        class="actuators-data-table rounded-lg"
    >
      <template #item.sensor_name="{ item }">
        <span>{{ t('sensors_name.' + item.sensor_name) }}</span>
      </template>
      <template #item.actions="{ item }">
        <div class="d-flex w-100 ga-4">
          <v-tooltip text="Edit rule">
            <template v-slot:activator="{ props }">
              <v-icon
                  icon="mdi-pencil"
                  class="cursor-pointer"
                  v-bind="props"
                  size="32"
                  @click="openEditModal(item)"
              />
            </template>
          </v-tooltip>
          <v-tooltip text="Delete rule">
            <template v-slot:activator="{ props }">
              <v-icon
                  icon="mdi-trash-can-outline"
                  class="cursor-pointer"
                  v-bind="props"
                  size="32"
                  @click="deleteRule(item.id)"
              />
            </template>
          </v-tooltip>
        </div>
      </template>
    </v-data-table>
  </div>
  <CentralModal ref="openModal">
    <template #header>
      <h1>{{ modalTitle }}</h1>
    </template>
    <template #content>
      <v-container fluid class="py-2">
        <v-row>
          <v-col cols="12" md="6">
            <v-autocomplete
                v-model="form.sensor_name"
                label="Sensor"
                :items="sensorOptions"
                item-title="title"
                item-value="value"
                clearable
                variant="outlined"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-autocomplete
                v-model="form.operator"
                label="Operator"
                :items="operatorOptions"
                clearable
                variant="outlined"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
                v-model.number="form.threshold_value"
                label="Threshold"
                type="number"
                variant="outlined"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-autocomplete
                v-model="form.target_state"
                label="Target State"
                :items="targetStateOptions"
                clearable
                variant="outlined"
            />
          </v-col>
        </v-row>
      </v-container>
    </template>
    <template #footer>
      <div class="d-flex w-auto ga-4 justify-end">
        <v-btn
            class="rounded-lg bg-primary"
            variant="text"
            @click="()=>openModal.close()"
        >
          <div class="font-weight-bold">
            Exit
          </div>
        </v-btn>
        <v-btn
            class="rounded-lg bg-primary"
            variant="text"
            @click="submitRule"
        >
          <div class="font-weight-bold">
            Confirm
          </div>
        </v-btn>
      </div>
    </template>
  </CentralModal>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {computed, ref} from "vue";
import CentralModal from "../common/CentralModal.vue";
import {useSensorsStore} from "../../stores/sensors.js";
import {api} from "../../api/Request.js";

const props = defineProps({
  actuatorName: {
    type: String,
    required: true
  },
  header: {
    type: Array,
    required: true
  },
  items: {
    type: Array,
    required: true
  },
  actuatorState: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update-mode', 'update-status', 'rule-created', 'rule-updated', 'delete-rule'])

const {t} = useI18n();
const sensorsStore = useSensorsStore()

const operatorOptions = ['>', '<', '>=', '<=', '==', '!=']
const targetStateOptions = ['ON', 'OFF']
const sensorOptions = computed(() =>
  Object.keys(sensorsStore.sensorsList || {}).map((sensorKey) => ({
    title: t(`sensors_name.${sensorKey}`),
    value: sensorKey
  }))
)

const form = ref({
  sensor_name: null,
  operator: null,
  threshold_value: null,
  target_state: 'ON'
})
const editingRuleId = ref(null)

const auto = computed({
  get: () => props.actuatorState?.mode === 'AUTO',
  set: (value) => {
    emit('update-mode', Boolean(value))
  }
})

const isOn = computed({
  get: () => props.actuatorState?.status === 'ON',
  set: (value) => {
    emit('update-status', Boolean(value))
  }
})

const openModal = ref(null);
const modalTitle = computed(() =>
  editingRuleId.value
    ? `Edit rule for ${t('actuators.' + props.actuatorName)}`
    : `Add a new rule for ${t('actuators.' + props.actuatorName)}`
)

function openAddModal(){
  editingRuleId.value = null
  form.value = {
    sensor_name: null,
    operator: null,
    threshold_value: null,
    target_state: 'ON'
  }
  openModal.value.open()
}

function openEditModal(rule) {
  if (!rule?.id) return
  editingRuleId.value = rule.id
  form.value = {
    sensor_name: rule.sensor_name ?? null,
    operator: rule.operator ?? null,
    threshold_value: rule.threshold_value != null ? Number(rule.threshold_value) : null,
    target_state: rule.target_state ?? 'ON'
  }
  openModal.value.open()
}

async function submitRule() {
  if (!form.value.sensor_name || !form.value.operator || form.value.threshold_value == null || !form.value.target_state) {
    return
  }

  const payload = {
    sensor_name: form.value.sensor_name,
    operator: form.value.operator,
    threshold_value: Number(form.value.threshold_value),
    target_state: form.value.target_state
  }

  try {
    if (editingRuleId.value) {
      const updatedRule = await api.patch(`/api/rules/${editingRuleId.value}`, payload)
      emit('rule-updated', updatedRule)
    } else {
      const createdRule = await api.post('/api/rules', {
        ...payload,
        actuator_name: props.actuatorName
      })
      emit('rule-created', createdRule)
    }
    openModal.value.close()
    editingRuleId.value = null
    form.value = {
      sensor_name: null,
      operator: null,
      threshold_value: null,
      target_state: 'ON'
    }
  } catch (err) {
    console.log(err)
  }
}

function deleteRule(ruleId) {
  if (!ruleId) return
  emit('delete-rule', ruleId)
}


</script>

<style scoped lang="scss">
@use "../../assets/variables" as vars;

.tooltip-container {
  border: 3px solid vars.$orange;
  padding: 0 12px;
}

.actuators-data-table {
  border: 3px solid vars.$orange;
  overflow: hidden;
}
</style>
