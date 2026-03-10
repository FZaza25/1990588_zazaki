<template>
  <div class="utility-card">
    <div v-if="loaded.loading" class="d-flex flex-column">
      <div class="d-flex align-center justify-lg-space-between justify-center flex-wrap">
        <v-icon :icon="props.icon" size="40" class="mr-2 w-25"/>
        <h2 v-if="hasCardTitle">{{ t('sensors_name.' + props.title) }}</h2>
        <v-progress-circular v-else indeterminate color="primary" size="26" width="2" />

      </div>
      <div class="d-flex justify-center text-size-large">
        <div class="d-flex justify-lg-space-between justify-center w-100 align-center">
          <h1 v-if="hasCardValue">{{ props.value }}</h1>
          <v-progress-circular v-else indeterminate color="primary" size="26" width="2" />
          <v-icon icon="mdi-chart-areaspline" @click="props.openChart" class="icon-hover ml-2" size="40"/>
        </div>


      </div>
    </div>
    <div v-else class="d-flex justify-center align-center w-100">
      <v-progress-circular indeterminate color="primary"/>
    </div>

  </div>
</template>

<script setup>

import {useI18n} from "vue-i18n";
import {useLoadingStore} from "../../stores/loading.js";
import {computed} from "vue";

const {t, te} = useI18n();

const loaded = useLoadingStore()

const props = defineProps({
  title: String,
  icon: String,
  value: String,
  openChart: Function,
})

const hasCardTitle = computed(() => {
  if (typeof props.title !== "string") return false
  const normalized = props.title.trim()
  if (!normalized || normalized === "undefined" || normalized === "null") return false
  return te(`sensors_name.${normalized}`)
})

const hasCardValue = computed(() => {
  if (props.value === undefined || props.value === null) return false
  const normalized = String(props.value).trim().toLowerCase()
  if (!normalized) return false
  return !normalized.includes("undefined") && !normalized.includes("null")
})

</script>
