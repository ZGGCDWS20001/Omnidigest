<template>
  <div class="knowledge-graph">
    <!-- KG Not Enabled State -->
    <div v-if="!kgEnabled" class="kg-disabled">
      <div class="kg-disabled-icon">🔗</div>
      <h3>Knowledge Graph</h3>
      <p>Knowledge Graph is not enabled</p>
      <button class="btn" @click="showNotification">
        Explore Knowledge Graph
      </button>
    </div>

    <!-- KG Enabled - Main Content -->
    <template v-else>
      <!-- Search and Path Query Panel -->
      <div class="card fade-in search-panel">
        <div class="search-row">
          <!-- Entity Search -->
          <div class="search-group">
            <input
              v-model="searchName"
              type="text"
              placeholder="Search entity name..."
              class="search-input"
              @keyup.enter="searchEntities"
            />
            <select v-model="searchType" class="search-select">
              <option value="">All Types</option>
              <option value="Person">Person</option>
              <option value="Organization">Organization</option>
              <option value="Location">Location</option>
            </select>
            <button class="btn btn-sm" @click="searchEntities">Search</button>
          </div>

          <!-- Path Search -->
          <div class="search-group path-search">
            <input
              v-model="pathStart"
              type="text"
              placeholder="Start entity..."
              class="search-input"
            />
            <span class="path-arrow">→</span>
            <input
              v-model="pathEnd"
              type="text"
              placeholder="End entity..."
              class="search-input"
            />
            <button class="btn btn-sm" @click="searchPath">Find Path</button>
          </div>
        </div>

        <!-- Search Results -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div class="search-results-header">
            <span>Search Results ({{ searchResults.length }})</span>
            <button class="btn-close" @click="searchResults = []">×</button>
          </div>
          <div class="search-results-list">
            <div
              v-for="entity in searchResults"
              :key="entity.uid"
              class="search-result-item"
              @click="selectEntity(entity)"
            >
              <span class="entity-type-badge" :style="{ background: getTypeColor(entity['dgraph.type']) }">
                {{ entity['dgraph.type'] || 'Unknown' }}
              </span>
              <span class="entity-name">{{ entity.name }}</span>
              <span v-if="entity.sources" class="entity-sources">{{ entity.sources.length }} sources</span>
            </div>
          </div>
        </div>

        <!-- Path Results -->
        <div v-if="pathResults.length > 0" class="path-results">
          <div class="path-results-header">
            <span>Paths Found ({{ pathResults.length }})</span>
            <button class="btn-close" @click="pathResults = []">×</button>
          </div>
          <div v-for="(path, idx) in pathResults" :key="idx" class="path-item">
            <span v-for="(node, i) in path" :key="i" class="path-node">
              {{ node.name }}<span v-if="i < path.length - 1" class="path-sep"> → </span>
            </span>
          </div>
        </div>
      </div>

      <!-- Entity Details Sidebar -->
      <div v-if="selectedEntity" class="entity-sidebar">
        <div class="sidebar-header">
          <h3>Entity Details</h3>
          <button class="btn-close" @click="selectedEntity = null">×</button>
        </div>
        <div class="sidebar-content">
          <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">{{ selectedEntity.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Type:</span>
            <span class="entity-type-badge" :style="{ background: getTypeColor(selectedEntity['dgraph.type']) }">
              {{ selectedEntity['dgraph.type'] || 'Unknown' }}
            </span>
          </div>
          <div v-if="selectedEntity.description" class="detail-row">
            <span class="detail-label">Description:</span>
            <span class="detail-value">{{ selectedEntity.description }}</span>
          </div>
          <div v-if="selectedEntity.aliases && selectedEntity.aliases.length" class="detail-row">
            <span class="detail-label">Aliases:</span>
            <span class="detail-value">{{ selectedEntity.aliases.join(', ') }}</span>
          </div>
          <div v-if="selectedEntity.sources && selectedEntity.sources.length" class="detail-row">
            <span class="detail-label">Sources:</span>
            <span class="detail-value">{{ selectedEntity.sources.length }} articles</span>
          </div>
          <div v-if="selectedEntity.confidence" class="detail-row">
            <span class="detail-label">Confidence:</span>
            <span class="detail-value">{{ (selectedEntity.confidence * 100).toFixed(1) }}%</span>
          </div>

          <!-- Related Entities -->
          <div v-if="selectedEntity.related_to && selectedEntity.related_to.length" class="related-section">
            <h4>Related To</h4>
            <div
              v-for="rel in selectedEntity.related_to"
              :key="rel.uid"
              class="related-item"
              @click="selectEntityByUid(rel.uid)"
            >
              <span class="entity-type-badge" :style="{ background: getTypeColor(rel['dgraph.type']) }">
                {{ rel['dgraph.type'] || 'Unknown' }}
              </span>
              <span class="entity-name">{{ rel.name }}</span>
            </div>
          </div>

          <div v-if="selectedEntity['~related_to'] && selectedEntity['~related_to'].length" class="related-section">
            <h4>Related From</h4>
            <div
              v-for="rel in selectedEntity['~related_to']"
              :key="rel.uid"
              class="related-item"
              @click="selectEntityByUid(rel.uid)"
            >
              <span class="entity-type-badge" :style="{ background: getTypeColor(rel['dgraph.type']) }">
                {{ rel['dgraph.type'] || 'Unknown' }}
              </span>
              <span class="entity-name">{{ rel.name }}</span>
            </div>
          </div>

          <!-- Mentioned In Events -->
          <div v-if="selectedEntity.mentioned_in && selectedEntity.mentioned_in.length" class="related-section">
            <h4>Mentioned In Events</h4>
            <div
              v-for="event in selectedEntity.mentioned_in"
              :key="event.uid"
              class="event-item"
            >
              <span class="event-title">{{ event.title }}</span>
              <span v-if="event.category" class="event-category">{{ event.category }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Graph Preview - Now below search, shows person connections by default -->
      <div class="card fade-in graph-section">
        <div class="graph-header">
          <h3>{{ graphTitle }}</h3>
          <button v-if="hasSearchResults" class="btn btn-sm" @click="clearGraphSearch">Show All Person Relations</button>
        </div>
        <div class="graph-preview">
          <svg v-if="graphNodes.length > 0" viewBox="0 0 800 400" class="graph-svg">
            <!-- Connections -->
            <g class="connections">
              <line
                v-for="(conn, idx) in graphConnections"
                :key="'conn-' + idx"
                :x1="conn.x1"
                :y1="conn.y1"
                :x2="conn.x2"
                :y2="conn.y2"
                class="connection-line"
              />
            </g>
            <!-- Nodes -->
            <g class="nodes">
              <g
                v-for="node in graphNodes"
                :key="node.id"
                class="node"
                :transform="'translate(' + node.x + ',' + node.y + ')'"
                @click="handleNodeClick(node)"
              >
                <circle
                  r="20"
                  :fill="node.color"
                  class="node-circle"
                />
                <text
                  y="35"
                  text-anchor="middle"
                  class="node-label"
                >
                  {{ node.label }}
                </text>
              </g>
            </g>
          </svg>
          <div v-else class="graph-empty">
            <span>No graph data available</span>
          </div>
          <div class="graph-overlay">
            <span>{{ graphSubtitle }}</span>
          </div>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-4 fade-in stats-overview">
        <div class="stat-card">
          <div class="label">Total Entities</div>
          <div class="value">{{ stats.total_entities || 0 }}</div>
          <div class="sub">in graph</div>
        </div>
        <div class="stat-card">
          <div class="label">Total Relations</div>
          <div class="value">{{ stats.total_relations || 0 }}</div>
          <div class="sub">connections</div>
        </div>
        <div class="stat-card">
          <div class="label">Extracted Today</div>
          <div class="value">{{ stats.extracted_today || 0 }}</div>
          <div class="sub">new triples</div>
        </div>
        <div class="stat-card">
          <div class="label">Last Extraction</div>
          <div class="value time">{{ formatTime(stats.last_extraction) }}</div>
          <div class="sub">timestamp</div>
        </div>
      </div>

      <!-- Entity Type Distribution -->
      <div class="card fade-in" style="animation-delay: 0.1s">
        <h3>Entity Distribution</h3>
        <div class="entity-types">
          <div
            v-for="type in entityTypes"
            :key="type.name"
            class="entity-type"
            :style="{ '--type-color': type.color }"
          >
            <div class="entity-icon">{{ type.icon }}</div>
            <div class="entity-info">
              <div class="entity-name">{{ type.name }}</div>
              <div class="entity-count">{{ type.count }}</div>
            </div>
            <div class="entity-bar">
              <div class="entity-bar-fill" :style="{ width: type.percentage + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Extractions -->
      <div class="grid grid-2 fade-in" style="animation-delay: 0.2s">
        <div class="card">
          <h3>Recent Entities</h3>
          <div class="entity-list">
            <div
              v-for="entity in recentEntities"
              :key="entity.uid"
              class="entity-item clickable"
              @click="selectEntityByUid(entity.uid)"
            >
              <span class="entity-type-badge" :style="{ background: getTypeColor(entity.type) }">
                {{ entity.type }}
              </span>
              <span class="entity-name">{{ entity.name }}</span>
              <span class="entity-relations">{{ entity.relation_count || 0 }} relations</span>
            </div>
            <div v-if="recentEntities.length === 0" class="loading">
              No entities yet
            </div>
          </div>
        </div>

        <div class="card">
          <h3>Top Relations</h3>
          <div class="relation-list">
            <div
              v-for="relation in topRelations"
              :key="relation.type"
              class="relation-item"
            >
              <div class="relation-type">{{ relation.type }}</div>
              <div class="relation-count">{{ relation.count }}</div>
            </div>
            <div v-if="topRelations.length === 0" class="loading">
              No relations yet
            </div>
          </div>
        </div>
      </div>

      <!-- Graph Preview -->
      <div class="card fade-in" style="animation-delay: 0.3s">
        <h3>Graph Preview</h3>
        <div class="graph-preview">
          <svg viewBox="0 0 800 400" class="graph-svg">
            <!-- Animated connections -->
            <g class="connections">
              <line
                v-for="(conn, idx) in graphConnections"
                :key="'conn-' + idx"
                :x1="conn.x1"
                :y1="conn.y1"
                :x2="conn.x2"
                :y2="conn.y2"
                class="connection-line"
              />
            </g>
            <!-- Nodes -->
            <g class="nodes">
              <g
                v-for="node in graphNodes"
                :key="node.id"
                class="node"
                :transform="'translate(' + node.x + ',' + node.y + ')'"
                @click="handleNodeClick(node)"
              >
                <circle
                  r="20"
                  :fill="node.color"
                  class="node-circle"
                />
                <text
                  y="35"
                  text-anchor="middle"
                  class="node-label"
                >
                  {{ node.label }}
                </text>
              </g>
            </g>
          </svg>
          <div class="graph-overlay">
            <span>Live Graph Visualization</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Notification Toast -->
    <div v-if="showToast" class="toast" :class="toastType">
      <span class="toast-icon">{{ toastType === 'warning' ? '⚠️' : 'ℹ️' }}</span>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { kgApi } from '../api'

export default {
  name: 'KnowledgeGraph',
  setup() {
    const kgEnabled = ref(false) // Will be set from backend
    const loading = ref(true)
    const showToast = ref(false)
    const toastMessage = ref('')
    const toastType = ref('info')

    // Search state
    const searchName = ref('')
    const searchType = ref('')
    const searchResults = ref([])
    const selectedEntity = ref(null)

    // Path search state
    const pathStart = ref('')
    const pathEnd = ref('')
    const pathResults = ref([])

    const stats = ref({
      total_entities: 0,
      total_relations: 0,
      extracted_today: 0,
      last_extraction: null
    })

    const entityTypes = ref([
      { name: 'Person', icon: '👤', count: 0, color: '#4ade80', percentage: 0 },
      { name: 'Organization', icon: '🏢', count: 0, color: '#60a5fa', percentage: 0 },
      { name: 'Location', icon: '📍', count: 0, color: '#f472b6', percentage: 0 },
      { name: 'Event', icon: '📅', count: 0, color: '#fbbf24', percentage: 0 }
    ])

    const recentEntities = ref([])
    const topRelations = ref([])

    // Graph data
    const graphNodes = ref([])
    const graphConnections = ref([])
    const isSearchGraph = ref(false)

    // Computed properties for graph
    const graphTitle = computed(() => isSearchGraph.value ? 'Search Results Graph' : 'Person Relations')
    const graphSubtitle = computed(() => isSearchGraph.value ? 'Showing search results' : 'Live Person Network')
    const hasSearchResults = computed(() => searchResults.value.length > 0)

    // Load graph data - fetch person relations
    const loadGraphData = async () => {
      try {
        // Get relations between entities
        const response = await kgApi.getRelations({ limit: 100 })
        if (response.status === 'ok' && response.relations) {
          buildGraphFromRelations(response.relations)
        }
      } catch (e) {
        // Handle error silently
      }
    }

    // Build graph from relations data
    const buildGraphFromRelations = (relations) => {
      const nodeMap = {}
      const nodes = []
      const connections = []
      const colors = {
        'Person': '#4ade80',
        'Organization': '#60a5fa',
        'Location': '#f472b6',
        'Event': '#fbbf24'
      }

      // Filter to only show Person connections when not searching
      const filteredRelations = isSearchGraph.value
        ? relations
        : relations.filter(r => r.source_type === 'Person' || r.target_type === 'Person')

      // Build nodes
      filteredRelations.forEach(rel => {
        if (!nodeMap[rel.source_uid]) {
          nodeMap[rel.source_uid] = {
            id: rel.source_uid,
            name: rel.source_name,
            type: rel.source_type,
            color: colors[rel.source_type] || '#888'
          }
        }
        if (!nodeMap[rel.target_uid]) {
          nodeMap[rel.target_uid] = {
            id: rel.target_uid,
            name: rel.target_name,
            type: rel.target_type,
            color: colors[rel.target_type] || '#888'
          }
        }
      })

      // Convert to array and limit
      const nodeArray = Object.values(nodeMap).slice(0, 15)
      nodeArray.forEach((node, idx) => {
        // Position in circle
        const angle = (2 * Math.PI * idx) / nodeArray.length
        const centerX = 400, centerY = 200, radius = 150
        node.x = centerX + radius * Math.cos(angle)
        node.y = centerY + radius * Math.sin(angle)
        node.label = node.name ? node.name.substring(0, 10) : 'Unknown'
      })

      // Build connections
      filteredRelations.forEach(rel => {
        const sourceNode = nodeArray.find(n => n.id === rel.source_uid)
        const targetNode = nodeArray.find(n => n.id === rel.target_uid)
        if (sourceNode && targetNode) {
          connections.push({
            x1: sourceNode.x,
            y1: sourceNode.y,
            x2: targetNode.x,
            y2: targetNode.y
          })
        }
      })

      graphNodes.value = nodeArray
      graphConnections.value = connections.slice(0, 20)
    }

    // Clear graph search and return to default view
    const clearGraphSearch = () => {
      isSearchGraph.value = false
      searchResults.value = []
      loadGraphData()
    }

    const showNotification = () => {
      showToast.value = true
      toastMessage.value = 'Knowledge Graph is not enabled. Please enable it in configuration.'
      toastType.value = 'warning'
      setTimeout(() => {
        showToast.value = false
      }, 3000)
    }

    const formatTime = (time) => {
      if (!time) return '-'
      return new Date(time).toLocaleString('zh-CN')
    }

    const getTypeColor = (type) => {
      if (!type) return '#888'
      const found = entityTypes.value.find(t => t.name === type)
      return found ? found.color : '#888'
    }

    // Search entities
    const searchEntities = async () => {
      if (!searchName.value && !searchType.value) {
        toastMessage.value = 'Please enter a search term or select a type'
        toastType.value = 'warning'
        showToast.value = true
        setTimeout(() => { showToast.value = false }, 3000)
        return
      }

      try {
        const params = {}
        if (searchName.value) params.name = searchName.value
        if (searchType.value) params.entity_type = searchType.value

        const response = await kgApi.searchEntities(params)
        if (response.status === 'ok') {
          searchResults.value = response.entities || []

          // Also load relations for graph visualization
          if (searchResults.value.length > 0) {
            isSearchGraph.value = true
            // Get relations involving these entities
            const entityUids = searchResults.value.slice(0, 5).map(e => e.uid)
            // For now, just load all relations and filter client-side
            const relResponse = await kgApi.getRelations({ limit: 100 })
            if (relResponse.status === 'ok' && relResponse.relations) {
              // Filter to only show relations involving searched entities
              const filteredRels = relResponse.relations.filter(r =>
                entityUids.includes(r.source_uid) || entityUids.includes(r.target_uid)
              )
              buildGraphFromRelations(filteredRels)
            }
          }
        }
      } catch (e) {
        toastMessage.value = 'Failed to search entities'
        toastType.value = 'warning'
        showToast.value = true
        setTimeout(() => { showToast.value = false }, 3000)
      }
    }

    // Select entity from search results
    const selectEntity = async (entity) => {
      try {
        const response = await kgApi.getEntity(entity.uid)
        if (response.status === 'ok') {
          selectedEntity.value = response.entity
        }
      } catch (e) {
        // Handle error silently
      }
    }

    // Select entity by UID
    const selectEntityByUid = async (uid) => {
      try {
        const response = await kgApi.getEntity(uid)
        if (response.status === 'ok') {
          selectedEntity.value = response.entity
        }
      } catch (e) {
        // Handle error silently
      }
    }

    // Handle node click in graph
    const handleNodeClick = (node) => {
      selectEntityByUid(node.id)
    }

    // Search path between entities
    const searchPath = async () => {
      if (!pathStart.value || !pathEnd.value) {
        toastMessage.value = 'Please enter both start and end entities'
        toastType.value = 'warning'
        showToast.value = true
        setTimeout(() => { showToast.value = false }, 3000)
        return
      }

      try {
        const response = await kgApi.searchPath({
          start: pathStart.value,
          end: pathEnd.value
        })
        if (response.status === 'ok') {
          pathResults.value = response.paths || []
          if (pathResults.value.length === 0) {
            toastMessage.value = 'No path found between these entities'
            toastType.value = 'info'
            showToast.value = true
            setTimeout(() => { showToast.value = false }, 3000)
          }
        }
      } catch (e) {
        toastMessage.value = 'Failed to search path'
        toastType.value = 'warning'
        showToast.value = true
        setTimeout(() => { showToast.value = false }, 3000)
      }
    }

    // Check if KG is enabled from settings
    const checkKgStatus = async () => {
      try {
        const response = await kgApi.status()
        kgEnabled.value = response.enabled

        // If enabled, load stats
        if (kgEnabled.value) {
          const statsResponse = await kgApi.stats()

          // Check for error in response
          if (statsResponse.status === 'error') {
            toastMessage.value = statsResponse.message || 'Failed to load KG stats'
            toastType.value = 'warning'
            showToast.value = true
            setTimeout(() => { showToast.value = false }, 5000)
          }

          if (statsResponse.stats) {
            stats.value = statsResponse.stats

            // Update entity types from API response
            if (statsResponse.stats.entity_types && statsResponse.stats.entity_types.length > 0) {
              const total = statsResponse.stats.total_entities || 1
              entityTypes.value = statsResponse.stats.entity_types.map(type => ({
                ...type,
                percentage: total > 0 ? (type.count / total * 100).toFixed(1) : 0
              }))
            }

            // Update recent entities
            if (statsResponse.stats.recent_entities) {
              recentEntities.value = statsResponse.stats.recent_entities
            }

            // Update top relations
            if (statsResponse.stats.top_relations) {
              topRelations.value = statsResponse.stats.top_relations
            }

            // Update graph visualization data - load real relations for person network
            await loadGraphData()
          }
        }
      } catch (e) {
        kgEnabled.value = false
      }
      loading.value = false
    }

    onMounted(() => {
      checkKgStatus()
    })

    return {
      kgEnabled,
      loading,
      showToast,
      toastMessage,
      toastType,
      // Search
      searchName,
      searchType,
      searchResults,
      selectedEntity,
      pathStart,
      pathEnd,
      pathResults,
      // Stats
      stats,
      entityTypes,
      recentEntities,
      topRelations,
      graphNodes,
      graphConnections,
      graphTitle,
      graphSubtitle,
      hasSearchResults,
      // Methods
      showNotification,
      formatTime,
      getTypeColor,
      searchEntities,
      selectEntity,
      selectEntityByUid,
      clearGraphSearch,
      handleNodeClick,
      searchPath
    }
  }
}
</script>

<style scoped>
.knowledge-graph {
  min-height: 400px;
}

/* Disabled State */
.kg-disabled {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  background: var(--bg-secondary);
  border-radius: 16px;
  text-align: center;
  padding: 40px;
  opacity: 0.7;
}

.kg-disabled-icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

.kg-disabled h3 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.kg-disabled p {
  color: var(--text-muted);
  margin: 0 0 20px 0;
}

/* Search Panel */
.search-panel {
  margin-bottom: 24px;
}

.stats-overview {
  margin-bottom: 24px;
}

.search-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.search-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}

