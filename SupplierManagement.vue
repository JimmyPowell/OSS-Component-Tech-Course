<template>
  <div class="supplier-management">
    <!-- 页面标题和描述 -->
    <div class="page-header">
      <h1 class="page-title">供应商信息管理</h1>
      <p class="page-subtitle">管理供应商信息列表，如供应商名称、地址等</p>
    </div>
    
    <!-- 操作按钮和搜索区域 -->
    <div class="action-bar">
      <div class="left-actions">
        <a-button type="primary" class="add-btn" @click="showAddDrawer">
          <template #icon><plus-outlined /></template>
          添加供应商
        </a-button>
        <a-button @click="uploadModalVisible = true">
          <template #icon><cloud-upload-outlined /></template>
          批量导入
        </a-button>
        <a-button class="refresh-btn" @click="fetchSuppliers">
          刷新
        </a-button>
        <a-button class="settings-btn" @click="showColumnSettings">
          <template #icon><setting-outlined /></template>
          列设置
        </a-button>
      </div>
      

      
      <div class="right-actions">
        <a-input 
          v-model:value="searchText"
          placeholder="名称/编号/POI"
          class="search-input rounded-input"
          allow-clear
        />
        <a-button type="primary" class="search-btn" @click="handleSearch(searchText)">
          查询
        </a-button>
        <a-button class="reset-btn" @click="handleReset">
          重置
        </a-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-section">
      <a-table
        :columns="columns"
        :data-source="suppliers"
        :pagination="paginationConfig"
        :loading="loading"
        row-key="uuid"
        @change="handleTableChange"
        size="middle"
      >
        <!-- 状态列自定义渲染 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'updated_at'">
            {{ formatDate(record.updated_at) }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" @click="showEditDrawer(record)" size="small">
                <template #icon><edit-outlined /></template>
                编辑
              </a-button>
              <a-popconfirm
                title="确定要删除这个供应商吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.uuid)"
              >
                <a-button type="link" danger size="small">
                  <template #icon><delete-outlined /></template>
                  删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 添加/编辑供应商抽屉 -->
    <a-drawer
      :open="drawerVisible"
      :width="480"
      placement="left"
      @close="closeDrawer"
      :mask-closable="false"
      :closable="false"
      class="custom-drawer"
    >
      <!-- 自定义抽屉头部，关闭按钮放在右侧 -->
      <template #title>
        <div class="custom-drawer-header">
          <div class="drawer-title">{{ drawerTitle }}</div>
          <button class="drawer-close" @click="closeDrawer">
            <span class="anticon anticon-close">
              <svg viewBox="64 64 896 896" data-icon="close" width="1em" height="1em" fill="currentColor" aria-hidden="true">
                <path d="M563.8 512l262.5-312.9c4.4-5.2.7-13.1-6.1-13.1h-79.8c-4.7 0-9.2 2.1-12.3 5.7L511.6 449.8 295.1 191.7c-3-3.6-7.5-5.7-12.3-5.7H203c-6.8 0-10.5 7.9-6.1 13.1L459.4 512 196.9 824.9A7.95 7.95 0 00203 838h79.8c4.7 0 9.2-2.1 12.3-5.7l216.5-258.1 216.5 258.1c3 3.6 7.5 5.7 12.3 5.7h79.8c6.8 0 10.5-7.9 6.1-13.1L563.8 512z"></path>
              </svg>
            </span>
          </button>
        </div>
      </template>
      <div v-if="!isEditing">
        <!-- 智能添加部分 -->
        <div class="smart-add-section">
          <h3>智能添加</h3>
          <a-auto-complete
            v-model:value="searchQuery"
            :options="searchResults"
            :filter-option="false"
            :default-active-first-option="false"
            @search="onSearch"
            @select="onSelectSearchResult"
            style="width: 100%"
          >
            <template #option="{ value, label, data }">  
              <div class="search-result-item">
                <div class="search-result-name">{{ data.name }}</div>
                <div class="search-result-address">{{ data.address }}</div>
              </div>
            </template>
            <template #default>
              <a-input 
                size="large" 
                placeholder="输入公司名称或POI" 
                v-model:value="searchQuery"
                class="rounded-input"
                allow-clear
              />
            </template>
          </a-auto-complete>
        </div>
        
        <!-- 手动填写折叠面板 -->
        <a-collapse 
          v-model:activeKey="activeKeys"
          class="manual-add-collapse"
        >
          <a-collapse-panel key="1" header="手动填写">
            <a-form
              :model="formData"
              :rules="formRules"
              layout="vertical"
              ref="formRef"
              @finish="handleSubmit"
            >
        <!-- 可自动填充的字段放在前面 -->
        <a-form-item label="供应商名称" name="name" required>
          <a-input v-model:value="formData.name" placeholder="请输入供应商名称" />
        </a-form-item>

        <a-form-item label="公司地址" class="address-form-item">
          <div class="address-row">
            <a-form-item name="province" class="address-item">
              <a-input v-model:value="addressFields.province" placeholder="省" />
            </a-form-item>
            <a-form-item name="city" class="address-item">
              <a-input v-model:value="addressFields.city" placeholder="市" />
            </a-form-item>
            <a-form-item name="district" class="address-item">
              <a-input v-model:value="addressFields.district" placeholder="区/县" />
            </a-form-item>
          </div>
          <a-form-item name="detailAddress">
            <a-textarea
              v-model:value="addressFields.detailAddress"
              placeholder="详细地址"
              :rows="2"
            />
          </a-form-item>
        </a-form-item>
        
        <a-form-item label="公司编号" name="company_id">
          <a-input v-model:value="formData.company_id" placeholder="请输入公司编号（可选）" />
        </a-form-item>

        <a-form-item label="POI ID" name="poi_id">
          <a-input v-model:value="formData.poi_id" placeholder="高德地图POI唯一标识（智能搜索自动填充）" readonly />
          <template #extra>通过智能搜索自动填充，不需要手动编辑</template>
        </a-form-item>
        
        <a-form-item label="地理位置" name="location">
          <a-input v-model:value="formData.location" placeholder="经纬度坐标（智能搜索自动填充）" readonly />
          <template #extra>格式：经度,纬度，通过智能搜索自动填充</template>
        </a-form-item>

        <!-- 手动填写的字段放在后面 -->
        <a-form-item label="联系人" name="contact_person">
          <a-input v-model:value="formData.contact_person" placeholder="请输入联系人姓名" />
        </a-form-item>

        <a-form-item label="联系电话" name="contact_phone">
          <a-input v-model:value="formData.contact_phone" placeholder="请输入联系电话" />
        </a-form-item>

        <a-form-item label="联系邮箱" name="contact_email">
          <a-input v-model:value="formData.contact_email" placeholder="请输入联系邮箱" />
        </a-form-item>

        <a-form-item label="状态" name="status" required>
          <a-select v-model:value="formData.status" placeholder="请选择状态">
            <a-select-option value="Active">活跃</a-select-option>
            <a-select-option value="Inactive">停用</a-select-option>
            <a-select-option value="Pending">待审核</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="描述" name="description">
          <a-textarea
            v-model:value="formData.description"
            placeholder="请输入供应商描述或备注"
            :rows="4"
          />
        </a-form-item>

        <div class="drawer-footer">
          <a-space>
            <a-button @click="closeDrawer">取消</a-button>
            <a-button type="primary" html-type="submit" :loading="submitLoading">
              {{ isEditing ? '更新' : '创建' }}
            </a-button>
          </a-space>
        </div>
            </a-form>
          </a-collapse-panel>
        </a-collapse>
      </div>
      
      <!-- 编辑状态下不显示智能添加 -->
      <a-form
        v-else
        :model="formData"
        :rules="formRules"
        layout="vertical"
        ref="formRef"
        @finish="handleSubmit"
      >
        <a-form-item label="供应商名称" name="name" required>
          <a-input v-model:value="formData.name" placeholder="请输入供应商名称" />
        </a-form-item>

        <a-form-item label="公司编号" name="company_id">
          <a-input v-model:value="formData.company_id" placeholder="请输入公司编号（可选）" />
        </a-form-item>

        <a-form-item label="联系人" name="contact_person">
          <a-input v-model:value="formData.contact_person" placeholder="请输入联系人姓名" />
        </a-form-item>

        <a-form-item label="联系电话" name="contact_phone">
          <a-input v-model:value="formData.contact_phone" placeholder="请输入联系电话" />
        </a-form-item>

        <a-form-item label="联系邮箱" name="contact_email">
          <a-input v-model:value="formData.contact_email" placeholder="请输入联系邮箱" />
        </a-form-item>
        
        <a-form-item label="地址" name="address">
          <a-textarea
            v-model:value="formData.address"
            placeholder="请输入供应商地址"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="状态" name="status" required>
          <a-select v-model:value="formData.status" placeholder="请选择状态">
            <a-select-option value="Active">活跃</a-select-option>
            <a-select-option value="Inactive">停用</a-select-option>
            <a-select-option value="Pending">待审核</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="描述" name="description">
          <a-textarea
            v-model:value="formData.description"
            placeholder="请输入供应商描述或备注"
            :rows="4"
          />
        </a-form-item>

        <div class="drawer-footer">
          <a-space>
            <a-button @click="closeDrawer">取消</a-button>
            <a-button type="primary" html-type="submit" :loading="submitLoading">
              {{ isEditing ? '更新' : '创建' }}
            </a-button>
          </a-space>
        </div>
      </a-form>
    </a-drawer>
  </div>

  <!-- 列设置对话框 -->
  <a-modal
    v-model:visible="columnSettingsVisible"
    title="列设置"
    width="500px"
    :footer="null"
  >
    <p class="modal-subtitle">选择要显示的列</p>
    <a-checkbox-group v-model:value="visibleColumns" style="width: 100%">
      <div class="column-settings-grid">
        <a-checkbox v-for="col in availableColumns" :key="col.key" :value="col.key">
          {{ col.title }}
        </a-checkbox>
      </div>
    </a-checkbox-group>
    <div class="column-settings-footer">
      <a-button @click="resetColumnSettings">重置</a-button>
      <a-button type="primary" @click="saveColumnSettings">保存</a-button>
    </div>
  </a-modal>

  <SupplierUploadModal 
    v-model:open="uploadModalVisible"
    @upload-success="handleUploadSuccess"
  />
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SettingOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons-vue'
import httpClient from '../utils/httpClient'
import { debounce } from 'lodash'
import SupplierUploadModal from './SupplierUploadModal.vue'

// 响应式数据
const suppliers = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const searchText = ref('')
const statusFilter = ref(undefined)
const drawerVisible = ref(false)
const isEditing = ref(false)
const editingUuid = ref('')
const formRef = ref()

// 批量上传相关
const uploadModalVisible = ref(false)

// 智能搜索相关
const searchQuery = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const activeKeys = ref([])

// 列设置相关
const columnSettingsVisible = ref(false)
const visibleColumns = ref([])
const defaultVisibleColumns = ['name', 'contact_person', 'contact_phone', 'contact_email', 'status', 'actions']


// 地址字段
const addressFields = reactive({
  province: '',
  city: '',
  district: '',
  detailAddress: ''
})

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
})

