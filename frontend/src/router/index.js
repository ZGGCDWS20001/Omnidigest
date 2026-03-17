import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Config from '../views/Config.vue'
import Sources from '../views/Sources.vue'
import TokenStats from '../views/TokenStats.vue'
import KnowledgeGraph from '../views/KnowledgeGraph.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard' }
  },
  {
    path: '/config',
    name: 'Config',
    component: Config,
    meta: { title: 'Configuration' }
  },
  {
    path: '/sources',
    name: 'Sources',
    component: Sources,
    meta: { title: 'RSS Sources' }
  },
  {
    path: '/tokens',
    name: 'TokenStats',
    component: TokenStats,
    meta: { title: 'Token Stats' }
  },
  {
    path: '/knowledge-graph',
    name: 'KnowledgeGraph',
    component: KnowledgeGraph,
    meta: { title: 'Knowledge Graph' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
