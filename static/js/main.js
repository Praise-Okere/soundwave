document.addEventListener('DOMContentLoaded', () => {
    const genreCheckboxes = document.querySelectorAll('.genre-checkbox');
    const recommendBtn = document.getElementById('recommendBtn');
    const genreForm = document.getElementById('genreForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Hardcoded user ID for v1
    const userId = 'guest_user';
    
    // Global Audio Player state
    let currentAudio = null;
    let currentPlayBtn = null;

    // Enable/disable submit button based on selection
    genreCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const anyChecked = Array.from(genreCheckboxes).some(cb => cb.checked);
            recommendBtn.disabled = !anyChecked;
        });
    });

    genreForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const selectedGenres = Array.from(genreCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
            
        if (selectedGenres.length === 0) return;
        
        // UI State
        recommendBtn.disabled = true;
        loadingSpinner.classList.remove('d-none');
        resultsSection.classList.add('d-none');
        resultsContainer.innerHTML = '';
        
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    genres: selectedGenres
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                renderRecommendations(data.recommendations);
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            alert('Failed to get recommendations. Please try again.');
        } finally {
            recommendBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
        }
    });

    function renderRecommendations(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info">No recommendations found for the selected genres.</div>';
            resultsSection.classList.remove('d-none');
            return;
        }

        let html = '';
        recommendations.forEach((rec, index) => {
            // Convert score to percentage
            const scorePercent = (rec.hybrid_score * 100).toFixed(1);
            
            html += `
                <div class="card track-card shadow-sm mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h5 class="card-title mb-1 fw-bold">${rec.track_name}</h5>
                                <h6 class="card-subtitle text-muted mb-2">${rec.artists}</h6>
                                <span class="badge genre-badge mb-3">${rec.track_genre.toUpperCase()}</span>
                            </div>
                            <div>
                                <button class="btn btn-outline-success btn-sm rounded-circle play-preview-btn" data-url="${rec.preview_url || ''}" ${rec.preview_url ? '' : 'disabled'}>
                                    <i class="bi bi-play-fill"></i>
                                </button>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <div class="d-flex justify-content-between text-muted" style="font-size: 0.8rem;">
                                <span>Match Score</span>
                                <span>${scorePercent}%</span>
                            </div>
                            <div class="progress mt-1">
                                <div class="progress-bar bg-success" role="progressbar" style="width: ${scorePercent}%" aria-valuenow="${scorePercent}" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        </div>
                        
                        <div class="d-flex align-items-center justify-content-between pt-2 border-top">
                            <span class="text-muted" style="font-size: 0.85rem;">Rate this track:</span>
                            <div class="star-rating" data-track-id="${rec.track_id}">
                                <i class="bi bi-star-fill" data-rating="5"></i>
                                <i class="bi bi-star-fill" data-rating="4"></i>
                                <i class="bi bi-star-fill" data-rating="3"></i>
                                <i class="bi bi-star-fill" data-rating="2"></i>
                                <i class="bi bi-star-fill" data-rating="1"></i>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        resultsContainer.innerHTML = html;
        resultsSection.classList.remove('d-none');
        
        // Attach event listeners
        attachRatingListeners();
        attachPlaybackListeners();
    }
    
    function attachPlaybackListeners() {
        const playBtns = document.querySelectorAll('.play-preview-btn');
        
        playBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const url = btn.getAttribute('data-url');
                if (!url) return;
                
                const icon = btn.querySelector('i');
                
                // If this same song is already playing, pause it
                if (currentAudio && currentAudio.src === url && !currentAudio.paused) {
                    currentAudio.pause();
                    icon.classList.remove('bi-pause-fill');
                    icon.classList.add('bi-play-fill');
                    return;
                }
                
                // If another song is playing, stop it and reset its icon
                if (currentAudio) {
                    currentAudio.pause();
                    if (currentPlayBtn) {
                        const oldIcon = currentPlayBtn.querySelector('i');
                        oldIcon.classList.remove('bi-pause-fill');
                        oldIcon.classList.add('bi-play-fill');
                    }
                }
                
                // Play new song
                currentAudio = new Audio(url);
                currentPlayBtn = btn;
                
                currentAudio.play();
                icon.classList.remove('bi-play-fill');
                icon.classList.add('bi-pause-fill');
                
                // Reset icon when audio finishes
                currentAudio.addEventListener('ended', () => {
                    icon.classList.remove('bi-pause-fill');
                    icon.classList.add('bi-play-fill');
                    currentAudio = null;
                    currentPlayBtn = null;
                });
            });
        });
    }
    
    function attachRatingListeners() {
        const ratingContainers = document.querySelectorAll('.star-rating');
        
        ratingContainers.forEach(container => {
            const stars = container.querySelectorAll('i');
            const trackId = container.dataset.trackId;
            
            stars.forEach(star => {
                star.addEventListener('click', async () => {
                    const rating = star.dataset.rating;
                    
                    // Visual update
                    stars.forEach(s => {
                        s.classList.remove('active', 'text-warning');
                        s.style.color = s.dataset.rating <= rating ? '#ffc107' : '#dee2e6';
                    });
                    
                    // Submit rating
                    try {
                        const response = await fetch('/rate', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                user_id: userId,
                                track_id: trackId,
                                rating: rating
                            })
                        });
                        
                        const data = await response.json();
                        if (!response.ok) {
                            console.error('Rating error:', data.error);
                        }
                    } catch (error) {
                        console.error('Error submitting rating:', error);
                    }
                });
            });
        });
    }
});
