<template>
  <StreamCard :title="props.entries.sensor_id" :icon="props.entries.icon" :value="props.entries.value"/>
</template>

<script setup>

import {ref} from "vue";
import StreamCard from "../common/StreamCard.vue";

const openModal = ref(null)

const props = defineProps({
  entries: Object
})

const openChart = ()=>{
  openModal.value.open()
}

</script>