.search-group.path-search {
  min-width: 500px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
}

.search-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
}

.path-arrow {
  color: var(--text-muted);
  font-size: 18px;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

/* Search Results */
.search-results, .path-results {
  margin-top: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.search-results-header, .path-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--bg-tertiary);
  font-weight: 500;
}

.search-results-list {
  max-height: 200px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: var(--bg-tertiary);
}

.search-result-item:last-child {
  border-bottom: none;
}

.entity-sources {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
}

/* Path Results */
.path-item {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
}

.path-item:last-child {
  border-bottom: none;
}

.path-node {
  color: var(--text-primary);
}

.path-sep {
  color: var(--text-muted);
}

.btn-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-muted);
  padding: 0 4px;
}

.btn-close:hover {
  color: var(--text-primary);
}

/* Entity Sidebar */
.entity-sidebar {
  position: fixed;
  top: 80px;
  right: 20px;
  width: 360px;
  max-height: calc(100vh - 100px);
  background: var(--bg-secondary);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 100;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.sidebar-content {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

.detail-row {
  margin-bottom: 12px;
}

.detail-label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
}

.related-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.related-section h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.related-item:hover {
  background: var(--bg-tertiary);
}

.event-item {
  padding: 8px;
  border-radius: 6px;
  margin-bottom: 6px;
  background: var(--bg-tertiary);
}

.event-title {
  display: block;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.event-category {
  font-size: 11px;
  color: var(--text-muted);
}

/* Entity Distribution */
.entity-types {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.entity-type {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  transition: transform 0.2s;
}

.entity-type:hover {
  transform: translateX(4px);
}

.entity-icon {
  font-size: 24px;
  width: 40px;
  text-align: center;
}

.entity-info {
  flex: 1;
  min-width: 120px;
}

.entity-name {
  font-weight: 500;
  color: var(--text-primary);
}

.entity-count {
  font-size: 20px;
  font-weight: 600;
  color: var(--type-color);
}

.entity-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
  overflow: hidden;
}

.entity-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--type-color), transparent);
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* Lists */
.entity-list, .relation-list {
  max-height: 300px;
  overflow-y: auto;
}