// 定义所有可用的列
const availableColumns = [
  {
    title: '供应商名称',
    dataIndex: 'name',
    key: 'name',
    width: 150,
  },
  {
    title: '联系人',
    dataIndex: 'contact_person',
    key: 'contact_person',
    width: 120,
  },
  {
    title: '联系电话',
    dataIndex: 'contact_phone',
    key: 'contact_phone',
    width: 130,
  },
  {
    title: '联系邮箱',
    dataIndex: 'contact_email',
    key: 'contact_email',
    width: 180,
  },
  {
    title: '地址',
    dataIndex: 'address',
    key: 'address',
    width: 200,
    ellipsis: true,
  },
  {
    title: '位置信息',
    dataIndex: 'location',
    key: 'location',
    width: 150,
    ellipsis: true,
  },
  {
    title: 'POI ID',
    dataIndex: 'poi_id',
    key: 'poi_id',
    width: 120,
    ellipsis: true,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    width: 200,
    ellipsis: true,
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    key: 'updated_at',
    width: 150,
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right',
  },
]

// 根据可见列动态计算实际显示的列
const columns = computed(() => {
  // 必须显示操作列
  const mustShowColumns = ['actions']
  
  // 过滤出需要显示的列
  return availableColumns.filter(col => {
    return visibleColumns.value.includes(col.key) || mustShowColumns.includes(col.key)
  })
})

