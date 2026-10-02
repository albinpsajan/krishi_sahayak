/** Role helpers shared across the app (developer-friendly naming). */

export function isFarmerRole(user) {
  return user?.role === 'FARMER';
}

export function isOfficerRole(user) {
  return user?.role === 'OFFICER';
}

export function homeTabForRole(role) {
  return role === 'OFFICER' ? 'dashboard' : 'home';
}
