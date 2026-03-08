<template>
  <StreamCard :title="entries.sensor_id" :icon="entries.icon" :value="entries.value"/>
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