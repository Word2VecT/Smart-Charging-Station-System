import { useAdminAuth } from './useAdminAuth'
import { useState } from '#app'

interface AdminPile {
  pile_id: number
  pile_code: string
  type: string
  status: string
  power_rate: number
}

export const useAdminPile = () => {
  const { api, apiFetch } = useAdminAuth()  // ✅ 加上 apiFetch
  const piles = useState<AdminPile[]>('admin_piles', () => [])

  const fetchPiles = async () => {
    try {
      const data = await api('/admin/piles')
      piles.value = data
    } catch (error) {
      console.error('获取充电桩失败', error)
      piles.value = []
    }
  }

  return {
    piles,
    fetchPiles,
    apiFetch, // ✅ 返回 apiFetch，供前端调用 PATCH 请求
  }
}
