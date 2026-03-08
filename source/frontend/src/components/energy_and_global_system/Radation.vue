<template>
  <StreamCard :title="entries.sensor_id" :icon="entries.icon" :value="entries.value + ' ' + entries.unit"/>
</template>

<script setup>

import StreamCard from "../common/StreamCard.vue";

const props = defineProps({
  entries: Object
})
</script>