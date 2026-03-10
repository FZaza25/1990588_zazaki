<template>
  <div class="actuators-table">
    <div class="d-flex justify-space-between">
      <h2 >{{ t('actuators.'+props?.items[0]?.actuator_name) }}</h2>
      <div class="d-flex bg-background align-center justify-space-between w-33 rounded-lg my-5">
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
        class="rounded-lg"
    />
  </div>

</template>

<script setup>
import {useI18n} from "vue-i18n";

const {t} = useI18n();

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