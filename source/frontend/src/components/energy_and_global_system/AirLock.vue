<template>
  <StreamCard :title="props.entries.title" :icon="props.entries.icon" :value="props.entries"/>
</template>

<script setup>

import StreamCard from "../common/StreamCard.vue";

const props = defineProps({
  entries: Object
})

</script>