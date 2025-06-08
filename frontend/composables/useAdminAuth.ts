// composables/useAdminAuth.ts
import { useState, useRouter } from '#app'
import { useCookie } from '#imports'

export const useAdminAuth = () => {
  const token = useCookie<string | null>('admin_token')
  const admin = useState<any | null>('admin_user', () => null)
  const router = useRouter()

  const apiFetch = (endpoint: string, options: any = {}) => {
    const headers = options.headers || {}
    if (token.value && !headers.Authorization) {
      headers.Authorization = `Bearer ${token.value}`
    }

    return $fetch(endpoint, {
      baseURL: 'http://localhost:8000',
      ...options,
      headers,
    })
  }

  const fetchAdmin = async (tokenOverride?: string) => {
    const currentToken = tokenOverride || token.value
    if (!currentToken) {
      admin.value = null
      return
    }

    try {
      const data = await apiFetch('/admin-auth/me', {
        headers: {
          Authorization: `Bearer ${currentToken}`
        }
      })
      admin.value = data
    } catch (error) {
      console.error('获取管理员信息失败', error)
      admin.value = null
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const data = await apiFetch('/admin-auth/token', {
        method: 'POST',
        body: formData
      })

      token.value = data.access_token

      await fetchAdmin(data.access_token)

      if (admin.value) {
        router.push('/admin-dashboard')
      } else {
        throw new Error('登录成功但无法获取管理员信息')
      }
    } catch (error) {
      console.error('管理员登录失败', error)
      token.value = null
      admin.value = null
      throw error
    }
  }

  const logout = (redirect = true) => {
    token.value = null
    admin.value = null
    if (redirect) {
      router.push('/admin-login')
    }
  }

  const init = async () => {
    await fetchAdmin()
  }

  return {
    token,
    admin,
    api: apiFetch,
    apiFetch,
    login,
    logout,
    fetchAdmin,
    init,
  }
}
