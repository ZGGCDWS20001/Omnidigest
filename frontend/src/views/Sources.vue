<template>
  <div class="sources">
    <!-- Tab Navigation -->
    <div class="tabs-container fade-in">
      <div class="tabs">
        <div class="tab" :class="{ active: serviceType === 'daily' }" @click="serviceType = 'daily'">
          <span class="tab-icon">📰</span>
          <span>Daily News</span>
          <span class="tab-badge" v-if="serviceType === 'daily' && sources.length">{{ sources.length }}</span>
        </div>
        <div class="tab" :class="{ active: serviceType === 'breaking' }" @click="serviceType = 'breaking'">
          <span class="tab-icon">🚨</span>
          <span>Breaking News</span>
          <span class="tab-badge" v-if="serviceType === 'breaking' && sources.length">{{ sources.length }}</span>
        </div>
        <div class="tab" :class="{ active: serviceType === 'twitter' }" @click="serviceType = 'twitter'">
          <span class="tab-icon">🐦</span>
          <span>Twitter</span>
          <span class="tab-badge" v-if="serviceType === 'twitter' && sources.length">{{ sources.length }}</span>
        </div>
      </div>
    </div>

    <!-- Header with Stats -->
    <div class="card fade-in" style="animation-delay: 0.1s">
      <div class="sources-header">
        <div class="sources-title">
          <h3>{{ serviceTitle }}</h3>
          <span class="sources-count">{{ sources.length }} sources</span>
        </div>
        <button v-if="serviceType === 'daily'" class="btn" @click="showAddForm = !showAddForm">
          <span v-if="!showAddForm">+</span>
          {{ showAddForm ? 'Cancel' : 'Add Source' }}
        </button>
      </div>

      <!-- Add Form (only for daily) -->
      <div v-if="showAddForm && serviceType === 'daily'" class="add-form fade-in">
        <h4>Add New RSS Source</h4>
        <div class="form-grid">
          <div class="form-group">
            <label>Name</label>
            <input v-model="newSource.name" type="text" placeholder="e.g., BBC News" />
          </div>
          <div class="form-group">
            <label>URL</label>
            <input v-model="newSource.url" type="text" placeholder="https://..." />
          </div>
        </div>
        <div class="form-actions">
          <button class="btn btn-primary" @click="addSource" :disabled="!newSource.name || !newSource.url || adding">
            {{ adding ? 'Adding...' : 'Add Source' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading/Error States -->
    <div v-if="loading" class="loading-state fade-in">
      <div class="loading-spinner"></div>
      <p>Loading sources...</p>
    </div>
    <div v-else-if="error" class="error-state fade-in">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
      <button class="btn" @click="loadSources">Retry</button>
    </div>

    <!-- Sources Grid -->
    <template v-else>
      <!-- Daily RSS Sources Cards -->
      <div v-if="sources.length > 0 && serviceType === 'daily'" class="sources-grid fade-in">
        <div v-for="source in sources" :key="source.id" class="source-card">
          <div class="source-card-header">
            <div class="source-name">{{ source.name }}</div>
            <span class="badge" :class="source.enabled ? 'badge-success' : 'badge-danger'">
              {{ source.enabled ? 'Active' : 'Disabled' }}
            </span>
          </div>
          <div class="source-url">
            <a :href="source.url" target="_blank" rel="noopener">{{ truncateUrl(source.url) }}</a>
          </div>
          <div class="source-stats">
            <div class="source-stat" :class="{ danger: source.fail_count > 5 }">
              <span class="stat-label">Failures</span>
              <span class="stat-value">{{ source.fail_count }}</span>
            </div>
            <div class="source-stat">
              <span class="stat-label">Last Error</span>
              <span class="stat-value error-text">{{ source.last_error || 'None' }}</span>
            </div>
          </div>
          <div class="source-actions">
            <button class="btn btn-secondary btn-sm" @click="toggleSource(source)">
              {{ source.enabled ? 'Disable' : 'Enable' }}
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteSource(source)">Delete</button>
          </div>
        </div>
      </div>

      <!-- Breaking RSS Sources Cards -->
      <div v-else-if="sources.length > 0 && serviceType === 'breaking'" class="sources-grid">
        <div v-for="source in sources" :key="source.id" class="source-card">
          <div class="source-card-header">
            <div class="source-name">{{ source.name }}</div>
            <span class="badge" :class="source.enabled ? 'badge-success' : 'badge-danger'">
              {{ source.enabled ? 'Active' : 'Disabled' }}
            </span>
          </div>
          <div class="source-meta">
            <span class="platform-tag">{{ source.platform }}</span>
          </div>
          <div class="source-url">
            <a :href="source.url" target="_blank" rel="noopener">{{ truncateUrl(source.url) }}</a>
          </div>
          <div class="source-stats">
            <div class="source-stat success">
              <span class="stat-label">Success</span>
              <span class="stat-value">{{ source.success_count }}</span>
            </div>
            <div class="source-stat" :class="{ danger: source.fail_count > 5 }">
              <span class="stat-label">Failed</span>
              <span class="stat-value">{{ source.fail_count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Twitter Accounts Cards -->
      <div v-else-if="sources.length > 0 && serviceType === 'twitter'" class="sources-grid">
        <div v-for="source in sources" :key="source.id" class="source-card twitter-card">
          <div class="source-card-header">
            <div class="source-name">
              <span class="twitter-icon">🐦</span>
              @{{ source.username }}
            </div>
            <span class="badge" :class="getTwitterStatusClass(source.status)">
              {{ source.status }}
            </span>
          </div>
          <div class="source-stats">
            <div class="source-stat" :class="{ danger: source.fail_count > 5 }">
              <span class="stat-label">Failures</span>
              <span class="stat-value">{{ source.fail_count }}</span>
            </div>
            <div class="source-stat">
              <span class="stat-label">Last Used</span>
              <span class="stat-value">{{ formatTime(source.last_used_at) }}</span>
            </div>
          </div>
          <div class="source-error" v-if="source.last_error">
            <span class="error-label">Last Error:</span>
            <span class="error-text">{{ source.last_error }}</span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state fade-in">
        <span class="empty-icon">📭</span>
        <p>No {{ serviceType }} sources found</p>
        <button v-if="serviceType === 'daily'" class="btn" @click="showAddForm = true">Add First Source</button>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { sourcesApi } from '../api'

export default {
  name: 'Sources',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const adding = ref(false)
    const allSources = ref([])
    const serviceType = ref('daily')
    const showAddForm = ref(false)

    const newSource = ref({
      name: '',
      url: ''
    })

    const serviceTitle = computed(() => {
      const titles = {
        daily: 'Daily News RSS Sources',
        breaking: 'Breaking News Sources',
        twitter: 'Twitter Accounts'
      }
      return titles[serviceType.value] || 'Sources'
    })

    const sources = computed(() => allSources.value)

    const loadSources = async () => {
      loading.value = true
      error.value = null
      try {
        const data = await sourcesApi.list(serviceType.value)
        allSources.value = data.sources || []
      } catch (e) {
        error.value = e.message || 'Failed to load sources'
      } finally {
        loading.value = false
      }
    }

    watch(serviceType, () => {
      loadSources()
    })

    const addSource = async () => {
      adding.value = true
      try {
        await sourcesApi.add(newSource.value.url, newSource.value.name)
        newSource.value = { name: '', url: '' }
        showAddForm.value = false
        await loadSources()
      } catch (e) {
        error.value = e.message || 'Failed to add source'
      } finally {
        adding.value = false
      }
    }

    const toggleSource = async (source) => {
      try {
        await sourcesApi.toggle(source.id)
        await loadSources()
      } catch (e) {
        error.value = e.message || 'Failed to toggle source'
      }
    }

    const deleteSource = async (source) => {
      if (!confirm(`Delete ${source.name}?`)) return
      try {
        await sourcesApi.delete(source.id)
        await loadSources()
      } catch (e) {
        error.value = e.message || 'Failed to delete source'
      }
    }

    const truncateUrl = (url) => {
      if (!url) return ''
      return url.length > 50 ? url.substring(0, 50) + '...' : url
    }

    const getTwitterStatusClass = (status) => {
      const classes = {
        active: 'badge-success',
        cooling: 'badge-warning',
        error: 'badge-danger'
      }
      return classes[status] || 'badge-info'
    }

    const formatTime = (time) => {
      if (!time) return '-'
      return new Date(time).toLocaleString('zh-CN')
    }

    onMounted(() => {
      loadSources()
    })

    return {
      loading,
      error,
      adding,
      sources,
      serviceType,
      serviceTitle,
      showAddForm,
      newSource,
      addSource,
      toggleSource,
      deleteSource,
      truncateUrl,
      getTwitterStatusClass,
      formatTime,
      loadSources
    }
  }
}
</script>

<style scoped>
.tabs-container {
  margin-bottom: 20px;
}

.tabs {
  display: flex;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 8px;
  border-radius: 12px;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
  font-weight: 500;
}

.tab:hover {
  background: var(--bg-tertiary);
}

.tab.active {
  background: var(--accent);
  color: white;
}

.tab-icon {
  font-size: 16px;
}

.tab-badge {
  background: rgba(255, 255, 255, 0.3);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

/* Header */
.sources-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.sources-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.sources-title h3 {
  margin: 0;
}

.sources-count {
  font-size: 14px;
  color: var(--text-muted);
}

/* Add Form */
.add-form {
  background: var(--bg-tertiary);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.add-form h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input {
  padding: 10px 14px;
  border: 1px solid var(--border-color-dark);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  background: var(--accent);
  color: white;
}

/* Loading/Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--bg-secondary);
  border-radius: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: var(--text-secondary);
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* Sources Grid */
.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.source-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 1px solid var(--border-color);
  transition: transform 0.2s, box-shadow 0.2s;
}

.source-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.source-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-name {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.twitter-icon {
  color: #1da1f2;
}

.source-url {
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-url a {
  color: var(--accent);
  text-decoration: none;
}

.source-url a:hover {
  text-decoration: underline;
}

.source-meta {
  display: flex;
  gap: 8px;
}

.platform-tag {
  background: var(--bg-tertiary);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.source-stats {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.source-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.source-stat.success .stat-value {
  color: #4ade80;
}

.source-stat.danger .stat-value {
  color: #ef4444;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.error-text {
  font-size: 12px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
}

.source-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.source-error {
  display: flex;
  gap: 8px;
  font-size: 12px;
  padding: 8px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 6px;
}

.error-label {
  color: var(--text-muted);
}

.source-error .error-text {
  color: #ef4444;
  max-width: none;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--bg-secondary);
  border-radius: 16px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  color: var(--text-muted);
  margin-bottom: 16px;
}
</style>
