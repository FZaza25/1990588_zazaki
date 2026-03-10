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
      <template #item.actions="{ item }">
        <div class="d-flex w-100 ga-4">
          <v-tooltip text="Edit rule">
            <template v-slot:activator="{ props }">
              <v-icon icon="mdi-pencil" class="cursor-pointer" v-bind="props" size="32"/>
            </template>
          </v-tooltip>
          <v-tooltip text="Delete rule">
            <template v-slot:activator="{ props }">
              <v-icon icon="mdi-trash-can-outline" class="cursor-pointer" v-bind="props" size="32"/>
            </template>
          </v-tooltip>
        </div>
      </template>
    </v-data-table>
  </div>
  <CentralModal ref="openModal">
    <template #header>
      <h1>Add a new rule for {{ t('actuators.' + props.actuatorName) }}</h1>
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

const emit = defineEmits(['update-mode', 'update-status'])

const {t} = useI18n();

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

function openAddModal(){
  openModal.value.open()
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
