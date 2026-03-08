export default {
    path: 'water-system',
    name: 'water_system',
    components: {
        sensors: () => import('../../../views/monitoring/water_system/Sensors.vue'),
    }
}