<template>
  <div class="astock-dashboard">
    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading A-Stock data...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- Market Session Indicator -->
      <div class="market-session-indicator" :class="marketSession">
        <span class="session-dot"></span>
        <span class="session-text">{{ marketSessionText }}</span>
        <span class="session-time">{{ currentTime }}</span>
      </div>

      <!-- Quote Cards -->
      <div class="grid grid-2 fade-in">
        <!-- Shanghai Index -->
        <div class="quote-card" :class="getQuoteClass(quotes.shanghai)">
          <div class="quote-header">
            <span class="quote-name">{{ quotes.shanghai?.name || 'Shanghai Composite' }}</span>
            <span class="quote-symbol">{{ quotes.shanghai?.symbol || 'sh000001' }}</span>
          </div>
          <div class="quote-body">
            <div class="quote-price">{{ formatNumber(quotes.shanghai?.price) }}</div>
            <div class="quote-change" :class="getChangeClass(quotes.shanghai?.change)">
              <span class="change-value">{{ formatChange(quotes.shanghai?.change) }}</span>
              <span class="change-percent">({{ formatPercent(quotes.shanghai?.change) }})</span>
            </div>
          </div>
          <div class="quote-stats">
            <div class="quote-stat">
              <span class="stat-label">Volume</span>
              <span class="stat-value">{{ formatVolume(quotes.shanghai?.volume) }}</span>
            </div>
            <div class="quote-stat">
              <span class="stat-label">Turnover</span>
              <span class="stat-value">{{ formatTurnover(quotes.shanghai?.turnover) }}</span>
            </div>
          </div>
        </div>

        <!-- Shenzhen Index -->
        <div class="quote-card" :class="getQuoteClass(quotes.shenzhen)">
          <div class="quote-header">
            <span class="quote-name">{{ quotes.shenzhen?.name || 'Shenzhen Component' }}</span>
            <span class="quote-symbol">{{ quotes.shenzhen?.symbol || 'sz399001' }}</span>
          </div>
          <div class="quote-body">
            <div class="quote-price">{{ formatNumber(quotes.shenzhen?.price) }}</div>
            <div class="quote-change" :class="getChangeClass(quotes.shenzhen?.change)">
              <span class="change-value">{{ formatChange(quotes.shenzhen?.change) }}</span>
              <span class="change-percent">({{ formatPercent(quotes.shenzhen?.change) }})</span>
            </div>
          </div>
          <div class="quote-stats">
            <div class="quote-stat">
              <span class="stat-label">Volume</span>
              <span class="stat-value">{{ formatVolume(quotes.shenzhen?.volume) }}</span>
            </div>
            <div class="quote-stat">
              <span class="stat-label">Turnover</span>
              <span class="stat-value">{{ formatTurnover(quotes.shenzhen?.turnover) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Analysis & Sectors -->
      <div class="grid grid-2 fade-in" style="margin-top: 20px;">
        <!-- Latest Analysis -->
        <div class="card analysis-card">
          <div class="card-header">
            <h3>📈 AI Analysis</h3>
            <span class="analysis-time" v-if="latestAnalysis?.prediction_date">
              {{ latestAnalysis.prediction_date }}
            </span>
          </div>
          <div class="analysis-content" v-if="latestAnalysis">
            <div class="analysis-item">
              <span class="analysis-label">Shanghai Composite</span>
              <span class="analysis-value" :class="getDirectionClass(latestAnalysis.shanghai?.direction)">
                {{ latestAnalysis.shanghai?.direction || '-' }}
              </span>
              <span class="analysis-confidence">
                Confidence: {{ latestAnalysis.shanghai?.confidence || 0 }}%
              </span>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">Shenzhen Component</span>
              <span class="analysis-value" :class="getDirectionClass(latestAnalysis.shenzhen?.direction)">
                {{ latestAnalysis.shenzhen?.direction || '-' }}
              </span>
              <span class="analysis-confidence">
                Confidence: {{ latestAnalysis.shenzhen?.confidence || 0 }}%
              </span>
            </div>
            <div class="analysis-sentiment" v-if="latestAnalysis.overall_sentiment">
              <span class="sentiment-label">Market Sentiment:</span>
              <span class="sentiment-value">{{ latestAnalysis.overall_sentiment }}</span>
            </div>
            <div class="analysis-drivers" v-if="latestAnalysis.key_drivers?.length">
              <span class="drivers-label">Key Drivers:</span>
              <div class="drivers-tags">
                <span v-for="driver in latestAnalysis.key_drivers" :key="driver" class="driver-tag">
                  {{ driver }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-analysis">
            <span>No analysis data available</span>
            <button class="btn" @click="triggerAnalysis" :disabled="analyzing">
              {{ analyzing ? 'Analyzing...' : 'Trigger Analysis' }}
            </button>
          </div>
        </div>

        <!-- Sector Ranking -->
        <div class="card sectors-card">
          <div class="card-header">
            <h3>🏭 Sector Performance</h3>
          </div>
          <div class="sectors-list">
            <div v-if="sectors.length === 0" class="empty-sectors">
              No sector data available
            </div>
            <div
              v-for="(sector, index) in sectors"
              :key="sector.name"
              class="sector-item"
            >
              <span class="sector-rank">{{ index + 1 }}</span>
              <span class="sector-name">{{ sector.name }}</span>
              <span class="sector-change" :class="getChangeClass(sector.change)">
                {{ formatPercent(sector.change) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Financial News -->
      <div class="card news-card fade-in" style="margin-top: 20px;">
        <div class="card-header">
          <h3>📰 Financial News</h3>
          <button class="btn btn-sm" @click="loadNews">
            Refresh
          </button>
        </div>
        <div class="news-grid">
          <div v-if="news.length === 0" class="empty-news">
            No news available
          </div>
          <div
            v-for="item in news"
            :key="item.id || item.title"
            class="news-item"
          >
            <div class="news-meta">
              <span class="news-time">{{ formatNewsTime(item.publish_time) }}</span>
              <span v-if="item.source" class="news-source">{{ item.source }}</span>
            </div>
            <a v-if="item.url" :href="item.url" target="_blank" class="news-title">
              {{ item.title }}
            </a>
            <div v-else class="news-title">{{ item.title }}</div>
            <div v-if="item.symbols?.length" class="news-tags">
              <span
                v-for="stock in item.symbols.slice(0, 5)"
                :key="stock"
                class="stock-tag"
              >
                {{ stock }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Accuracy Stats -->
      <div class="card accuracy-card fade-in" style="margin-top: 20px;">
        <div class="card-header">
          <h3>🎯 Prediction Accuracy</h3>
        </div>
        <div class="accuracy-grid" v-if="accuracy">
          <div class="accuracy-item">
            <div class="accuracy-value">{{ accuracy.overall_accuracy || 0 }}%</div>
            <div class="accuracy-label">Overall Accuracy</div>
          </div>
          <div class="accuracy-item">
            <div class="accuracy-value">{{ accuracy.total_predictions || 0 }}</div>
            <div class="accuracy-label">Total Predictions</div>
          </div>
          <div class="accuracy-item">
            <div class="accuracy-value">{{ accuracy.recent_accuracy || 0 }}%</div>
            <div class="accuracy-label">Recent Accuracy</div>
          </div>
          <div class="accuracy-item">
            <div class="accuracy-value">{{ accuracy.correct_predictions || 0 }}</div>
            <div class="accuracy-label">Correct Predictions</div>
          </div>
        </div>
        <div v-else class="empty-accuracy">
          No accuracy data available
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { astockApi } from '../api'

export default {
  name: 'AStockDashboard',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const analyzing = ref(false)

    // Data
    const quotes = ref({})
    const sectors = ref([])
    const news = ref([])
    const latestAnalysis = ref(null)
    const accuracy = ref(null)

    // Time
    const currentTime = ref('')
    let timeInterval = null

    const marketSession = computed(() => {
      return quotes.value.market_session || 'closed'
    })

    const marketSessionText = computed(() => {
      const texts = {
        pre_market: 'Pre-Market',
        morning: 'Morning',
        lunch: 'Lunch',
        afternoon: 'Afternoon',
        closed: 'Closed'
      }
      return texts[marketSession.value] || 'Unknown'
    })

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        const [quotesData, sectorsData, newsData, analysisData, accuracyData] = await Promise.all([
          astockApi.quotes().catch(() => ({})),
          astockApi.sectors().catch(() => []),
          astockApi.news(20).catch(() => []),
          astockApi.latestAnalysis().catch(() => null),
          astockApi.accuracy().catch(() => null)
        ])

        quotes.value = quotesData || {}
        sectors.value = sectorsData?.sectors || sectorsData || []
        news.value = newsData?.news || newsData || []
        latestAnalysis.value = analysisData || null
        accuracy.value = accuracyData || null
      } catch (e) {
        error.value = e.message || 'Failed to load A-Stock data'
      } finally {
        loading.value = false
      }
    }

    const loadNews = async () => {
      try {
        const data = await astockApi.news(20)
        news.value = data?.news || data || []
      } catch (e) {
        // Silently fail
      }
    }

    const triggerAnalysis = async () => {
      analyzing.value = true
      try {
        await astockApi.triggerAnalysis()
        // Reload analysis after trigger
        setTimeout(async () => {
          const data = await astockApi.latestAnalysis()
          latestAnalysis.value = data || null
        }, 2000)
      } catch (e) {
        error.value = 'Failed to trigger analysis'
      } finally {
        analyzing.value = false
      }
    }

    // Formatters
    const formatNumber = (num) => {
      if (num === null || num === undefined) return '-'
      return Number(num).toFixed(2)
    }

    const formatChange = (change) => {
      if (change === null || change === undefined) return '-'
      const sign = change >= 0 ? '+' : ''
      return sign + Number(change).toFixed(2)
    }

    const formatPercent = (percent) => {
      if (percent === null || percent === undefined) return '-'
      const sign = percent >= 0 ? '+' : ''
      return sign + Number(percent).toFixed(2) + '%'
    }

    const formatVolume = (volume) => {
      if (!volume) return '-'
      if (volume >= 100000000) return (volume / 100000000).toFixed(2) + 'B'
      if (volume >= 10000) return (volume / 10000).toFixed(2) + 'M'
      return volume
    }

    const formatTurnover = (turnover) => {
      if (!turnover) return '-'
      if (turnover >= 100000000) return (turnover / 100000000).toFixed(2) + 'B'
      if (turnover >= 10000) return (turnover / 10000).toFixed(2) + 'M'
      return turnover
    }

    const formatNewsTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      const now = new Date()
      const diff = now - date
      const hours = Math.floor(diff / 3600000)
      if (hours < 1) return 'Just now'
      if (hours < 24) return `${hours}h ago`
      return date.toLocaleDateString('zh-CN')
    }

    const getQuoteClass = (quote) => {
      if (!quote?.change) return ''
      return quote.change >= 0 ? 'quote-up' : 'quote-down'
    }

    const getChangeClass = (change) => {
      if (change === null || change === undefined) return ''
      return change >= 0 ? 'change-up' : 'change-down'
    }

    const getDirectionClass = (direction) => {
      if (!direction) return ''
      const upKeywords = ['上涨', '看涨', '多头', '涨', 'rise', 'up', 'bullish', 'gain']
      const downKeywords = ['下跌', '看跌', '空头', '跌', 'fall', 'down', 'bearish', 'drop']
      if (upKeywords.some(k => direction.includes(k))) return 'direction-up'
      if (downKeywords.some(k => direction.includes(k))) return 'direction-down'
      return 'direction-neutral'
    }

    const updateTime = () => {
      const now = new Date()
      currentTime.value = now.toLocaleString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    onMounted(() => {
      loadData()
      updateTime()
      timeInterval = setInterval(updateTime, 1000)
    })

    onUnmounted(() => {
      if (timeInterval) {
        clearInterval(timeInterval)
      }
    })

    return {
      loading,
      error,
      analyzing,
      quotes,
      sectors,
      news,
      latestAnalysis,
      accuracy,
      currentTime,
      marketSession,
      marketSessionText,
      loadNews,
      triggerAnalysis,
      formatNumber,
      formatChange,
      formatPercent,
      formatVolume,
      formatTurnover,
      formatNewsTime,
      getQuoteClass,
      getChangeClass,
      getDirectionClass
    }
  }
}
</script>

<style scoped>
.astock-dashboard {
  min-height: 400px;
}

/* Market Session Indicator */
.market-session-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
}

.session-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6b7280;
}

.market-session-indicator.pre_market .session-dot,
.market-session-indicator.morning .session-dot,
.market-session-indicator.afternoon .session-dot {
  background: #4ade80;
  animation: pulse 2s infinite;
}

.market-session-indicator.closed .session-dot {
  background: #6b7280;
}

.session-text {
  font-weight: 500;
}

.session-time {
  margin-left: auto;
  color: var(--text-muted);
}

/* Quote Cards */
.quote-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.quote-card.quote-up {
  border-color: rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), transparent);
}

