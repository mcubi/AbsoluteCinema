console.log("Cargando reseñas WebSocket - v", window.movieId, new Date().getTime());

let socket = null;
let currentRating = 0;
let movieId = window.movieId;
let movieTitle = window.movieTitle;
let pollingInterval = null;
let initialReviewsLoaded = false;
let currentUsername = window.currentUsername || '';

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/reviews/${movieId}/`;
    
    try {
        socket = new WebSocket(wsUrl);
        socket.onopen = function (e) {
            document.getElementById("connection-status").innerHTML = '<i class="fas fa-check-circle text-green-500"></i> Conectado (WebSocket)';
            const reviewsList = document.getElementById("reviews-list");
            if (reviewsList.children.length === 0 || reviewsList.querySelector(".fa-comment-slash")) {
                socket.send(JSON.stringify({ action: "get_reviews" }));
            }
        };

        socket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            handleWebSocketMessage(data);
        };

        socket.onclose = function (e) {
            document.getElementById("connection-status").innerHTML = '<i class="fas fa-exclamation-triangle text-yellow-500"></i> WebSocket no disponible. Usando polling...';
            startPolling();
        };

        socket.onerror = function (e) {
            document.getElementById("connection-status").innerHTML = '<i class="fas fa-exclamation-triangle text-yellow-500"></i> WebSocket no disponible. Usando polling...';
            startPolling();
        };
    } catch (error) {
        startPolling();
    }
}

function startPolling() {
    if (pollingInterval) return;
    document.getElementById("connection-status").innerHTML = '<i class="fas fa-sync text-blue-500"></i> Actualizando automáticamente (Polling)';
    fetch(`/api/reviews/${movieId}/`)
        .then((response) => response.json())
        .then((data) => {
            if (data.reviews) { displayReviews(data.reviews); }
        });
    pollingInterval = setInterval(loadReviewsViaAJAX, 5000);
}

function loadReviewsViaAJAX() {
    fetch(`/api/reviews/${movieId}/`)
        .then((response) => response.json())
        .then((data) => {
            if (data.reviews) {
                const reviewsList = document.getElementById("reviews-list");
                const existingReviewIds = Array.from(reviewsList.querySelectorAll("[data-review-id]")).map((el) => el.getAttribute("data-review-id"));
                const newReviews = data.reviews.filter((review) => !existingReviewIds.includes(review.id.toString()));
                if (newReviews.length > 0) {
                    newReviews.forEach((review) => addReviewToList(review));
                }
                updateReviewCount(reviewsList.querySelectorAll("[data-review-id]").length);
            }
        });
}

function handleWebSocketMessage(data) {
    if (data.action === "reviews_list") {
        displayReviews(data.reviews);
    } else if (data.action === "new_review") {
        addReviewToList(data.review);
    } else if (data.error) {
        alert(data.error);
    }
}

function displayReviews(reviews) {
    const reviewsList = document.getElementById("reviews-list");
    if (reviewsList.children.length === 0 || reviewsList.querySelector(".fa-comment-slash")) {
        reviewsList.innerHTML = "";
        if (reviews.length === 0) {
            reviewsList.innerHTML = `
                <div class="text-center py-16 bg-gray-100 dark:bg-[#1a1a1a] rounded-xl border border-gray-200 dark:border-white/5">
                    <i class="fas fa-comment-slash text-5xl text-gray-400 dark:text-gray-600 mb-4"></i>
                    <p class="text-gray-500 dark:text-gray-400">No hay reseñas todavía</p>
                </div>
            `;
        } else {
            reviews.forEach((review) => addReviewToList(review));
        }
    } else {
        const existingReviewIds = Array.from(reviewsList.querySelectorAll("[data-review-id]")).map((el) => el.getAttribute("data-review-id"));
        const newReviews = reviews.filter((review) => !existingReviewIds.includes(review.id.toString()));
        newReviews.forEach((review) => addReviewToList(review));
    }
    updateReviewCount(reviewsList.querySelectorAll("[data-review-id]").length);
}

// avatar
function getAvatarHtml(avatarUrl, username, size = 12) {
    const sizeClass = size === 12 ? 'w-12 h-12' : 'w-8 h-8';
    const iconSize = size === 12 ? 'text-lg' : 'text-sm';
    const fallbackIcon = `<div class='${sizeClass} rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center'><i class='fas fa-user text-gray-500 dark:text-gray-400 ${iconSize}'></i></div>`;

    // si es null, vacío o None
    if (!avatarUrl || avatarUrl === 'null' || avatarUrl === '' || avatarUrl === 'None') {
        console.log("→ Usando fallback (sin avatar)");
        return fallbackIcon;
    }

    // construir url completa
    let finalUrl = avatarUrl;
    
    // si la url empieza con /media/, usarla directamente
    if (avatarUrl.startsWith('/media/')) {
        finalUrl = avatarUrl;
    }
    // si la url no empieza con http, añadir la base
    else if (!avatarUrl.startsWith('http')) {
        finalUrl = window.location.origin + '/media/' + avatarUrl.split('/').pop();
    }
    
    console.log("Avatar URL final:", finalUrl);

    return `<img src="${finalUrl}" alt="${escapeHtml(username)}" class="${sizeClass} rounded-full object-cover" onerror="console.error('Error cargando avatar:', this.src); this.outerHTML = \`${fallbackIcon}\`;">`;
}
// ------------------------------------------

function addReviewToList(review) {
    const reviewsList = document.getElementById("reviews-list");
    if (reviewsList.querySelector(".fa-comment-slash")) {
        reviewsList.innerHTML = "";
    }
    const existingReview = reviewsList.querySelector(`[data-review-id="${review.id}"]`);
    if (existingReview) return;

    if (review.parent_id) {
        const parentReview = reviewsList.querySelector(`[data-review-id="${review.parent_id}"]`);
        if (parentReview) {
            const repliesContainer = parentReview.querySelector(`[data-replies-container="${review.parent_id}"]`);
            if (repliesContainer) {
                addReplyToContainer(repliesContainer, review);
                updateReplyCount(review.parent_id);
                return;
            }
        }
    }

    const isOwnReview = review.user === currentUsername;
    const deleteButton = isOwnReview ? `
        <button onclick="deleteReview(${review.id})" class="text-red-500 hover:text-red-700 text-sm font-medium transition flex items-center gap-1">
            <i class="fas fa-trash"></i> Eliminar
        </button>
    ` : '';

    const replyButton = window.isUserAuthenticated ? `<button onclick="toggleReplyForm(${review.id})" class="text-ac-primary hover:text-ac-primary-dark text-sm font-medium transition flex items-center gap-1"><i class="fas fa-reply"></i> Responder</button>` : '';

    const avatarHtml = getAvatarHtml(review.avatar, review.user, 12);

    const reviewElement = document.createElement("div");
    reviewElement.className = "bg-gray-50 dark:bg-[#1a1a1a] rounded-xl p-6 border border-gray-200 dark:border-white/5";
    reviewElement.setAttribute("data-review-id", review.id);
    reviewElement.innerHTML = `
        <div class="flex items-start gap-4">
            ${avatarHtml}
            <div class="flex-1">
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-bold text-gray-900 dark:text-white">${escapeHtml(review.user)}</h4>
                    <div class="flex items-center gap-3">
                        <span class="text-sm text-gray-500">${review.created_at}</span>
                        ${deleteButton}
                    </div>
                </div>
                <div class="flex items-center gap-2 mb-3">
                    ${generateStars(review.rating)}
                    <span class="text-sm text-gray-500">(${review.rating}/5)</span>
                </div>
                <p class="text-gray-700 dark:text-gray-300">${escapeHtml(review.content)}</p>
                <div class="flex items-center gap-4 mt-3">
                    ${replyButton}
                    <span class="text-sm text-gray-500">${review.reply_count || 0} respuestas</span>
                </div>
            </div>
        </div>
        <div id="reply-form-${review.id}" class="hidden mt-4 ml-16 bg-white dark:bg-[#2a2a2a] rounded-lg p-4 border border-gray-200 dark:border-white/5">
            <form onsubmit="submitReply(event, ${review.id})" class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tu respuesta</label>
                    <textarea id="reply-content-${review.id}" rows="3" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-ac-primary focus:border-transparent dark:bg-[#1a1a1a] dark:text-white" placeholder="Escribe tu respuesta..." required></textarea>
                </div>
                <div class="flex gap-2">
                    <button type="submit" class="bg-ac-primary hover:bg-ac-primary-dark text-white px-4 py-2 rounded-lg text-sm font-bold transition">
                        <i class="fas fa-paper-plane"></i> Enviar Respuesta
                    </button>
                    <button type="button" onclick="toggleReplyForm(${review.id})" class="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg text-sm font-bold transition">
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
        <div data-replies-container="${review.id}" class="mt-4 ml-16 space-y-3"></div>
    `;
    reviewsList.insertBefore(reviewElement, reviewsList.firstChild);
    updateReviewCount(reviewsList.children.length);

    if (review.replies && review.replies.length > 0) {
        const repliesContainer = reviewElement.querySelector(`[data-replies-container="${review.id}"]`);
        review.replies.forEach(reply => addReplyToContainer(repliesContainer, reply));
    }
}

function addReplyToContainer(container, reply) {
    const existingReply = container.querySelector(`[data-reply-id="${reply.id}"]`);
    if (existingReply) return;

    const isOwnReply = reply.user === currentUsername;
    const deleteButton = isOwnReply ? `
        <button onclick="deleteReview(${reply.id})" class="text-red-500 hover:text-red-700 text-xs font-medium transition flex items-center gap-1">
            <i class="fas fa-trash"></i>
        </button>
    ` : '';

    const replyAvatarHtml = getAvatarHtml(reply.avatar, reply.user, 8);

    const replyElement = document.createElement("div");
    replyElement.className = "bg-white dark:bg-[#2a2a2a] rounded-lg p-4 border border-gray-200 dark:border-white/5";
    replyElement.setAttribute("data-reply-id", reply.id);
    replyElement.innerHTML = `
        <div class="flex items-start gap-3">
            ${replyAvatarHtml}
            <div class="flex-1">
                <div class="flex items-center justify-between mb-1">
                    <h5 class="font-semibold text-gray-900 dark:text-white text-sm">${escapeHtml(reply.user)}</h5>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-500">${reply.created_at}</span>
                        ${deleteButton}
                    </div>
                </div>
                <p class="text-gray-700 dark:text-gray-300 text-sm">${escapeHtml(reply.content)}</p>
            </div>
        </div>
    `;
    container.appendChild(replyElement);
}

function toggleReplyForm(reviewId) {
    const form = document.getElementById(`reply-form-${reviewId}`);
    form.classList.toggle("hidden");
}

function submitReply(event, parentReviewId) {
    event.preventDefault();
    const content = document.getElementById(`reply-content-${parentReviewId}`).value.trim();
    if (!content) { alert("Por favor, escribe una respuesta"); return; }

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ action: "add_review", rating: 5, content: content, movie_title: movieTitle, parent_id: parentReviewId }));
        document.getElementById(`reply-content-${parentReviewId}`).value = "";
        toggleReplyForm(parentReviewId);
    } else {
        sendReplyViaAPI(parentReviewId, content);
    }
}

function sendReplyViaAPI(parentReviewId, content) {
    fetch(`/api/reviews/${movieId}/add/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify({ rating: 5, content: content, movie_title: movieTitle, parent_id: parentReviewId }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                const parentReview = document.querySelector(`[data-review-id="${parentReviewId}"]`);
                if (parentReview) {
                    const repliesContainer = parentReview.querySelector(`[data-replies-container="${parentReviewId}"]`);
                    if (repliesContainer) {
                        addReplyToContainer(repliesContainer, data.review);
                        updateReplyCount(parentReviewId);
                    }
                }
                document.getElementById(`reply-content-${parentReviewId}`).value = "";
                toggleReplyForm(parentReviewId);
            } else {
                alert(data.error || "Error al enviar la respuesta");
            }
        });
}