// 表单数据
const formData = reactive({
  name: '',
  company_id: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: '',
  location: '', // 经纬度坐标
  poi_id: '', // 高德POI ID
  status: 'Active',
  description: '',
})

// 监听地址字段变化，自动合成address
watch([() => addressFields.province, () => addressFields.city, () => addressFields.district, () => addressFields.detailAddress], () => {
  if (isEditing.value) return // 编辑模式下不自动合成地址
  
  const addressParts = []
  if (addressFields.province) addressParts.push(addressFields.province)
  if (addressFields.city) addressParts.push(addressFields.city)
  if (addressFields.district) addressParts.push(addressFields.district)
  
  // 省市区用|分隔
  let formattedAddress = addressParts.join('|')
  
  // 如果有详细地址，添加到最后
  if (addressFields.detailAddress) {
    formattedAddress = formattedAddress ? `${formattedAddress} ${addressFields.detailAddress}` : addressFields.detailAddress
  }
  
  formData.address = formattedAddress
})

// 列设置相关函数

// 初始化列设置
const initColumnSettings = () => {
  try {
    // 尝试从 localStorage 加载已保存的列设置
    const savedColumns = localStorage.getItem('supplierVisibleColumns')
    if (savedColumns) {
      visibleColumns.value = JSON.parse(savedColumns)
    } else {
      // 使用默认设置
      visibleColumns.value = [...defaultVisibleColumns]
    }
  } catch (error) {
    console.error('加载列设置失败:', error)
    visibleColumns.value = [...defaultVisibleColumns]
  }
}

