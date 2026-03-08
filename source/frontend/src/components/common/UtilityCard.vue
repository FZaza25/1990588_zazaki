<template>
  <div class="utility-card">
    <div class="d-flex flex-column">
      <div class="d-flex align-center justify-lg-space-between justify-center flex-wrap">
        <v-icon :icon="props.icon" size="40" class="mr-2 w-25"/>
        <h2 class="">{{ t('sensors_name.'+props.title) }}</h2>

      </div>
      <div class="d-flex justify-center text-size-large">
        <h1>{{props.value}}</h1>
      </div>
    </div>

  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";

const {t} = useI18n();

const props = defineProps({
  title: String,
  icon: String,
  value: String,
})

</script>