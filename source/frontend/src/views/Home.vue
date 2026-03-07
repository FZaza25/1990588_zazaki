<template>
  <div class="d-flex w-100 h-100 justify-center align-center">
    <div class="login-card w-md-50 w-66 w-lg-25 h-50 rounded-lg border-md" >
      <div class="d-flex flex-column">
          <img class="login-logo pt-8" src="/mars-iot-logo.png" alt="logo">
          <div class="d-flex justify-center text-center w-100 font-weight-bold px-12 py-8" style="font-size: 20px">
            {{ t('login.subtitle') }}
          </div>
          <div class="d-flex justify-center py-8">
            <v-btn
                class="rounded-lg w-33 bg-primary"
                variant="text"
                @click="router.push({ name: 'monitoring' })"
            >
              <div class="font-weight-bold">
                {{ t('login.title') }}
              </div>
            </v-btn>
          </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()

const {t} = useI18n()

</script>
