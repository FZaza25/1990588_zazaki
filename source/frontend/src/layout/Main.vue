<template>
  <div class="d-flex">
    <router-view name="sidebar"/>
    <div class="d-flex flex-column">
      <router-view name="header"/>
      <router-view name="content"/>
    </div>
  </div>

</template>

<script setup>

</script>