.entity-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-bottom: 1px solid var(--border-color);
}

.entity-item:last-child {
  border-bottom: none;
}

.entity-item.clickable {
  cursor: pointer;
  transition: background 0.2s;
}

.entity-item.clickable:hover {
  background: var(--bg-tertiary);
}

.entity-type-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
  font-weight: 500;
}

.entity-relations {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
}

.relation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.relation-item:last-child {
  border-bottom: none;
}

.relation-type {
  font-weight: 500;
}

.relation-count {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent);
}

/* Graph Section */
.graph-section {
  margin-bottom: 24px;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.graph-header h3 {
  margin: 0;
}

/* Graph Preview */
.graph-preview {
  position: relative;
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
  border-radius: 12px;
  overflow: hidden;
  min-height: 400px;
}

.graph-svg {
  width: 100%;
  height: 400px;
}

.connection-line {
  stroke: var(--text-muted);
  stroke-width: 2;
  stroke-dasharray: 5, 5;
  animation: dash 20s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -1000;
  }
}

.node-circle {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  transition: r 0.3s;
}

.node {
  cursor: pointer;
}

.node:hover .node-circle {
  r: 25;
}

.node-label {
  fill: var(--text-primary);
  font-size: 12px;
  font-weight: 500;
}

.graph-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-muted);
}

