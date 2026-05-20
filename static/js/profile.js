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

// delete review
function deleteReview(reviewId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta reseña? Esta acción no se puede deshacer.')) {
        return;
    }

    fetch(`/api/reviews/delete/${reviewId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.error || 'Error al eliminar la reseña');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al eliminar la reseña');
    });
}

// to show/hide reviews
function initReviewsToggle() {
    const showMoreBtn = document.getElementById('show-more-btn');
    const showLessBtn = document.getElementById('show-less-btn');
    const moreReviews = document.getElementById('more-reviews');
    
    if (showMoreBtn && showLessBtn && moreReviews) {
        showMoreBtn.addEventListener('click', function() {
            moreReviews.classList.remove('hidden');
            showMoreBtn.classList.add('hidden');
            showLessBtn.classList.remove('hidden');
        });
        
        showLessBtn.addEventListener('click', function() {
            moreReviews.classList.add('hidden');
            showMoreBtn.classList.remove('hidden');
            showLessBtn.classList.add('hidden');
            
            // smooth scroll
            showMoreBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initReviewsToggle();
});