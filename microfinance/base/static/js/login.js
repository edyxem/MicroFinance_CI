async function doLogin() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  try {
    const data = await API.post('/api/auth/login/', {
      username,
      password
    });

    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    localStorage.setItem('role', data.user.role);
    localStorage.setItem('user', JSON.stringify(data.user));

    const redirects = {
      ADMIN: '/admin-dashboard/',
      AGENT: '/agent-dashboard/',
      CLIENT: '/client-dashboard/'
    };

    window.location.href = redirects[data.user.role] || '/';

  } catch (e) {
    document.getElementById('msg').innerHTML =
      `<div class="alert alert-error">${e.error || 'Identifiants incorrects'}</div>`;
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') doLogin();
});