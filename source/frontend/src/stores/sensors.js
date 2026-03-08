import { defineStore } from 'pinia'

export const useSensorsStore = defineStore('sensors', {
    state: ()=>({
        sensorsList: {
            corridor_pressure: {
                icon: 'mdi-car-brake-low-pressure'
            },
            co2_hall: {
                icon: 'mdi-molecule-co2'
            },
            greenhouse_temperature: {
                icon: 'mdi-thermometer'
            },
            air_quality_pm25: {
                icon: 'mdi-weather-cloudy'
            },
            air_quality_voc: {
                icon: 'mdi-weather-cloudy'
            },
            entrance_humidity: {
                icon: 'mdi-water-percent'
            },
            hydroponic_ph: {
                icon: 'mdi-ph'
            },
            water_tank_level: {
                icon: 'mdi-chart-waterfall'
            }
        }
    }),
    persist: true
})