// 显示列设置对话框
const showColumnSettings = () => {
  columnSettingsVisible.value = true
}

// 保存列设置
const saveColumnSettings = () => {
  try {
    // 保存到localStorage
    localStorage.setItem('supplierVisibleColumns', JSON.stringify(visibleColumns.value))
    columnSettingsVisible.value = false
  } catch (error) {
    console.error('保存列设置失败:', error)
  }
}

// 重置列设置
const resetColumnSettings = () => {
  visibleColumns.value = [...defaultVisibleColumns]
}

// 监听searchQuery变化，自动触发搜索
watch(() => searchQuery.value, (newValue) => {
  if (newValue && newValue.length >= 2) {
    onSearch(newValue)
  } else {
    searchResults.value = []
  }
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入供应商名称', trigger: 'blur' },
    { min: 1, max: 255, message: '供应商名称长度应在1-255字符之间', trigger: 'blur' },
  ],
  contact_email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' },
  ],
}

// 计算属性
const drawerTitle = computed(() => isEditing.value ? '编辑供应商' : '添加供应商')
const paginationConfig = computed(() => ({
  ...pagination,
  onChange: (page, pageSize) => {
    pagination.current = page
    pagination.pageSize = pageSize
    fetchSuppliers()
  },
  onShowSizeChange: (current, size) => {
    pagination.current = 1
    pagination.pageSize = size
    fetchSuppliers()
  },
}))

