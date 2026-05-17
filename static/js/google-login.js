/* Google One Tap "botón" wrapper para la página de login (Django template).
   Requiere:
   - @react-oauth/google NO; aquí usamos el script de Google Identity Services.
   - En el botón se obtiene un token (credential) y se envía a Django endpoint:
       POST /users/api/auth/google/
*/

(function () {
  function postCredential(credential) {
    return fetch('/users/api/google-auth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ credential }),
    });
  }

  function initButton({ clientId, buttonId = 'google-login-button' }) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;

    if (!window.google || !window.google.accounts || !window.google.accounts.id) {
      console.error('Google Identity Services no cargado.');
      alert('Google Identity Services no cargó. Revisa consola / carga del script.');
      return;
    }

    if (!window.__ac_google_initialized) {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: function (response) {
          const credential = response.credential;
          if (!credential) {
            console.error('No credential recibido');
            alert('No se recibió credential de Google.');
            return;
          }

          postCredential(credential)
            .then(async (res) => {
              const data = await res.json().catch(() => ({}));
              if (!res.ok) {
                console.error('Google login API error:', data);
                throw new Error(data.error || 'Backend error');
              }
              if (data.status === 'success') {
                // Redirect a la home real
                window.location.href = '/';
              } else {
                console.error('Google login no success:', data);
                alert(data.error || 'Error al iniciar sesión.');
              }
            })
            .catch((err) => {
              console.error('Google login backend error:', err);
              alert(err.message || 'Error al iniciar sesión con Google');
            });
        },
      });
      window.__ac_google_initialized = true;
    }

    // IMPORTANTE: prompt() muestra selector
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      try {
        window.google.accounts.id.prompt();
      } catch (err) {
        console.error('Error en prompt() de Google:', err);
        alert('No se pudo abrir el selector de Google.');
      }
    });
  }

  function redirectHome() {
    // Redirigir explícitamente a la home (según tu template base usa `{% url 'home' %}`)
    // La "home" real está en el proyecto como la ruta name='home' => '/'
    // (en caso de que luego cambie, aquí puedes ajustar)
    window.location.href = '/';

  }

  // Alias por si quieres cambiar el destino en el futuro
  function redirectAfterLogin() {
    redirectHome();
  }


  window.renderGoogleLoginButton = function renderGoogleLoginButton(options) {
    const {
      clientId,
      buttonId = 'google-login-button',
      tokenCallback,
    } = options || {};

    const btn = document.getElementById(buttonId);
    if (!btn) return;

    // Cargar GIS global si existe
    if (!window.google || !window.google.accounts || !window.google.accounts.id) {
      console.error('Google Identity Services no cargado.');
      return;
    }

    // Solicitar token cuando el usuario pulse el botón
    btn.addEventListener('click', function (e) {
      e.preventDefault();

      // Capturamos el credential vía callback de GIS
      // Nota: renderButton/initializeOneTap usan One Tap automático.
      // Para "botón manual", usamos prompt() tras inicializar.
      // En la práctica, prompt() mostrará el selector de Google.

      // Inicializar una vez (si no existe)
      if (!window.__ac_google_initialized) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: function (response) {
            const credential = response.credential;
            if (!credential) {
              console.error('No credential recibido');
              return;
            }
            postCredential(credential)
              .then(async (res) => {
                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                  throw new Error(data.error || 'Backend error');
                }
                if (data.status === 'success') {
                  redirectHome();
                } else {
                  if (tokenCallback) tokenCallback(data);
                }
              })
              .catch((err) => {
                console.error('Google login backend error:', err);
                alert(err.message || 'Error al iniciar sesión con Google');
              });
          },
        });
        window.__ac_google_initialized = true;
      }

      // Mostrar selector de Google
      window.google.accounts.id.prompt();
    });
  };
})();

