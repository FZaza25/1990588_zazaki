export default {
    path: 'energy-and-global-systems',
    name: 'energy_and_global_systems',
    components: {
        stream: () => import('../../../views/monitoring/energy_and_global_system/Stream.vue')
    }
}