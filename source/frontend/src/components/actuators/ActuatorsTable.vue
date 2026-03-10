<template>
  <div class="actuators-table">
    <div class="d-flex">
      <h2>{{ t('actuators.'+props?.items[0]?.actuator_name) }}</h2>
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