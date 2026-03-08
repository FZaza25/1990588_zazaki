import { defineStore } from 'pinia'

export const useStreamsStore = defineStore('streams', {
    state: ()=>({
        streamsList: {
            solar_array: {
                icon: 'mdi-solar-power-variant-outline'
            },
            life_support: {
                icon: 'mdi-sprout'
            },
            radiation: {
                icon: 'mdi-sun-wireless-outline'
            },
            thermal_loop: {
                icon: 'mdi-home-thermometer-outline'
            },
            power_bus: {
                icon: 'mdi-home-lightning-bolt-outline'
            },
            power_consumption: {
                icon: 'mdi-power-plug-battery-outline'
            },
            airlock: {
                icon: 'mdi-home-lock-open'
            },
        },
        charts: {
            solar_array: [],
            life_support: null,
            radiation: [],
            thermal_loop: [],
            power_bus: [],
            power_consumption: [],
            airlock: [],
        }
    }),
    persist: true
})