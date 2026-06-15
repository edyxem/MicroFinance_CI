function flash(msg, type = 'info') {
  const el = document.getElementById('flash');
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
  setTimeout(() => { el.innerHTML = ''; }, 3500);
}

function statusBadge(s) {
  const labels = {
    SOUMISE:    'Soumise',
    EN_ANALYSE: 'En analyse',
    APPROUVEE:  'Approuvée',
    DECAISSEE:  'Décaissée',
    REFUSEE:    'Refusée',
    SOLDEE:     'Soldée',
    EN_ATTENTE: 'En attente',
    PAYEE:      'Payée',
    EN_RETARD:  'En retard',
    ACTIVE:     'Active',
    EXPIREE:    'Expirée',
    OUVERTE:    'Ouverte',
    EN_COURS:   'En cours',
    RESOLUE:    'Résolue',
  };
  const label = labels[s] || s;
  return `<span class="badge status-${s}">${label}</span>`;
}

function renderBarChart(containerId, data, labelKey, valueKey, color = '#1a6cff') {
  const el = document.getElementById(containerId);
  if (!el) return;
  const max = Math.max(...data.map(d => d[valueKey]), 1);
  el.className = 'bar-chart';
  el.innerHTML = data.map(d => {
    const h = Math.round((d[valueKey] / max) * 130) + 10;
    return `
      <div class="bar-wrap" title="${d[labelKey]} : ${d[valueKey]}">
        <div class="bar" style="height:${h}px; background:${color};"></div>
        <span class="bar-label">${String(d[labelKey]).slice(-5)}</span>
      </div>`;
  }).join('');
}

function fmtFCFA(amount) {
  return Number(amount).toLocaleString('fr-FR') + ' FCFA';
}

function fmtDate(str) {
  if (!str) return '—';
  return new Date(str).toLocaleDateString('fr-FR');
}

function fmtDateTime(str) {
  if (!str) return '—';
  return new Date(str).toLocaleString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}


function apiError(e) {
  if (typeof e === 'string') return e;
  if (e.error) return e.error;
  if (e.detail) return e.detail;
  return Object.values(e).flat().join(' ');
}

function requireAuth(roles = []) {
  const user = API.user;
  if (!user || !API.token) {
    window.location.href = '/login/';
    return null;
  }
  if (roles.length && !roles.includes(user.role)) {
    window.location.href = '/';
    return null;
  }
  return user;
}