/* ══════════════════════════════════════════════════════════
   api.js — helpers globaux COFINANCE CI
   ══════════════════════════════════════════════════════════ */

// ── Token helpers ─────────────────────────────────────────
function getAccess()  { return localStorage.getItem('access');  }
function getRefresh() { return localStorage.getItem('refresh'); }
function getUser()    { 
  try { return JSON.parse(localStorage.getItem('user')); }
  catch { return null; }
}

function isLoggedIn() { return !!getAccess(); }

function logout() {
  const refresh = getRefresh();
  if (refresh) {
    fetch('/api/auth/logout/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ refresh })
    }).catch(() => {});
  }
  localStorage.clear();
  window.location.href = '/login/';
}

function authHeader() {
  return { 'Authorization': 'Bearer ' + getAccess() };
}

// ── Requête API avec refresh automatique ─────────────────
async function apiFetch(url, options = {}) {
  options.headers = {
    'Content-Type': 'application/json',
    ...authHeader(),
    ...(options.headers || {})
  };

  let res = await fetch(url, options);

  // Token expiré → tenter le refresh
  if (res.status === 401) {
    const refreshed = await tryRefresh();
    if (!refreshed) { logout(); return null; }
    options.headers['Authorization'] = 'Bearer ' + getAccess();
    res = await fetch(url, options);
  }

  return res;
}

async function tryRefresh() {
  const refresh = getRefresh();
  if (!refresh) return false;
  try {
    const res  = await fetch('/api/auth/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('access', data.access);
    if (data.refresh) localStorage.setItem('refresh', data.refresh);
    return true;
  } catch { return false; }
}

// ── Flash messages ────────────────────────────────────────
function flash(msg, type = 'info') {
  const el = document.getElementById('flash');
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
  setTimeout(() => { el.innerHTML = ''; }, 4000);
}

// ── Formatage ─────────────────────────────────────────────
function fmtMoney(n) {
  return Number(n).toLocaleString('fr-FR') + ' FCFA';
}

function fmtDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('fr-FR');
}

function fmtDatetime(d) {
  if (!d) return '—';
  return new Date(d).toLocaleString('fr-FR');
}

function badge(status) {
  return `<span class="badge status-${status}">${status.replace('_', ' ')}</span>`;
}

// ── Navbar dynamique selon le rôle ────────────────────────
(function buildNav() {
  const user = getUser();
  const nav  = document.getElementById('nav-links');
  if (!nav) return;

  // Pages publiques : rien à afficher
  const publicPages = ['/login/', '/register/', '/'];
  if (publicPages.includes(window.location.pathname)) return;

  // Pas connecté → renvoi login
  if (!isLoggedIn()) { window.location.href = '/login/'; return; }

  const role = user?.role;

  const links = {
    CLIENT: [
      ['/', 'Accueil'],
      ['/client-dashboard/', 'Tableau de bord'],
      ['/client/credits/', 'Mes crédits'],
      ['/client/insurance/', 'Assurance'],
      ['/client/chat/', 'Support'],
      ['/client/notifications/', 'Notifs'],
      ['/client/profile/', 'Profil'],
    ],
    AGENT: [
      ['/agent-dashboard/', 'Tableau de bord'],
      ['/agent/credits/', 'Dossiers'],
      ['/agent/payments/', 'Paiements'],
      ['/agent/conversations/', 'Support'],
    ],
    ADMIN: [
      ['/admin-dashboard/', 'Tableau de bord'],
      ['/admin/credits/', 'Crédits'],
      ['/admin/users/', 'Utilisateurs'],
      ['/admin/insurance/', 'Assurance'],
      ['/admin/reports/', 'Rapports'],
    ],
  };

  const roleLinks = links[role] || [];
  nav.innerHTML = roleLinks
    .map(([href, label]) => `<a href="${href}">${label}</a>`)
    .join('');

  // Bouton déconnexion + nom user
  nav.innerHTML += `
    <span class="nav-user">${user?.username || ''} (${role})</span>
    <button class="btn btn-sm btn-danger" onclick="logout()">Déconnexion</button>
  `;
})();