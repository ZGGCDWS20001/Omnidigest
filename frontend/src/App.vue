<template>
  <div class="app-container">
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="logo" @click="sidebarCollapsed = !sidebarCollapsed">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="#4ade80" stroke-width="2"/>
            <circle cx="16" cy="16" r="4" fill="#4ade80"/>
            <circle cx="16" cy="6" r="2" fill="#4ade80"/>
            <circle cx="16" cy="26" r="2" fill="#4ade80"/>
            <circle cx="6" cy="16" r="2" fill="#4ade80"/>
            <circle cx="26" cy="16" r="2" fill="#4ade80"/>
            <line x1="16" y1="12" x2="16" y2="8" stroke="#4ade80" stroke-width="1.5"/>
            <line x1="16" y1="20" x2="16" y2="24" stroke="#4ade80" stroke-width="1.5"/>
            <line x1="12" y1="16" x2="8" y2="16" stroke="#4ade80" stroke-width="1.5"/>
            <line x1="20" y1="16" x2="24" y2="16" stroke="#4ade80" stroke-width="1.5"/>
          </svg>
        </div>
        <div class="logo-text">
          <h1>OmniDigest</h1>
          <p>Dashboard</p>
        </div>
      </div>
      <nav>
        <router-link to="/" title="Dashboard">
          <span class="icon">📊</span>
          <span class="nav-text">Dashboard</span>
        </router-link>
        <router-link to="/knowledge-graph" title="Knowledge Graph">
          <span class="icon">🔗</span>
          <span class="nav-text">Knowledge Graph</span>
        </router-link>
        <router-link to="/config" title="Configuration">
          <span class="icon">⚙️</span>
          <span class="nav-text">Configuration</span>
        </router-link>
        <router-link to="/sources" title="RSS Sources">
          <span class="icon">📰</span>
          <span class="nav-text">RSS Sources</span>
        </router-link>
        <router-link to="/tokens" title="Token Stats">
          <span class="icon">💰</span>
          <span class="nav-text">Token Stats</span>
        </router-link>
      </nav>
      <div class="api-key-display" v-if="apiKey">
        <small>API Key:</small>
        <code>{{ showKey ? apiKey : maskedKey }}</code>
        <button @click="showKey = !showKey">{{ showKey ? 'Hide' : 'Show' }}</button>
      </div>
    </aside>
    <main class="main-content">
      <header>
        <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed" :title="sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'">
          {{ sidebarCollapsed ? '→' : '←' }}
        </button>
        <h2>{{ currentPageTitle }}</h2>
        <div class="header-actions">
          <button class="theme-toggle" @click="toggleTheme" :title="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
            {{ isDark ? '☀️' : '🌙' }}
          </button>
          <button @click="refreshData" :disabled="loading">
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const apiKey = ref(localStorage.getItem('api_key') || '')
    const showKey = ref(false)
    const loading = ref(false)
    const isDark = ref(localStorage.getItem('theme') === 'dark')
    const sidebarCollapsed = ref(false)

    const maskedKey = computed(() => {
      if (!apiKey.value) return ''
      return apiKey.value.substring(0, 8) + '...' + apiKey.value.substring(apiKey.value.length - 4)
    })

    const currentPageTitle = computed(() => {
      return route.meta.title || 'Dashboard'
    })

    const refreshData = () => {
      loading.value = true
      window.location.reload()
    }

    const toggleTheme = () => {
      isDark.value = !isDark.value
      localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
      document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
    }

    // Apply theme on mount
    onMounted(() => {
      if (!apiKey.value) {
        const key = prompt('Please enter your API key:')
        if (key) {
          apiKey.value = key
          localStorage.setItem('api_key', key)
        }
      }
      // Apply saved theme
      if (isDark.value) {
        document.documentElement.setAttribute('data-theme', 'dark')
      }
    })

    return {
      apiKey,
      showKey,
      maskedKey,
      currentPageTitle,
      loading,
      isDark,
      sidebarCollapsed,
      refreshData,
      toggleTheme
    }
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.sidebar {
  width: 240px;
  background: #1a1a2e;
  color: #fff;
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 70px;
  padding: 20px 10px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 4px;
}

.logo-icon {
  flex-shrink: 0;
}

.logo-text {
  overflow: hidden;
  white-space: nowrap;
  transition: opacity 0.3s ease;
}

.sidebar.collapsed .logo-text {
  opacity: 0;
  width: 0;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  color: #4ade80;
  white-space: nowrap;
}

.logo p {
  margin: 0;
  font-size: 11px;
  color: #888;
  white-space: nowrap;
}

nav {
  margin-top: 30px;
  flex: 1;
}

nav a {
  display: flex;
  align-items: center;
  padding: 12px 14px;
  color: #ccc;
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
}

nav a:hover, nav a.router-link-active {
  background: #16213e;
  color: #fff;
}

nav a .icon {
  flex-shrink: 0;
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.nav-text {
  transition: opacity 0.3s ease;
}

.sidebar.collapsed .nav-text {
  opacity: 0;
  width: 0;
}

.api-key-display {
  padding: 12px;
  background: #16213e;
  border-radius: 8px;
  font-size: 12px;
  overflow: hidden;
  transition: padding 0.3s ease;
}

.sidebar.collapsed .api-key-display {
  padding: 8px 4px;
}

.sidebar.collapsed .api-key-display small,
.sidebar.collapsed .api-key-display button {
  display: none;
}

.api-key-display code {
  display: block;
  margin: 8px 0;
  word-break: break-all;
  color: #4ade80;
  font-size: 10px;
}

.api-key-display button {
  background: #4ade80;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

header {
  background: var(--bg-secondary);
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-toggle {
  background: var(--bg-tertiary);
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 16px;
}

header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-actions button {
  background: #4ade80;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.theme-toggle {
  background: var(--bg-tertiary) !important;
  font-size: 16px;
  padding: 8px 12px !important;
}

.header-actions button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