function updateReplyCount(parentReviewId) {
    const parentReview = document.querySelector(`[data-review-id="${parentReviewId}"]`);
    if (parentReview) {
        const repliesContainer = parentReview.querySelector(`[data-replies-container="${parentReviewId}"]`);
        const countSpan = parentReview.querySelector('.text-sm.text-gray-500');
        if (repliesContainer && countSpan) {
            const replyCount = repliesContainer.children.length;
            countSpan.textContent = `${replyCount} respuesta${replyCount !== 1 ? "s" : ""}`;
        }
    }
}

function generateStars(rating) {
    let stars = "";
    for (let i = 1; i <= 5; i++) {
        if (i <= rating) {
            stars += '<i class="fas fa-star text-yellow-500"></i>';
        } else {
            stars += '<i class="far fa-star text-gray-300"></i>';
        }
    }
    return stars;
}

function updateReviewCount(count) {
    document.getElementById("review-count").textContent = `${count} reseña${count !== 1 ? "s" : ""}`;
}

function toggleReviewForm() {
    document.getElementById("review-form").classList.toggle("hidden");
}

function setRating(rating) {
    currentRating = rating;
    document.getElementById("rating").value = rating;
    const stars = document.querySelectorAll(".star-btn i");
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.remove("far", "text-gray-300");
            star.classList.add("fas", "text-yellow-500");
        } else {
            star.classList.remove("fas", "text-yellow-500");
            star.classList.add("far", "text-gray-300");
        }
    });
}

