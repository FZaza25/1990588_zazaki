<template>
  <v-navigation-drawer
    class="sidebar"
    v-model="drawer"
    :width="drawerWidth"
    app
    :rail="mdAndDown"
    expand-on-hover
    permanent
  >
    <div class="sidebar-content">
      <div class="sidebar-logo-wrap">
        <img class="sidebar-logo" src="/mars-iot-logo.png" alt="logo">
      </div>
      <v-list class="pt-16 sidebar-list border-t border-background">
        <v-list-item
            v-for="item in SideBarItems"
            class="text-white text-wrap py-lg-6 py-4"
            density="comfortable"
            :class="route.name === item.to? 'selected-item': ''"
            @click="router.push({name: item.to})"
        >
          <div class="d-flex align-center ga-4">
            <v-icon :icon="item.icon" />
            <div class="font-weight-bold" >
              {{t('sidebar.'+item.to)}}
            </div>
          </div>
        </v-list-item>
      </v-list>
      <div class="sidebar-footer pa-4 text-white font-weight-bold cursor-pointer border-t border-background" @click="router.push('/')">
            <v-icon icon="mdi-step-backward"/>
          {{mdAndDown?'':t('back')}}
      </div>
    </div>
  </v-navigation-drawer>

</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import SideBarItems from "../../data/SideBarItems.js";
import {useRouter, useRoute} from "vue-router";
import {useI18n} from "vue-i18n";
import { useDisplay } from 'vuetify'

const { mdAndDown } = useDisplay()

const drawer = ref(true)
const viewportWidth = ref(window.innerWidth)
const drawerWidth = computed(() => Math.round(viewportWidth.value * 0.20))

const router = useRouter()

const {t} = useI18n()

const route = useRoute()

const onResize = () => {
  viewportWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener("resize", onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize)
})
</script>
