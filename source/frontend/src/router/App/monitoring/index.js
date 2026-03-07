import EnergyAndGlobalSystems from './EnergyAndGlobalSystems.js'
import WaterSystem from './WaterSystem.js'
import IndoorEnvironment from './IndoorEnvironment.js'

export default {
    path: 'monitoring',
    name: 'monitoring',
    redirect: { name: 'indoor_environment' },
    components: {
        sidebar: () => import('../../../components/common/SideBar.vue'),
        header: () => import('../../../components/common/Header.vue'),
        content: () => import('../../../components/common/ContentCard.vue'),
    },
    children: [EnergyAndGlobalSystems, WaterSystem, IndoorEnvironment]
}
