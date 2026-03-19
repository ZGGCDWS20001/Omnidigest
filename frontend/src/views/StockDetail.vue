<template>
  <div class="stock-detail">
    <!-- Back Button -->
    <button class="back-btn" @click="goBack">
      ← Back to A-Stock
    </button>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading stock data...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <!-- Stock Header -->
      <div class="stock-header fade-in">
        <div class="stock-title">
          <h1>{{ stock.name || stock.symbol }}</h1>
          <span class="stock-symbol">{{ stock.symbol }}</span>
        </div>
        <div class="stock-price" :class="getChangeClass(stock.change)">
          <span class="price">{{ formatNumber(stock.price) }}</span>
          <span class="change">{{ formatChange(stock.change) }}</span>
          <span class="change-percent">({{ formatPercent(stock.change) }})</span>
        </div>
      </div>

      <!-- Price Stats -->
      <div class="grid grid-4 fade-in" style="margin-top: 20px;">
        <div class="stat-card">
          <div class="stat-label">Open</div>
          <div class="stat-value">{{ formatNumber(stock.open) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">High</div>
          <div class="stat-value">{{ formatNumber(stock.high) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Low</div>
          <div class="stat-value">{{ formatNumber(stock.low) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Prev Close</div>
          <div class="stat-value">{{ formatNumber(stock.prev_close) }}</div>
        </div>
      </div>

      <!-- Volume Stats -->
      <div class="grid grid-2 fade-in" style="margin-top: 20px;">
        <div class="stat-card">
          <div class="stat-label">Volume</div>
          <div class="stat-value">{{ formatVolume(stock.volume) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Turnover</div>
          <div class="stat-value">{{ formatTurnover(stock.turnover) }}</div>
        </div>
      </div>

      <!-- Stock News -->
      <div class="card news-card fade-in" style="margin-top: 20px;">
        <div class="card-header">
          <h3>📰 Related News</h3>
          <button class="btn btn-sm" @click="loadStockNews" :disabled="newsLoading">
            {{ newsLoading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
        <div class="news-list">
          <div v-if="stockNews.length === 0" class="empty-news">
            No related news available
          </div>
          <div
            v-for="item in stockNews"
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
            <div v-if="item.content" class="news-content">
              {{ truncateContent(item.content) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Update Time -->
      <div class="update-time" v-if="stock.update_time">
        Updated: {{ stock.update_time }}
      </div>
    </template>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { astockApi } from '../api'

export default {
  name: 'StockDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()

    const loading = ref(true)
    const error = ref(null)
    const newsLoading = ref(false)
    const stock = ref({})
    const stockNews = ref([])

    const symbol = ref('')

    const loadStockData = async () => {
      loading.value = true
      error.value = null
      try {
        const data = await astockApi.stockQuote(symbol.value)
        stock.value = data || {}
      } catch (e) {
        error.value = e.message || 'Failed to load stock data'
      } finally {
        loading.value = false
      }
    }

    const loadStockNews = async () => {
      newsLoading.value = true
      try {
        const data = await astockApi.stockNews(symbol.value, 20)
        stockNews.value = data?.news || []
      } catch (e) {
        // Silently fail
      } finally {
        newsLoading.value = false
      }
    }

    const goBack = () => {
      router.push('/stocks')
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

    const formatPercent = (change) => {
      if (change === null || change === undefined) return '-'
      const sign = change >= 0 ? '+' : ''
      return sign + Number(change).toFixed(2) + '%'
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

    const truncateContent = (content) => {
      if (!content) return ''
      return content.length > 100 ? content.substring(0, 100) + '...' : content
    }

    const getChangeClass = (change) => {
      if (change === null || change === undefined) return ''
      return change >= 0 ? 'price-up' : 'price-down'
    }

    const init = () => {
      symbol.value = route.params.symbol
      if (symbol.value) {
        loadStockData()
        loadStockNews()
      }
    }

    onMounted(() => {
      init()
    })

    watch(() => route.params.symbol, () => {
      if (route.params.symbol) {
        init()
      }
    })

    return {
      loading,
      error,
      newsLoading,
      stock,
      stockNews,
      goBack,
      loadStockNews,
      formatNumber,
      formatChange,
      formatPercent,
      formatVolume,
      formatTurnover,
      formatNewsTime,
      truncateContent,
      getChangeClass
    }
  }
}
</script>

<style scoped>
.stock-detail {
  min-height: 400px;
}

.back-btn {
  background: var(--bg-tertiary);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 16px;
}

.back-btn:hover {
  background: var(--border-color);
}

/* Stock Header */
.stock-header {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 24px;
}

.stock-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.stock-title h1 {
  margin: 0;
  font-size: 28px;
}

.stock-symbol {
  font-size: 14px;
  color: var(--text-muted);
  font-family: monospace;
}

.stock-price {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.stock-price .price {
  font-size: 48px;
  font-weight: 700;
}

.stock-price .change {
  font-size: 24px;
  font-weight: 600;
}

.stock-price .change-percent {
  font-size: 18px;
}

.price-up .change,
.price-up .change-percent {
  color: #ef4444;
}

.price-down .change,
.price-down .change-percent {
  color: #3b82f6;
}

/* Stats */
.stat-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
}

/* News */
.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  margin-bottom: 4px;
}

.news-title:hover {
  color: var(--accent);
}

.news-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.empty-news {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}

/* Update Time */
.update-time {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .back-btn {
    min-height: 44px;
    padding: 12px 20px;
    font-size: 14px;
  }

  .stock-header {
    padding: 16px;
  }

  .stock-title {
    flex-direction: column;
    gap: 4px;
  }

  .stock-title h1 {
    font-size: 22px;
  }

  .stock-symbol {
    font-size: 12px;
  }

  .stock-price {
    flex-wrap: wrap;
  }

  .stock-price .price {
    font-size: 32px;
  }

  .stock-price .change {
    font-size: 18px;
  }

  .stock-price .change-percent {
    font-size: 14px;
  }

  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-label {
    font-size: 11px;
  }

  .stat-value {
    font-size: 16px;
  }

  .grid-2 {
    grid-template-columns: 1fr;
  }

  .news-item {
    padding: 10px;
  }

  .news-title {
    font-size: 14px;
  }

  .news-content {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .back-btn {
    min-height: 48px;
    padding: 14px 20px;
    font-size: 15px;
    width: 100%;
    text-align: center;
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .stock-header {
    padding: 14px;
  }

  .stock-title h1 {
    font-size: 20px;
  }

  .stock-symbol {
    font-size: 11px;
  }

  .stock-price .price {
    font-size: 28px;
  }

  .stock-price .change {
    font-size: 16px;
  }

  .stock-price .change-percent {
    font-size: 14px;
  }

  .grid-4 {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-label {
    font-size: 10px;
    margin-bottom: 4px;
  }

  .stat-value {
    font-size: 15px;
  }

  .grid-2 {
    gap: 10px;
  }

  .stat-card {
    padding: 12px;
  }

  .news-list {
    gap: 10px;
  }

  .news-item {
    padding: 12px;
  }

  .news-meta {
    flex-direction: column;
    gap: 4px;
  }

  .news-time,
  .news-source {
    font-size: 10px;
  }

  .news-title {
    font-size: 13px;
    line-height: 1.4;
  }

  .news-content {
    font-size: 12px;
    margin-top: 6px;
  }

  /* Button Touch Optimization */
  .btn {
    min-height: 44px;
    padding: 12px 20px;
    font-size: 14px;
    border-radius: 8px;
  }

  .btn-sm {
    min-height: 40px;
    padding: 10px 16px;
    font-size: 13px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .card-header h3 {
    font-size: 14px;
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }
}

/* Extra small mobile */
@media (max-width: 375px) {
  .stock-header {
    padding: 12px;
  }

  .stock-title h1 {
    font-size: 18px;
  }

  .stock-price .price {
    font-size: 24px;
  }

  .stock-price .change {
    font-size: 14px;
  }

  .stock-price .change-percent {
    font-size: 12px;
  }

  .grid-4 {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .stat-card {
    padding: 10px;
  }

  .stat-value {
    font-size: 14px;
  }

  .news-title {
    font-size: 12px;
  }
}
</style>
