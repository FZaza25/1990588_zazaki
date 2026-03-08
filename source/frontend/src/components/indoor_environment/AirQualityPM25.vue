<template>
  <UtilityCard :title="entries.sensor_id" :icon="entries.icon" :value="entries.value + ' ' + entries.unit"/>
</template>

<script setup>

import UtilityCard from "../common/UtilityCard.vue";

const props = defineProps({
  entries: Object
})
</script>