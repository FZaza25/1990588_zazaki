<template>
  <div class="d-flex w-100 h-100">

    <router-view name="sidebar"/>
    <div class="d-flex flex-column w-100 h-100">
      <router-view name="header"/>
      <router-view name="content"/>
    </div>
  </div>

</template>

<script setup>

</script>