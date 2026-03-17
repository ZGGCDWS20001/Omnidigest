<template>
  <div class="config">
    <div v-if="loading" class="loading">Loading configuration...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <div class="tabs">
        <div
          v-for="section in sections"
          :key="section"
          class="tab"
          :class="{ active: activeSection === section }"
          @click="activeSection = section"
        >
          {{ formatSectionName(section) }}
        </div>
      </div>

      <div class="card">
        <h3>{{ formatSectionName(activeSection) }}</h3>

        <div v-if="saving" class="loading">Saving...</div>
        <template v-else>
          <div v-if="configItems.length === 0" class="loading">
            No configuration items. Add new ones below.
          </div>
          <table v-else>
            <thead>
              <tr>
                <th>Key</th>
                <th>Value</th>
                <th>Type</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in configItems" :key="item.id || item.key">
                <td><code>{{ item.key }}</code></td>
                <td>
                  <input
                    v-if="editingKey === item.key"
                    v-model="editValue"
                    type="text"
                    class="form-control"
                  />
                  <code v-else>{{ item.value }}</code>
                </td>
                <td>{{ item.value_type }}</td>
                <td>{{ item.description || '-' }}</td>
                <td>
                  <template v-if="editingKey === item.key">
                    <button class="btn" @click="saveEdit(item)">Save</button>
                    <button class="btn btn-secondary" @click="cancelEdit">Cancel</button>
                  </template>
                  <template v-else>
                    <button class="btn btn-secondary" @click="startEdit(item)">Edit</button>
                    <button class="btn btn-danger" @click="deleteItem(item)">Delete</button>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Add New Config -->
          <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
            <h4>Add New Configuration</h4>
            <div class="grid grid-4">
              <div class="form-group">
                <label>Key</label>
                <input v-model="newItem.key" type="text" placeholder="e.g., BREAKING_IMPACT_THRESHOLD" />
              </div>
              <div class="form-group">
                <label>Value</label>
                <input v-model="newItem.value" type="text" placeholder="Value" />
              </div>
              <div class="form-group">
                <label>Type</label>
                <select v-model="newItem.value_type">
                  <option value="string">String</option>
                  <option value="int">Integer</option>
                  <option value="bool">Boolean</option>
                  <option value="json">JSON</option>
                </select>
              </div>
              <div class="form-group">
                <label>Description</label>
                <input v-model="newItem.description" type="text" placeholder="Description" />
              </div>
            </div>
            <button class="btn" @click="addItem" :disabled="!newItem.key || !newItem.value">
              Add Configuration
            </button>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { configApi } from '../api'

export default {
  name: 'Config',
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const saving = ref(false)
    const allConfig = ref({})
    const activeSection = ref('breaking')

    const editingKey = ref(null)
    const editValue = ref('')

    const newItem = ref({
      key: '',
      value: '',
      value_type: 'string',
      description: ''
    })

    const sections = computed(() => Object.keys(allConfig.value))
    const configItems = computed(() => allConfig.value[activeSection.value] || [])

    const loadConfig = async () => {
      loading.value = true
      error.value = null
      try {
        const data = await configApi.getAll()
        allConfig.value = data.config || {}
        if (sections.value.length > 0 && !sections.value.includes(activeSection.value)) {
          activeSection.value = sections.value[0]
        }
      } catch (e) {
        error.value = e.message || 'Failed to load configuration'
      } finally {
        loading.value = false
      }
    }

    const formatSectionName = (section) => {
      const names = {
        breaking: 'Breaking News',
        twitter: 'Twitter',
        notifications: 'Notifications',
        scheduler: 'Scheduler'
      }
      return names[section] || section
    }

    const startEdit = (item) => {
      editingKey.value = item.key
      editValue.value = item.value
    }

    const cancelEdit = () => {
      editingKey.value = null
      editValue.value = ''
    }

    const saveEdit = async (item) => {
      saving.value = true
      try {
        await configApi.updateSection(activeSection.value, [{
          key: item.key,
          value: editValue.value,
          value_type: item.value_type,
          description: item.description
        }])
        await loadConfig()
        cancelEdit()
      } catch (e) {
        error.value = e.message || 'Failed to save'
      } finally {
        saving.value = false
      }
    }

    const deleteItem = async (item) => {
      if (!confirm(`Delete ${item.key}?`)) return
      saving.value = true
      try {
        await configApi.delete(activeSection.value, item.key)
        await loadConfig()
      } catch (e) {
        error.value = e.message || 'Failed to delete'
      } finally {
        saving.value = false
      }
    }

    const addItem = async () => {
      saving.value = true
      try {
        await configApi.create(
          activeSection.value,
          newItem.value.key,
          newItem.value.value,
          newItem.value.value_type,
          newItem.value.description
        )
        newItem.value = { key: '', value: '', value_type: 'string', description: '' }
        await loadConfig()
      } catch (e) {
        error.value = e.message || 'Failed to add'
      } finally {
        saving.value = false
      }
    }

    onMounted(() => {
      loadConfig()
    })

    return {
      loading,
      error,
      saving,
      sections,
      activeSection,
      configItems,
      editingKey,
      editValue,
      newItem,
      formatSectionName,
      startEdit,
      cancelEdit,
      saveEdit,
      deleteItem,
      addItem
    }
  }
}
</script>

<style scoped>
.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  margin-right: 8px;
}
</style>
