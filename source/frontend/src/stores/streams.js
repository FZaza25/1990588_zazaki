import { defineStore } from 'pinia'

export const useStreamsStore = defineStore('streams', {
    state: ()=>({
        streamsList: {
            solar_array: {
                title: 'solar_array',
                icon: 'mdi-solar-power-variant-outline',
                selected: {
                    index: null,
                    value: null
                },
                power: {},
                voltage: {},
                current: {},
                cumulative_energy: {},
            },
            life_support: {
                title: 'life_support',
                icon: 'mdi-sprout',
                selected: {
                    index: null,
                    value: null
                },
                oxygen_percent: {}
            },
            radiation: {
                title: 'radiation',
                icon: 'mdi-sun-wireless-outline',
                selected: {
                    index: null,
                    value: null
                },
                radiation_uSv_h: {}
            },
            thermal_loop: {
                title: 'thermal_loop',
                icon: 'mdi-home-thermometer-outline',
                selected: {
                    index: null,
                    value: null
                },
                temperature: {},
                flow: {}
            },
            power_bus: {
                title: 'power_bus',
                icon: 'mdi-home-lightning-bolt-outline',
                selected: {
                    index: null,
                    value: null
                },
                power: {},
                voltage: {},
                current: {},
                cumulative_energy: {},
            },
            power_consumption: {
                title: 'power_consumption',
                icon: 'mdi-power-plug-battery-outline',
                selected: {
                    index: null,
                    value: null
                },
                power: {},
                voltage: {},
                current: {},
                cumulative_energy: {},
            },
            airlock: {
                title: 'airlock',
                icon: 'mdi-home-lock-open',
                selected: {
                    index: null,
                    value: null
                },
                cycles: {},
                state: {},
            },
        },
        charts: {
            solar_array: {
                power: [],
                voltage: [],
                current: [],
                cumulative_energy: [],
            },
            life_support: {
                oxygen_percent: null
            },
            radiation: {
                radiation_uSv_h: []
            },
            thermal_loop: {
                temperature: [],
                flow: []
            },
            power_bus: {
                power: [],
                voltage: [],
                current: [],
                cumulative_energy: [],
            },
            power_consumption: {
                power: [],
                voltage: [],
                current: [],
                cumulative_energy: [],
            }
        }
    }),
    persist: true
})