.quote-card.quote-down {
  border-color: rgba(59, 130, 246, 0.3);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), transparent);
}

.quote-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.quote-name {
  font-size: 18px;
  font-weight: 600;
}

.quote-symbol {
  font-size: 12px;
  color: var(--text-muted);
  font-family: monospace;
}

.quote-body {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 16px;
}

.quote-price {
  font-size: 36px;
  font-weight: 700;
}

.quote-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 18px;
  font-weight: 500;
}

.change-up {
  color: #ef4444;
}

.change-down {
  color: #3b82f6;
}

.quote-stats {
  display: flex;
  gap: 24px;
}

.quote-stat {
  display: flex;
  flex-direction: column;
}

.quote-stat .stat-label {
  font-size: 11px;
  color: var(--text-muted);
}

.quote-stat .stat-value {
  font-size: 14px;
  font-weight: 500;
}

/* Analysis Card */
.analysis-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analysis-time {
  font-size: 12px;
  color: var(--text-muted);
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.analysis-label {
  font-size: 13px;
  color: var(--text-secondary);
  min-width: 60px;
}

.analysis-value {
  font-size: 16px;
  font-weight: 600;
}

.direction-up {
  color: #ef4444;
}

.direction-down {
  color: #3b82f6;
}

.direction-neutral {
  color: #fbbf24;
}

.analysis-confidence {
  font-size: 11px;
  color: var(--text-muted);
}

.analysis-sentiment {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.sentiment-label {
  font-size: 12px;
  color: var(--text-muted);
}

.sentiment-value {
  font-weight: 500;
  color: #4ade80;
}

.analysis-drivers {
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.drivers-label {
  font-size: 12px;
  color: var(--text-muted);
  display: block;
  margin-bottom: 8px;
}

.drivers-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.driver-tag {
  background: var(--bg-tertiary);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.empty-analysis {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  color: var(--text-muted);
}

/* Sectors Card */
.sectors-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sector-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.sector-rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.sector-item:nth-child(1) .sector-rank {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.sector-item:nth-child(2) .sector-rank {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.sector-item:nth-child(3) .sector-rank {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.sector-name {
  flex: 1;
  font-size: 14px;
}

.sector-change {
  font-weight: 600;
  font-size: 14px;
}

.empty-sectors {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
}

/* News Card */
.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.news-item {
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.news-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 11px;
}

.news-time {
  color: var(--text-muted);
}

.news-source {
  color: var(--accent);
}

.news-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  text-decoration: none;
  line-height: 1.4;
  margin-bottom: 8px;
}

.news-title:hover {
  color: var(--accent);
}

.news-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.stock-tag {
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-family: monospace;
}

.empty-news {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
  grid-column: 1 / -1;
}

/* Accuracy Card */
.accuracy-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.accuracy-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.accuracy-value {
  font-size: 28px;
  font-weight: 700;
  color: #4ade80;
}

.accuracy-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.empty-accuracy {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
}

/* Responsive - Tablet */
@media (max-width: 768px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }

  .quote-card {
    padding: 16px;
  }

  .quote-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .quote-name {
    font-size: 16px;
  }

  .quote-symbol {
    font-size: 11px;
  }

  .quote-body {
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .quote-price {
    font-size: 28px;
  }

  .quote-change {
    font-size: 16px;
  }

  .quote-stats {
    gap: 12px;
    flex-wrap: wrap;
  }

  .quote-stat {
    flex: 1;
    min-width: 80px;
  }

  /* Analysis Card */
  .analysis-item {
    flex-wrap: wrap;
    gap: 8px;
  }

  .analysis-label {
    min-width: 50px;
    font-size: 12px;
  }

  .analysis-value {
    font-size: 14px;
  }

  .analysis-confidence {
    font-size: 10px;
  }

  /* Sector List - Horizontal Scroll */
  .sectors-list {
    flex-direction: row;
    overflow-x: auto;
    gap: 12px;
    padding-bottom: 8px;
  }

  .sector-item {
    min-width: 140px;
    flex-shrink: 0;
  }

  /* News Grid - Single Column */
  .news-grid {
    grid-template-columns: 1fr;
  }

  /* Accuracy Card */
  .accuracy-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .accuracy-item {
    padding: 12px;
  }

  .accuracy-value {
    font-size: 20px;
  }

  .accuracy-label {
    font-size: 11px;
  }

  /* Button Touch Optimization */
  .btn {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 20px;
    font-size: 14px;
  }

  /* Market Indicator */
  .market-session-indicator {
    padding: 10px 12px;
    font-size: 12px;
  }
}

/* Responsive - Mobile */
@media (max-width: 480px) {
  .quote-card {
    padding: 14px;
  }

  .quote-name {
    font-size: 14px;
  }

  .quote-price {
    font-size: 24px;
  }

  .quote-change {
    font-size: 14px;
  }

  .change-percent {
    font-size: 12px;
  }

  .quote-stats {
    flex-direction: column;
    gap: 8px;
  }

  .quote-stat {
    flex-direction: row;
    justify-content: space-between;
  }

  .quote-stat .stat-label {
    font-size: 11px;
  }

  .quote-stat .stat-value {
    font-size: 13px;
  }

  /* Sector Ranking - Compact Mode */
  .sectors-list {
    gap: 8px;
  }

  .sector-item {
    min-width: 120px;
    padding: 8px 10px;
  }

  .sector-rank {
    width: 20px;
    height: 20px;
    font-size: 11px;
  }

  .sector-name {
    font-size: 12px;
  }

  .sector-change {
    font-size: 12px;
  }

  /* News */
  .news-item {
    padding: 10px;
  }

  .news-title {
    font-size: 13px;
  }

  .news-tags {
    flex-wrap: wrap;
  }

  .stock-tag {
    font-size: 10px;
    padding: 2px 6px;
  }

  /* Accuracy */
  .accuracy-grid {
    grid-template-columns: 1fr;
  }

  .accuracy-value {
    font-size: 18px;
  }

  /* Analysis Panel */
  .analysis-sentiment,
  .analysis-drivers {
    padding-top: 8px;
  }

  .drivers-tags {
    gap: 4px;
  }

  .driver-tag {
    font-size: 11px;
    padding: 3px 8px;
  }

  /* Button - Min Touch Area */
  .btn {
    min-height: 48px;
    min-width: 48px;
    padding: 14px 24px;
    font-size: 15px;
    border-radius: 8px;
  }

  .btn-sm {
    min-height: 40px;
    min-width: 40px;
    padding: 10px 16px;
    font-size: 13px;
  }

  /* Card Title */
  .card h3 {
    font-size: 14px;
  }

  /* Loading State */
  .loading {
    padding: 30px;
    font-size: 14px;
  }
}

/* Extra small mobile */
@media (max-width: 375px) {
  .quote-card {
    padding: 12px;
  }

  .quote-price {
    font-size: 22px;
  }

  .quote-change {
    font-size: 13px;
  }

  .quote-stats {
    gap: 6px;
  }

  .quote-stat .stat-label {
    font-size: 10px;
  }

  .quote-stat .stat-value {
    font-size: 12px;
  }

  .sector-item {
    min-width: 110px;
  }

  .sector-name {
    font-size: 11px;
  }

  .news-title {
    font-size: 12px;
  }

  .accuracy-value {
    font-size: 16px;
  }

  .btn {
    padding: 12px 20px;
    font-size: 14px;
  }
}
</style>
