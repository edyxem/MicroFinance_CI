async function doRegister() {
  const payload = {
    username: document.getElementById('username').value.trim(),
    email: document.getElementById('email').value.trim(),
    phone: document.getElementById('phone').value.trim(),
    region: document.getElementById('region').value,
    password: document.getElementById('password').value,
  };

  try {
    await API.post('/api/auth/register/', payload);

    document.getElementById('msg').innerHTML =
      `<div class="alert alert-success">
        Compte créé ! <a href="/login/">Se connecter</a>
      </div>`;

  } catch (e) {
    const err = Object.values(e).flat().join(' ');

    document.getElementById('msg').innerHTML =
      `<div class="alert alert-error">${err}</div>`;
  }
}