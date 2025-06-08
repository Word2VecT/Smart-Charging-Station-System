import { useAdminAuth } from './useAdminAuth'
import { useState } from '#app'

interface AdminOrder {
  order_id: number
  user_id: number
  actual_charge_amount: number
  total_fee: number
  created_at: string
}

export const useAdminOrders = () => {
  const { api } = useAdminAuth()
  const orders = useState<AdminOrder[]>('admin_orders', () => [])

  const fetchOrders = async () => {
    try {
      const data = await api('/admin/orders')
      orders.value = data
    } catch (error) {
      console.error('获取订单失败', error)
      orders.value = []
    }
  }

  return { orders, fetchOrders }
}
