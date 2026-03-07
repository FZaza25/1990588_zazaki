import EnergyAndGlobalSystems from './EnergyAndGlobalSystems.js'
import WaterSystem from './WaterSystem.js'
import IndoorEnvironment from './IndoorEnvironment.js'

export default {
    path: 'monitoring',

    children: [EnergyAndGlobalSystems, WaterSystem, IndoorEnvironment]
}