// 获取供应商列表
const fetchSuppliers = async (isRetry = false) => {
  try {
    loading.value = true
    
    // 构建查询参数
    const params = new URLSearchParams()
    params.append('page', pagination.current)
    params.append('size', pagination.pageSize)
    
    if (searchText.value) {
      params.append('search', searchText.value)
    }
    
    if (statusFilter.value) {
      params.append('status', statusFilter.value)
    }
    
    // 打印详细请求信息以便调试
    console.log('Fetching suppliers with params:', params.toString())
    
    const response = await httpClient.get(`suppliers?${params}`)
    console.log('Suppliers response:', response)
    
    if (response.ok) {
      const result = await response.json()
      console.log('Suppliers data:', result) // 打印后端返回的数据
      
      suppliers.value = result.data.items || []
      pagination.total = result.data.total || 0
    } else {
      const errorText = await response.text()
      console.error('API错误响应:', errorText)
      
      // 如果是认证错误(403)且未重试过，尝试短暂延迟后重试一次
      // 这可能是因为令牌刚保存但尚未被httpClient加载的情况
      if (response.status === 403 && !isRetry) {
        console.log('检测到认证错误，将在500ms后重试请求...')
        setTimeout(() => fetchSuppliers(true), 500)
        return
      }
      
      throw new Error('获取供应商列表失败')
    }
  } catch (error) {
    console.error('获取供应商列表失败:', error)
    message.error('获取供应商列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.current = 1
  fetchSuppliers()
}

const handleSearchChange = (e) => {
  if (!e.target.value) {
    handleSearch()
  }
}

// 状态筛选
const handleStatusFilter = () => {
  pagination.current = 1
  fetchSuppliers()
}

// 重置搜索
const handleReset = () => {
  searchText.value = ''
  statusFilter.value = undefined
  pagination.current = 1
  fetchSuppliers()
}

// 表格变化处理
const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchSuppliers()
}

// 显示添加抽屉
const showAddDrawer = () => {
  isEditing.value = false
  editingUuid.value = ''
  drawerVisible.value = true
  nextTick(() => {
    resetForm()
    // 默认手动填写面板是关闭的
    activeKeys.value = []
  })
}

// 智能搜索
const onSearch = debounce(async (value) => {
  if (!value || value.length < 2) {
    searchResults.value = []
    return
  }
  
  searchLoading.value = true
  try {
    const response = await httpClient.get(`smart-search?q=${encodeURIComponent(value)}`)
    if (response.ok) {
      const data = await response.json()
      
      // 转换返回结果为AutoComplete需要的格式
      searchResults.value = data.results.map(item => ({
        value: item.id,
        label: item.name,
        data: item
      }))
    } else {
      searchResults.value = []
    }
  } catch (error) {
    console.error('智能搜索出错:', error)
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}, 300)

// 选择搜索结果
const onSelectSearchResult = (value, option) => {
  const poiData = option.data
  
  // 自动填充表单数据
  formData.name = poiData.name
  
  // 保存POI ID和位置信息
  formData.poi_id = poiData.id
  formData.location = poiData.location
  
  // 填充地址字段
  addressFields.province = poiData.pname || ''
  addressFields.city = poiData.cityname || ''
  addressFields.district = poiData.adname || ''
  addressFields.detailAddress = poiData.address || ''
  
  // 如果有电话，填充联系电话
  if (poiData.tel) {
    formData.contact_phone = poiData.tel
  }
  
  // 自动展开手动填写面板
  activeKeys.value = ['1']
  
  // 清空搜索框
  searchQuery.value = ''
}

// 显示编辑抽屉
const showEditDrawer = (record) => {
  isEditing.value = true
  editingUuid.value = record.uuid
  
  // 填充表单数据
  Object.keys(formData).forEach(key => {
    formData[key] = record[key] || ''
  })
  // 手动处理不匹配的字段名
  formData.company_id = record.uuid || ''
  
  drawerVisible.value = true
}

// 关闭抽屉
const closeDrawer = () => {
  drawerVisible.value = false
  // 重置操作统一在打开时进行，确保formRef可用
}

// 重置表单
const resetForm = () => {
  // 重置主表单数据
  Object.keys(formData).forEach(key => {
    if (key === 'status') {
      formData[key] = 'Active'
    } else {
      formData[key] = ''
    }
  })
  
  // 重置地址字段
  Object.keys(addressFields).forEach(key => {
    addressFields[key] = ''
  })
  
  // 清空搜索
  searchQuery.value = ''
  searchResults.value = []
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleUploadSuccess = () => {
  fetchSuppliers();
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    // 创建一个新对象，仅包含有值的字段
    const submitData = {}
    Object.entries(formData).forEach(([key, value]) => {
      // 如果字段有值，则添加到提交数据中
      if (value !== '' && value !== null && value !== undefined) {
        submitData[key] = value
      }
    })
    
    let response
    
    if (isEditing.value) {
      response = await httpClient.put(`suppliers/${editingUuid.value}`, submitData)
    } else {
      response = await httpClient.post('suppliers', submitData)
    }

    if (response.ok) {
      message.success(isEditing.value ? '供应商更新成功' : '供应商创建成功')
      closeDrawer()
      fetchSuppliers()
    } else {
      const result = await response.json()
      message.error(result.detail || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    message.error('操作时发生网络错误')
  } finally {
    submitLoading.value = false
  }
}

// 删除供应商
const handleDelete = async (uuid) => {
  try {
    const response = await httpClient.delete(`suppliers/${uuid}`)

    if (response.ok) {
      message.success('供应商删除成功')
      fetchSuppliers()
    } else {
      const result = await response.json()
      message.error(result.detail || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    message.error('删除时发生网络错误')
  }
}

// 工具函数
const getStatusColor = (status) => {
  const colors = {
    Active: 'green',
    Inactive: 'red',
    Pending: 'orange',
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    Active: '活跃',
    Inactive: '停用',
    Pending: '待审核',
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 在组件挂载时加载数据
onMounted(async () => {
  // 初始化列设置
  initColumnSettings()
  // 加载供应商数据
  await fetchSuppliers()
})

</script>

<style scoped>
.supplier-management {
  padding: 16px;
  background-color: #ffffff;
  height: auto;
}

/* 页面标题部分 */
.page-header {
  margin-bottom: 16px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 500;
  color: #262626;
}

.page-subtitle {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
}

/* 操作栏样式 - 使用横线分隔 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 0;
  border-bottom: 1px solid #f0f0f0;
}

.left-actions, .right-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 空心按钮样式，更细窄圆润 */
.add-btn,
.refresh-btn,
.settings-btn,
.search-btn,
.reset-btn {
  border-radius: 20px;
  height: 32px;
  font-weight: normal;
  box-shadow: none;
  background: transparent;
  padding: 0 14px;
}

.add-btn {
  font-weight: 500;
}

.search-input {
  min-width: 260px;
  height: 32px;
  border-radius: 30px;
}

.search-input :deep(.ant-input-wrapper) {
  display: flex;
  align-items: center;
  height: 32px;
}

/* 搜索框圆角和高度 */
.search-input :deep(.ant-input) {
  border-radius: 30px;
  height: 24px; /* 内部输入框略小 */
  font-size: 12px;
  padding: 0 12px 0 8px; /* 减少左侧内边距 */
  display: flex;
  align-items: center;
  text-indent: 0;
}

/* 强制内部元素对齐 */
.search-input :deep(.ant-input-affix-wrapper) {
  display: flex;
  align-items: center;
  padding: 0;
  height: 100%;
}

/* 搜索框placeholder样式 */
.search-input :deep(.ant-input::placeholder) {
  font-size: 11px;
  font-weight: 500;
  color: #bfbfbf;
}

/* 表格部分 - 移除阴影，使用横线 */
.table-section {
  background: #fff;
  padding: 8px 12px;
  border-radius: 12px;
  box-shadow: none;
}

/* 抽屉底部按钮区 - 移除阴影 */
.drawer-footer {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 100%;
  border-top: 1px solid #f0f0f0;
  padding: 12px 24px;
  background: #fff;
  text-align: right;
  box-shadow: none;
}

/* 统一表格样式 */
:deep(.ant-table) {
  border-radius: 12px;
  font-size: 13px;
}

:deep(.ant-table-thead > tr > th) {
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  padding: 8px 8px;
  font-weight: 500;
}

:deep(.ant-table-tbody > tr > td) {
  padding: 6px 8px;
}

:deep(.ant-table-row) {
  height: 40px;
}

:deep(.ant-pagination) {
  margin-top: 12px;
  margin-bottom: 0;
}

/* 统一按钮样式为空心且更细窄圆润 */
:deep(.ant-btn-primary) {
  background: transparent;
  color: #1890ff;
  border-color: #1890ff;
  height: 30px;
  padding: 0 12px;
}

:deep(.ant-btn-primary:hover) {
  background-color: rgba(24, 144, 255, 0.1);
  color: #1890ff;
  border-color: #1890ff;
}

:deep(.ant-btn) {
  border-radius: 20px;
  height: 28px;
  padding: 0 12px;
  font-size: 13px;
}


:deep(.ant-table-tbody > tr:hover > td) {
  background-color: #f5f5f5;
}

/* 抽屉样式优化 */
:deep(.ant-drawer-body) {
  padding-bottom: 80px;
}

:deep(.ant-form-item-label > label) {
  font-weight: 500;
  color: #262626;
}

/* 按钮样式 */
.ant-btn-primary {
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(24, 144, 255, 0.2);
}

.ant-btn {
  border-radius: 6px;
}

/* 标签样式 */
:deep(.ant-tag) {
  border-radius: 4px;
  font-weight: 500;
}

/* 智能添加部分样式 */
.smart-add-section {
  margin-bottom: 24px;
  padding: 16px;
  border-radius: 8px;
  background-color: #f9f9f9;
  border: 1px solid #f0f0f0;
}

/* 圆角输入框 */
.rounded-input :deep(.ant-input) {
  border-radius: 8px;
}

.smart-add-section :deep(.ant-select-selector) {
  border-radius: 8px !important;
}

.smart-add-section h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

/* 搜索结果样式 */
.search-result-item {
  padding: 8px 4px;
  cursor: pointer;
}

.search-result-name {
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
}

.search-result-address {
  font-size: 12px;
  color: #8c8c8c;
}

/* 地址输入样式 */
.address-form-item :deep(.ant-form-item-explain) {
  margin-top: -12px;
}

.address-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.address-item {
  flex: 1;
  margin-bottom: 0 !important;
}

/* 折叠面板样式 */
.manual-add-collapse {
  margin-bottom: 24px;
}

.manual-add-collapse :deep(.ant-collapse-header) {
  font-weight: 500;
}
/* 列设置对话框样式 */
.modal-subtitle {
  color: #666;
  margin-bottom: 16px;
}

.column-settings-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.column-settings-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
}

/* 自定义抽屉头部样式 */
.custom-drawer .custom-drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.custom-drawer .drawer-title {
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.custom-drawer .drawer-close {
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.45);
  line-height: 1;
  transition: color 0.3s;
}

.custom-drawer .drawer-close:hover {
  color: rgba(0, 0, 0, 0.75);
}

/* 无需重写ant-drawer-header相关样式了，因为我们使用完全自定义的头部 */
</style>
