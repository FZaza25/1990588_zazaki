<template>
  <div class="d-flex w-100 h-100 justify-center align-center">
    <div class="login-card w-md-50 w-66 w-lg-25 h-66 rounded-lg border-md" >
      <div class="d-flex flex-column">
        <div class="login-logo-wrap">
          <img class="login-logo" src="/mars-iot-logo.png" alt="logo">
        </div>

          <div class="d-flex justify-center text-center w-100 font-weight-bold text-background px-12 py-8" style="font-size: 20px">
            {{ t('login.subtitle') }}
          </div>
          <div class="d-flex justify-center py-8">
            <v-btn
                class="rounded-lg w-33 bg-background log-in-button"
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
