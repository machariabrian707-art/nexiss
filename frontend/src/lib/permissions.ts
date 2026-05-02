import type { AuthUser } from '@/stores/authStore'

export function isSuperadmin(user: AuthUser | null): boolean {
  return Boolean(user?.is_superuser)
}

export function isOrgAdmin(user: AuthUser | null): boolean {
  if (!user) return false
  if (user.is_superuser) return true
  return user.active_org_role === 'owner' || user.active_org_role === 'admin'
}

export function canProcessDocuments(user: AuthUser | null): boolean {
  if (!user) return false
  if (user.is_superuser) return true
  return Boolean(user.can_process_documents)
}
