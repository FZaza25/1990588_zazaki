<template>
  <div class="title">
    <h2>{{ t('sensors') }}</h2>
    <div class="d-flex ga-4">
      <UtilityCard />
      <UtilityCard />
      <UtilityCard />
    </div>

  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {onMounted, ref} from "vue";
import { api } from '../../../api/Request.js'
import UtilityCard from "../../../components/common/UtilityCard.vue";

const sensorsData = ref(null)

onMounted(async () => {
  try {
    await api.get('/api/state')
  }catch (error) {
    console.error(error)
  }
})

const {t} = useI18n();
</script>