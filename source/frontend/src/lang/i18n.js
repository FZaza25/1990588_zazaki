import { createI18n } from 'vue-i18n'

const messages = {
    en: {
        back: 'Back',
        sensors: 'Sensors',
        sensors_name: {
            corridor_pressure: 'Corridor Pressure',
            co2_hall: 'Co2 Hall',
            greenhouse_temperature: 'Greenhouse Temperature',
            air_quality_pm25: 'Air Quality pm25',
            air_quality_voc: 'Air Quality voc',
            entrance_humidity: 'Entrance Humidity',
            water_tank_level: 'Water Tank Level',
            hydroponic_ph: 'Hydroponic Ph',
        },
        login: {
            title: 'Log in',
            subtitle: 'Log in to monitor and control your habitat in real time.',
        },
        sidebar: {
            indoor_environment: 'Indoor Environment',
            water_system: 'Water and hydroponic systems',
            energy_and_global_systems: 'Energy and global systems',
        }
    },
    it: {
        login: {
            title: 'Accedi',
            subtitle: 'Accedi per monitorare e controllare il tuo habitat in tempo reale.',
        },
    },
}

export default createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
})
