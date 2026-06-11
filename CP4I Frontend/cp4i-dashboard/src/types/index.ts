export type UserRole = 'requestor' | 'approver' | 'operations' | 'management' | 'admin'

export interface User {
  name: string
  username: string
  role: UserRole
}