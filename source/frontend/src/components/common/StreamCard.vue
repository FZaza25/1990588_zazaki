<template>
  <div class="utility-card">
    <div class="d-flex flex-column">
      <div class="d-flex align-center justify-lg-space-between justify-center flex-wrap">
        <v-icon :icon="props.icon" size="40" class="mr-2"/>
        <h2 class="">{{ t('stream_name.'+props.title) }}</h2>

      </div>
      <div class="d-flex justify-center text-size-large">
        <div  v-if="loaded.loading" class="d-flex justify-lg-space-between justify-center w-100 align-center">
          <h1>{{props.value}}</h1>
          <v-icon v-if="props.openChart" icon="mdi-chart-areaspline" @click="props.openChart" class="icon-hover ml-2" size="40"/>
        </div>

        <v-progress-circular indeterminate color="primary" v-else/>
      </div>
    </div>

  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {useLoadingStore} from "../../stores/loading.js";

const {t} = useI18n();

const loaded = useLoadingStore()

const props = defineProps({
  title: String,
  icon: String,
  value: String,
  openChart: {
    type: Function,
    default: null
  }
})

</script>