function sendReviewViaAPI() {
    const content = document.getElementById("content").value.trim();
    fetch(`/api/reviews/${movieId}/add/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify({ rating: currentRating, content: content, movie_title: movieTitle }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                addReviewToList(data.review);
                document.getElementById("content").value = "";
                setRating(0);
                toggleReviewForm();
                updateReviewCount(document.getElementById("reviews-list").children.length);
            } else {
                alert(data.error || "Error al enviar la reseña");
            }
        });
}

function redirectToRegister() {
    if (confirm("Para escribir una reseña necesitas estar registrado. ¿Te gustaría registrarte ahora?")) {
        window.location.href = "/users/register";
    }
}

function deleteReview(reviewId) {
    if (!confirm("¿Estás seguro de que quieres eliminar esta reseña?")) {
        return;
    }

    fetch(`/api/reviews/delete/${reviewId}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                const replyElement = document.querySelector(`[data-reply-id="${reviewId}"]`);
                const reviewElement = document.querySelector(`[data-review-id="${reviewId}"]`);

                if (replyElement) {
                    const parentContainer = replyElement.closest('[data-replies-container]');
                    if (parentContainer) {
                        const parentReviewId = parentContainer.getAttribute('data-replies-container');
                        replyElement.remove();
                        updateReplyCount(parentReviewId);
                    }
                } else if (reviewElement) {
                    reviewElement.remove();
                    updateReviewCount(document.getElementById("reviews-list").children.length);
                }
            } else {
                alert(data.error || "Error al eliminar la reseña");
            }
        })
        .catch((error) => {
            console.error(error);
            alert("Error al eliminar la reseña");
        });
}

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

