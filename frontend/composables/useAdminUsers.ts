import { useAdminAuth } from './useAdminAuth'
import { useState } from '#app'

interface AdminUser {
  user_id: number
  username: string
  role: string
}

export const useAdminUsers = () => {
  const { api } = useAdminAuth()
  const users = useState<AdminUser[]>('admin_users', () => [])

  const fetchUsers = async () => {
    try {
      const data = await api('/admin/users')
      users.value = data
    } catch (error) {
      console.error('获取用户失败', error)
      users.value = []
    }
  }

  return { users, fetchUsers }
}
