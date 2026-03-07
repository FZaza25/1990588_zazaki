<template>
  <v-navigation-drawer
    class="sidebar"
    v-model="drawer"
    :width="drawerWidth"
    app
  >
    <div class="sidebar-logo-wrap">
      <img class="sidebar-logo" src="/mars-iot-logo.png" alt="logo">
    </div>
    <v-list class="pt-16">
      <v-list-item
          v-for="item in SideBarItems"
          class="text-white text-wrap py-6"
          density="comfortable"
          :class="route.name === item.to? 'selected-item': ''"
          @click="router.push({name: item.to})"
      >
        <div class="d-flex ga-4">
          <v-icon :icon="item.icon" />
          <div class="font-weight-bold" >
            {{item.label}}
          </div>
        </div>

      </v-list-item>/

    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import SideBarItems from "../../data/SideBarItems.js";
import {useRouter, useRoute} from "vue-router";

const drawer = ref(true)
const viewportWidth = ref(window.innerWidth)
const drawerWidth = computed(() => Math.round(viewportWidth.value * 0.20))

const router = useRouter()

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
