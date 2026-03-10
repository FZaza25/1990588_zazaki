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
        },
        charts: {
            corridor_pressure: [],
            co2_hall: [],
            greenhouse_temperature: [],
            air_quality_pm25: [],
            air_quality_voc: null,
            entrance_humidity: [],
            hydroponic_ph: [],
            water_tank_level: null

        }
    }),
    persist: true
})