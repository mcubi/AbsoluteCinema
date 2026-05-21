// 1. FUNCIÓN OFICIAL DE DJANGO PARA LEER EL TOKEN DE SEGURIDAD
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 2. NUESTRA FUNCIÓN DE AÑADIR A LA LISTA
function addToList(button, movieId, movieTitle) {
    const icon = button.querySelector('i');
    var isInList = button.classList.contains('added');
    
    // Evitamos doble clic accidental
    button.style.pointerEvents = 'none';

    // Cogemos el token de seguridad de las cookies
    const csrftoken = getCookie('csrftoken');

    // LLAMADA REAL AL BACKEND
    fetch('/api/toggle-lista/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'movie_id': movieId,
            'movie_title': movieTitle
        })
    })
    .then(response => {
        // Si la respuesta es HTML en vez de JSON, es que se nos caducó la sesión
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json();
        } else {
            throw new Error('No estás logueado');
        }
    })
    .then(data => {
        // Si el backend da error
        if (data.error) throw new Error(data.error);

        // LA ANIMACIÓN VISUAL SÓLO OCURRE SI TODO FUE BIEN
        // Ajustamos la animación dependiendo de qué tipo de botón es (el de "Populares Ahora" es diferente)
        const isListStyle = !button.classList.contains('watchlist-btn');

        if (data.status === 'added') {
            icon.style.transform = 'scale(0) rotate(90deg)';
            setTimeout(() => {
                icon.classList.remove('fa-plus');
                icon.classList.add('fa-check');
                button.classList.add('added');
                
                if(isListStyle) {
                    button.classList.add('!bg-ac-primary', '!text-white', '!border-ac-primary');
                    button.classList.remove('hover:bg-white', 'hover:text-black', 'bg-white/20');
                } else {
                    button.classList.add('!text-ac-primary', 'text-gray-900', 'dark:text-white');
                    button.classList.remove('text-gray-500', 'dark:text-gray-400', 'hover:text-ac-primary');
                }
                
                icon.style.transform = 'scale(1) rotate(0deg)';
                button.style.pointerEvents = 'auto';
            }, 150);
        } else if (data.status === 'removed') {
            icon.style.transform = 'scale(0) rotate(-90deg)';
            setTimeout(() => {
                icon.classList.remove('fa-check');
                icon.classList.add('fa-plus');
                button.classList.remove('added');
                
                if(isListStyle) {
                    button.classList.remove('!bg-ac-primary', '!text-white', '!border-ac-primary');
                    button.classList.add('hover:bg-white', 'hover:text-black', 'bg-white/20');
                } else {
                    button.classList.remove('!text-ac-primary', 'text-gray-900', 'dark:text-white');
                    button.classList.add('text-gray-500', 'dark:text-gray-400', 'hover:text-ac-primary');
                }
                
                icon.style.transform = 'scale(1) rotate(0deg)';
                button.style.pointerEvents = 'auto';
            }, 150);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.style.pointerEvents = 'auto'; // Reactivamos el botón
        alert("Parece que tu sesión expiró o no estás logueado. Prueba a iniciar sesión de nuevo.");
    });
}