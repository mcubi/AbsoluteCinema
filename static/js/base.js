// *************************************************
// Lógica Global para "Mi Lista" (Añadir/Quitar)

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

window.addToList = function (button, movieId, movieTitle) {
    const icon = button.querySelector("i");
    button.style.pointerEvents = "none";
    const csrftoken = getCookie("csrftoken");

    fetch("/api/toggle-lista/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ movie_id: movieId, movie_title: movieTitle }),
    })
    .then((response) => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1)
            return response.json();
        throw new Error("No logueado");
    })
    .then((data) => {
        if (data.error) throw new Error(data.error);

        icon.style.transform = "scale(0) rotate(90deg)";

        setTimeout(() => {
            const isAdded = data.status === "added";

            // 1. Cambiar icono
            icon.classList.replace(
                isAdded ? "fa-plus" : "fa-check",
                isAdded ? "fa-check" : "fa-plus",
            );

            // 2. Lógica de estilos (Detectamos qué tipo de botón es)
            if (button.classList.contains("watchlist-btn")) {
                // Estilo para la lista de Populares del Index
                button.classList.toggle("text-ac-primary", isAdded);
                button.classList.toggle("text-gray-500", !isAdded);
            } else if (button.classList.contains("w-[52px]")) {
                // Estilo para el botón grande de Detalle.html
                button.classList.toggle("!bg-ac-primary", isAdded);
                button.classList.toggle("!text-white", isAdded);
                button.classList.toggle("!border-ac-primary", isAdded);
            } else {
                // Estilo para los botones flotantes de los Catálogos
                button.classList.toggle("bg-ac-primary", isAdded);
                button.classList.toggle("border-ac-primary", isAdded);
                button.classList.toggle("bg-black/50", !isAdded);
                button.classList.toggle("border-white/20", !isAdded);
            }

            icon.style.transform = "scale(1) rotate(0deg)";
            button.style.pointerEvents = "auto";
            button.title = isAdded ? "Quitar de mi lista" : "Añadir a mi lista";
        }, 150);
    })
    .catch((error) => {
        button.style.pointerEvents = "auto";
        alert("Inicia sesión para guardar en tu lista.");
    });
};

// *************************************************
// Lógica del Menú Móvil

document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.getElementById("mobile-menu-button");
    const closeButton = document.getElementById("close-menu-button");
    const menuPanel = document.getElementById("mobile-menu-panel");
    const menuLinks = document.querySelectorAll(".mobile-menu-link");

    function openMenu() {
        if (menuPanel) {
            menuPanel.classList.remove("translate-x-full");
            menuPanel.classList.add("translate-x-0");
            document.body.classList.add("menu-open");
        }
    }

    function closeMenu() {
        if (menuPanel) {
            menuPanel.classList.remove("translate-x-0");
            menuPanel.classList.add("translate-x-full");
            document.body.classList.remove("menu-open");
        }
    }

    if (menuButton && closeButton && menuPanel) {
        menuButton.addEventListener("click", (e) => {
            e.stopPropagation();
            openMenu();
        });

        closeButton.addEventListener("click", (e) => {
            e.stopPropagation();
            closeMenu();
        });

        menuLinks.forEach(link => {
            link.addEventListener("click", () => {
                closeMenu();
            });
        });

        menuPanel.addEventListener("click", (e) => {
            if (e.target === menuPanel) {
                closeMenu();
            }
        });

        const menuContent = menuPanel.querySelector('.flex.flex-col.items-center');
        if (menuContent) {
            menuContent.addEventListener("click", (e) => {
                e.stopPropagation();
            });
        }
    }

    // *************************************************
    // Menú de perfil con click
    
    const avatarBtn = document.getElementById('profile-avatar-btn');
    const profileDropdown = document.getElementById('profile-dropdown');
    
    if (avatarBtn && profileDropdown) {
        avatarBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isVisible = !profileDropdown.classList.contains('hidden');
            if (!isVisible) {
                profileDropdown.classList.remove('hidden');
            } else {
                profileDropdown.classList.add('hidden');
            }
        });
        
        document.addEventListener('click', (e) => {
            if (!avatarBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
                profileDropdown.classList.add('hidden');
            }
        });
    }
});

// *************************************************
// Recargar al volver atrás

(function() {
    let isRefreshing = false;
    window.addEventListener('pageshow', function(event) {
        if (event.persisted && !isRefreshing) {
            isRefreshing = true;
            window.location.reload();
        }
    });
    let lastUrl = window.location.href;
    window.addEventListener('popstate', function() {
        if (!isRefreshing && window.location.href === lastUrl) {
            isRefreshing = true;
            window.location.reload();
        }
        lastUrl = window.location.href;
    });
})();

// *************************************************
// Función toggleTheme (para cambiar entre modo claro/oscuro)

window.toggleTheme = function () {
    if (document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
    } else {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
    }
};