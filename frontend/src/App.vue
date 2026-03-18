<template>
  <div class="app-container" :class="{ 'mobile-menu-open': mobileMenuOpen }">
    <!-- API Key Modal -->
    <div v-if="showApiKeyModal" class="modal-overlay" @click.self="closeApiKeyModal">
      <div class="modal-content">
        <h3>{{ apiKeyModalTitle }}</h3>
        <input
          v-model="apiKeyInput"
          type="text"
          placeholder="Enter API key (format: client_name:key)"
          class="modal-input"
          @keyup.enter="submitApiKey"
        />
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeApiKeyModal">Cancel</button>
          <button class="btn-confirm" @click="submitApiKey">Submit</button>
        </div>
      </div>
    </div>

    <!-- Mobile overlay -->
    <div class="mobile-overlay" v-if="mobileMenuOpen" @click="mobileMenuOpen = false"></div>

    <!-- Mobile header -->
    <header class="mobile-header">
      <button class="mobile-menu-btn" @click="mobileMenuOpen = !mobileMenuOpen">
        <span class="menu-icon">☰</span>
      </button>
      <div class="mobile-title">
        <h2>{{ currentPageTitle }}</h2>
      </div>
      <div class="mobile-header-actions">
        <button class="theme-toggle" @click="toggleTheme" :title="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
      </div>
    </header>

    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed, 'mobile-open': mobileMenuOpen }">
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
        <router-link to="/" title="Dashboard" @click="closeMobileMenu">
          <span class="icon">📊</span>
          <span class="nav-text">Dashboard</span>
        </router-link>
        <router-link to="/knowledge-graph" title="Knowledge Graph" @click="closeMobileMenu">
          <span class="icon">🔗</span>
          <span class="nav-text">Knowledge Graph</span>
        </router-link>
        <router-link to="/config" title="Configuration" @click="closeMobileMenu">
          <span class="icon">⚙️</span>
          <span class="nav-text">Configuration</span>
        </router-link>
        <router-link to="/sources" title="RSS Sources" @click="closeMobileMenu">
          <span class="icon">📰</span>
          <span class="nav-text">RSS Sources</span>
        </router-link>
        <router-link to="/tokens" title="Token Stats" @click="closeMobileMenu">
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
      <!-- Desktop header -->
      <header class="desktop-header">
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
    const mobileMenuOpen = ref(false)

    // Modal state
    const showApiKeyModal = ref(false)
    const apiKeyModalTitle = ref('Please enter your API key:')
    const apiKeyInput = ref('')
    const apiKeyCallback = ref(null)

    const openApiKeyModal = (title = 'Please enter your API key:', callback = null) => {
      apiKeyModalTitle.value = title
      apiKeyInput.value = ''
      apiKeyCallback.value = callback
      showApiKeyModal.value = true
    }

    const closeApiKeyModal = () => {
      showApiKeyModal.value = false
      apiKeyInput.value = ''
      apiKeyCallback.value = null
    }

    const submitApiKey = () => {
      if (apiKeyInput.value) {
        apiKey.value = apiKeyInput.value
        localStorage.setItem('api_key', apiKeyInput.value)
        if (apiKeyCallback.value) {
          apiKeyCallback.value(apiKeyInput.value)
        } else {
          window.location.reload()
        }
      }
      closeApiKeyModal()
    }

    // Listen for API key required event
    const handleApiKeyRequired = (event) => {
      openApiKeyModal(event.detail?.message || 'API Key Required', (key) => {
        window.location.reload()
      })
    }

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

    const closeMobileMenu = () => {
      mobileMenuOpen.value = false
    }

    // Apply theme on mount
    onMounted(() => {
      // Listen for API key required event from axios interceptor
      window.addEventListener('api-key-required', handleApiKeyRequired)

      if (!apiKey.value) {
        openApiKeyModal()
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
      mobileMenuOpen,
      refreshData,
      toggleTheme,
      closeMobileMenu,
      // Modal
      showApiKeyModal,
      apiKeyModalTitle,
      apiKeyInput,
      closeApiKeyModal,
      submitApiKey
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
  font-size: 18px;
}

.modal-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-input:focus {
  outline: none;
  border-color: var(--accent);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  background: var(--bg-tertiary);
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-primary);
}

.btn-confirm {
  background: #4ade80;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
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

.desktop-header {
  display: flex;
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

/* Mobile styles */
.mobile-header {
  display: none;
}

.mobile-overlay {
  display: none;
}

/* Responsive: Tablet and below */
@media (max-width: 768px) {
  .desktop-header {
    display: none;
  }

  .mobile-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .mobile-menu-btn {
    background: var(--bg-tertiary);
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
  }

  .menu-icon {
    display: block;
  }

  .mobile-title {
    flex: 1;
  }

  .mobile-title h2 {
    margin: 0;
    font-size: 16px;
    color: var(--text-primary);
  }

  .mobile-header-actions {
    display: flex;
    gap: 8px;
  }

  .mobile-header-actions .theme-toggle {
    background: var(--bg-tertiary) !important;
    font-size: 14px;
    padding: 6px 10px !important;
  }

  .sidebar {
    position: fixed;
    left: -240px;
    top: 0;
    bottom: 0;
    z-index: 1000;
    width: 240px;
    transition: left 0.3s ease;
    padding-top: 20px;
  }

  .sidebar.mobile-open {
    left: 0;
  }

  .sidebar.collapsed {
    width: 240px;
    left: -240px;
  }

  .sidebar.mobile-open.collapsed {
    left: 0;
  }

  .sidebar .logo-text,
  .sidebar .nav-text,
  .sidebar .api-key-display {
    opacity: 1;
    width: auto;
  }

  .mobile-overlay {
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }

  .content {
    padding: 16px;
  }
}

/* Responsive: Small mobile */
@media (max-width: 480px) {
  .mobile-header {
    padding: 10px 12px;
  }

  .mobile-menu-btn {
    padding: 6px 10px;
    font-size: 14px;
  }

  .mobile-title h2 {
    font-size: 14px;
  }

  .mobile-header-actions .theme-toggle {
    font-size: 12px;
    padding: 5px 8px !important;
  }

  .content {
    padding: 12px;
  }
}

/* Responsive: Extra small mobile */
@media (max-width: 375px) {
  .mobile-header {
    padding: 8px 10px;
  }

  .content {
    padding: 10px;
  }
}
</style>