.graph-overlay {
  position: absolute;
  bottom: 16px;
  right: 16px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-muted);
  box-shadow: 0 2px 8px var(--shadow);
}

/* Time value */
.stat-card .value.time {
  font-size: 24px;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
  animation: slideIn 0.3s ease;
  z-index: 1000;
  border-left: 4px solid var(--accent);
}

.toast.warning {
  border-left-color: #fbbf24;
}

.toast-icon {
  font-size: 20px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-item {
    padding: 14px;
  }

  .stat-number {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }

  .entities-grid {
    grid-template-columns: 1fr;
  }

  .entity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .entity-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .entity-title {
    font-size: 14px;
  }

  .entity-meta {
    font-size: 12px;
  }

  .entity-bar {
    height: 8px;
  }

  .entity-bar-fill {
    height: 100%;
  }

  .entity-content {
    font-size: 13px;
    line-height: 1.5;
  }

  .graph-svg {
    height: 300px;
  }

  .graph-preview {
    min-height: 300px;
  }

  .graph-empty {
    height: 300px;
  }

  .related-entities-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .related-entity-card {
    padding: 10px;
  }

  .related-entity-name {
    font-size: 12px;
  }

  .related-entity-type {
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }

  .stat-item {
    padding: 12px;
  }

  .stat-number {
    font-size: 20px;
  }

  .stat-label {
    font-size: 11px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }

  .entity-card {
    padding: 12px;
  }

  .entity-content {
    font-size: 12px;
  }

  .entity-tags {
    flex-wrap: wrap;
  }

  .entity-tag {
    font-size: 10px;
    padding: 2px 6px;
  }

  .graph-svg {
    height: 250px;
  }

  .graph-preview {
    min-height: 250px;
  }

  .graph-empty {
    height: 250px;
    font-size: 14px;
  }

  .node-label {
    font-size: 10px;
  }

  .related-entities-grid {
    grid-template-columns: 1fr;
  }

  .toast-container {
    left: 10px;
    right: 10px;
  }

  .toast {
    padding: 10px 12px;
  }
}
</style>
