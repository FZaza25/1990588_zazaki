<template>
  <div class="actuators-table">
    <div class="d-flex justify-space-between">
      <h2 >{{ t('actuators.'+props?.items[0]?.actuator_name) }}</h2>
      <div class="tooltip-container d-flex bg-background align-center justify-space-between w-50 rounded-lg my-5">
        <v-switch
            v-model="auto"
            :label="auto? 'Automatic':'Manual'"
            color="orange"
            class="w-33"
            hide-details
        />
        <v-switch
            v-model="isOn"
            :label="isOn? 'ON':'OFF'"
            color="orange"
            class="w-33"
            hide-details/>
        <v-tooltip text="Add rule">
          <template v-slot:activator="{ props }">
            <v-icon icon="mdi-plus" v-bind="props" size="32"/>
          </template>
        </v-tooltip>

      </div>
    </div>

    <v-data-table
        :headers="props.header"
        :items="props.items"
        class="actuators-data-table rounded-lg"
    />
  </div>

</template>

<script setup>
import {useI18n} from "vue-i18n";
import {ref} from "vue";

const {t} = useI18n();

const auto = ref(false)

const isOn = ref(false);

const props = defineProps({
  header: {
    type: Array,
    required: true
  },
  items: {
    type: Array,
    required: true
  }
})
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
