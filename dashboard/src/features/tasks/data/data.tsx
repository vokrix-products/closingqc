import {CircleCheckBig, TriangleAlert, Clock} from 'lucide-react'

export const labels = [
  {
    value: 'bug',
    label: 'Bug',
  },
  {
    value: 'feature',
    label: 'Feature',
  },
  {
    value: 'documentation',
    label: 'Documentation',
  },
]

// Severity tiers drive badge color. Every status maps to exactly one tier:
//   critical -> red (destructive)   e.g. expired, denied, failed
//   warning  -> amber (warning)     e.g. expiring soon, needs review
//   good     -> green (success)     e.g. valid, approved, done
//   neutral  -> gray (secondary)    e.g. pending, queued, n/a
export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<Severity, 'destructive' | 'warning' | 'success' | 'secondary'> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// Closing Exception statuses. value must match exactly what the backend
// poller writes to records.status. Every status declares a severity tier.
// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof TriangleAlert
  severity: Severity
}[] = [
  { label: 'Valid', value: 'Valid', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Missing', value: 'Missing', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Unsigned', value: 'Unsigned', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Expired', value: 'Expired', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Flagged', value: 'Flagged', icon: Clock, severity: 'warning' as Severity },
  { label: 'Needs Review', value: 'Needs Review', icon: Clock, severity: 'warning' as Severity },
  { label: 'Mismatch', value: 'Mismatch', icon: Clock, severity: 'warning' as Severity },
  { label: 'Late', value: 'Late', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Notary Invalid', value: 'Notary Invalid', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Unreadable', value: 'Unreadable', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Duplicate', value: 'Duplicate', icon: Clock, severity: 'warning' as Severity },
  { label: 'Version Mismatch', value: 'Version Mismatch', icon: Clock, severity: 'warning' as Severity },
  { label: 'Cleared', value: 'Cleared', icon: CircleCheckBig, severity: 'good' as Severity },
]
// __STATUSES_BLOCK_END__