function toggleDetalleLista(button, movieId, movieTitle) {
    const icon = button.querySelector('i');
    
    button.style.pointerEvents = "none";
    if(icon) icon.style.transform = "scale(0) rotate(90deg)";

    fetch("/api/toggle-lista/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ movie_id: movieId, movie_title: movieTitle || '' }),
    })
    .then((response) => {
        if (!response.ok) throw new Error("Error en la conexión");
        return response.json();
    })
    .then((data) => {
        if (data.error) throw new Error(data.error);

        setTimeout(() => {
            const isAdded = data.status === "added";

            if (isAdded) {
                button.classList.remove("bg-gray-100", "dark:bg-[#181818]", "text-gray-900", "dark:text-white", "border-gray-200", "dark:border-white/10");
                button.classList.add("added", "bg-ac-primary", "text-white", "border-ac-primary");
                if(icon) {
                    icon.classList.remove("fa-plus");
                    icon.classList.add("fa-check");
                }
            } else {
                button.classList.remove("added", "bg-ac-primary", "text-white", "border-ac-primary");
                button.classList.add("bg-gray-100", "dark:bg-[#181818]", "text-gray-900", "dark:text-white", "border-gray-200", "dark:border-white/10");
                if(icon) {
                    icon.classList.remove("fa-check");
                    icon.classList.add("fa-plus");
                }
            }

            if(icon) icon.style.transform = "scale(1) rotate(0deg)";
            button.style.pointerEvents = "auto";
        }, 150);
    })
    .catch((error) => {
        button.style.pointerEvents = "auto";
        if(icon) icon.style.transform = "scale(1) rotate(0deg)";
        console.error(error);
        alert("Error al añadir a la lista. Inicia sesión o inténtalo de nuevo.");
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const reviewForm = document.getElementById("review-form-element");
    if (reviewForm) {
        reviewForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const content = document.getElementById("content").value.trim();
            if (currentRating === 0) { alert("Por favor, selecciona una puntuación"); return; }
            if (!content) { alert("Por favor, escribe una reseña"); return; }

            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ action: "add_review", rating: currentRating, content: content, movie_title: movieTitle }));
                document.getElementById("content").value = "";
                setRating(0);
                toggleReviewForm();
            } else {
                sendReviewViaAPI();
            }
        });
    }
    
    connectWebSocket();
});