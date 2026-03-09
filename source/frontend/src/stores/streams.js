import { defineStore } from 'pinia'

export const useStreamsStore = defineStore('streams', {
    state: ()=>({
        streamsList: {
            solar_array: {
                title: 'solar_array',
                icon: 'mdi-solar-power-variant-outline',
                power: {},
                voltage: {},
                current: {},
                cumulative_energy: {},
            },
            life_support: {
                title: 'life_support',
                icon: 'mdi-sprout',
                oxygen_percent: {}
            },
            radiation: {
                title: 'radiation',
                icon: 'mdi-sun-wireless-outline',
                radiation_uSv_h: {}
            },
            thermal_loop: {
                title: 'thermal_loop',
                icon: 'mdi-home-thermometer-outline',
                temperature: {},
                flow: {}
            },
            power_bus: {
                title: 'power_bus',
                icon: 'mdi-home-lightning-bolt-outline',
                power: {},
                voltage: {},
                current: {},
                cumulative_energy: {},
            },
            power_consumption: {
                title: 'power_consumption',
                icon: 'mdi-power-plug-battery-outline',
                power: {},
                voltage: {},
                current: {},
                cumulative_energy: {},
            },
            airlock: {
                title: 'airlock',
                icon: 'mdi-home-lock-open',
                cycles: {},
                state: {},
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