import { createI18n } from 'vue-i18n'

const messages = {
    en: {
        back: 'Back',
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
