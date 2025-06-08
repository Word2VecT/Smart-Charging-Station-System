import { useAdminAuth } from './useAdminAuth'
import { useState } from '#app'

interface AdminRequest {
  request_id: number
  user_id: number
  requested_charge_type: string
  status: string
  request_time: string
}

export const useAdminRequests = () => {
  const { api } = useAdminAuth()
  const requests = useState<AdminRequest[]>('admin_requests', () => [])

  const fetchRequests = async () => {
    try {
      const data = await api('/admin/requests')
      requests.value = data
    } catch (error) {
      console.error('获取请求失败', error)
      requests.value = []
    }
  }

  return { requests, fetchRequests }
}
