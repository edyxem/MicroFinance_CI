document.addEventListener('DOMContentLoaded', function () {
  const user = API.user;
  const navLinks = document.getElementById('navLinks');
  const navUser  = document.getElementById('navUser');

  if (!navLinks) return;

  if (!user || !API.token) {
    navLinks.innerHTML = `
      <a href="/login/">Connexion</a>
      <a href="/register/">Inscription</a>`;
    return;
  }

  if (navUser) navUser.textContent = user.username;

  const MENUS = {
    CLIENT: [
      { href: '/client-dashboard/', label: 'Accueil' },
      { href: '/credits/',          label: 'Mes crédits' },
      { href: '/insurance/',        label: 'Assurance' },
      { href: '/chat/',             label: 'Support' },
      { href: '/notifications/',    label: '🔔', id: 'navNotif' },
    ],
    AGENT: [
      { href: '/agent-dashboard/', label: 'Accueil' },
      { href: '/credits/',         label: 'Dossiers' },
      { href: '/chat/',            label: 'Support' },
      { href: '/notifications/',   label: '🔔', id: 'navNotif' },
    ],
    ADMIN: [
      { href: '/admin-dashboard/', label: 'Dashboard' },
      { href: '/credits/',         label: 'Crédits' },
      { href: '/insurance/',       label: 'Assurance' },
      { href: '/chat/',            label: 'Support' },
      { href: '/api/docs/',        label: 'API Docs', target: '_blank' },
    ],
  };

  const items = MENUS[user.role] || [];
  navLinks.innerHTML = items.map(item => {
    const target = item.target ? `target="${item.target}"` : '';
    const id     = item.id ? `id="${item.id}"` : '';
    return `<a href="${item.href}" ${target} ${id}>${item.label}</a>`;
  }).join('') +
  `<span class="nav-user" id="navUser">${user.username} (${user.role})</span>
   <a href="/logout/" style="color:#ff8a80;">Déco</a>`;

  if (API.token) {
    API.get('/api/notifications/unread-count/')
      .then(d => {
        const el = document.getElementById('navNotif');
        if (el && d.unread_count > 0) {
          el.innerHTML += `<span class="badge-notif">${d.unread_count}</span>`;
        }
      })
      .catch(() => {});
  }
});