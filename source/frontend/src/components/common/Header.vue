<template>
  <div class="font-weight-bold text-white text-title-large py-4 px-15">
    {{ t('sidebar.'+route.name) }}
  </div>
</template>
<script setup>

import {useRoute} from "vue-router";
import {useI18n} from "vue-i18n";

const {t} = useI18n();

const route = useRoute()

</script>