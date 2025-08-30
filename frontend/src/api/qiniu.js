import apiClient from './index.js'

/**
 * 七牛云文件上传相关API
 */
export const qiniuAPI = {
  /**
   * 获取上传token
   * @param {string} fileKey - 文件key
   * @param {string} purpose - 上传目的
   */
  getUploadToken(fileKey, purpose = '用户文件上传') {
    return apiClient.post('/qiniu/upload-token', {
      token_type: 'upload',
      file_key: fileKey,
      purpose: purpose
    })
  },

  /**
   * 获取bucket信息
   */
  getBucketInfo() {
    return apiClient.get('/qiniu/bucket-info')
  },

  /**
   * 上传文件到七牛云
   * @param {File} file - 文件对象
   * @param {string} token - 上传token
   * @param {string} key - 文件key
   * @param {string} uploadUrl - 上传域名
   * @param {Function} onProgress - 进度回调
   */
  uploadFile(file, token, key, uploadUrl, onProgress) {
    return new Promise((resolve, reject) => {
      const formData = new FormData()
      formData.append('key', key)
      formData.append('token', token)
      formData.append('file', file)

      const xhr = new XMLHttpRequest()

      // 监听上传进度
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const percent = Math.round((event.loaded / event.total) * 100)
          onProgress(percent)
        }
      })

      // 上传完成处理
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const result = JSON.parse(xhr.responseText)
            resolve(result)
          } catch (error) {
            reject(new Error('解析响应失败'))
          }
        } else {
          reject(new Error(`HTTP ${xhr.status}`))
        }
      })

      // 上传错误处理
      xhr.addEventListener('error', (error) => {
        reject(error)
      })

      xhr.open('POST', uploadUrl)
      xhr.send(formData)
    })
  },

  /**
   * 生成文件key
   * @param {string} prefix - 前缀路径
   * @param {string} filename - 原始文件名
   */
  generateFileKey(prefix, filename) {
    const timestamp = Date.now()
    const randomStr = Math.random().toString(36).substring(2, 8)
    const fileExtension = filename.split('.').pop()
    return `${prefix}/${timestamp}_${randomStr}.${fileExtension}`
  }
}