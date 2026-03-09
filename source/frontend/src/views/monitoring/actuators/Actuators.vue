<template>

</template>

<script setup>
import {onMounted} from "vue";
import {api} from "../../../api/Request.js";

onMounted(async ()=>{
  try{
    const response = await api.get('/api/rules')
    console.log(response)
  }catch(err){
    console.log(err);
  }
})
</script>