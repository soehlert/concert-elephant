document.addEventListener("DOMContentLoaded", function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const reviewModal = document.querySelector('#createReviewModal');
    const reviewForm = document.querySelector('#reviewForm');
    const reviewText = document.querySelector('#reviewText');
    const starRating = document.querySelector('#starRating');
    const reviewIdField = document.querySelector('#reviewId');
    const showModalBtns = document.querySelectorAll('.showModalBtn');
    const editButtons = document.querySelectorAll('.edit-review-btn');

    // Grab concert details to use elsewhere
    function fetchConcertDetails(concertId) {
            return fetch(`/concerts/${concertId}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    console.error("Network issues fetching concert details:", response.statusText);
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                return {
                    artist: data.artist,
                    date: data.date
                };
            })
            .catch(error => {
                console.error("Error fetching concert details:", error);
            });
        }

    // Event listener to open the modal for adding a review
    showModalBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const concertId = btn.getAttribute('data-concert-id');

            fetchConcertDetails(concertId).then(details => {
                reviewModal.querySelector('#modalTitle').textContent = `Add Review for ${details.artist} on ${details.date}`;
                reviewModal.setAttribute('data-concert-id', concertId);
                reviewModal.setAttribute('data-action-type', 'add');
                reviewModal.querySelector('#deleteReviewIcon').style.display = 'none';
                reviewIdField.value = "";  // Clear the review ID field
                $(reviewModal).modal('show');
            });
        });
    });

    // Event listener for the modal to edit a review
    editButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const reviewId = btn.getAttribute('data-review-id');
            const concertId = btn.getAttribute('data-concert-id');

            reviewModal.setAttribute('data-action-type', 'edit');
            reviewIdField.value = reviewId;

            // First fetch the concert details
            fetchConcertDetails(concertId)
                .then(concertDetails => {
                    // Once you have the artist and date, fetch the review details
                    return fetch(`/concert/review/${reviewId}/`, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Combine the information and display in the modal
                        reviewText.value = data.note;
                        starRating.value = data.rating;
                        reviewModal.querySelector('#modalTitle').textContent = `Edit Review for ${concertDetails.artist} on ${concertDetails.date}`;
                        reviewModal.querySelector('#deleteReviewIcon').style.display = 'inline';
                        $(reviewModal).modal('show');
                    });
                })
                .catch(error => {
                    console.error("Error fetching details:", error);
                });
        });
    });

    // Add a new concert review or edit a current one
    reviewForm.addEventListener('submit', function(e) {
        e.preventDefault();

        let actionType = reviewModal.getAttribute('data-action-type');
        let concertId = reviewModal.getAttribute('data-concert-id');
        let reviewId = reviewIdField.value;
        let url = "";

        if (actionType === 'add') {
            url = reviewModal.getAttribute('data-add-review').replace('0', concertId);
        } else if (actionType === 'edit') {
            url = reviewModal.getAttribute('data-update-review').replace('0', reviewId);
        }

        fetch(url, {
            method: 'POST',
            body: new FormData(reviewForm),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();  // Reload the page to show the updated data
            } else {
                // Handle the errors here
                console.error(data.errors);
            }
        });
    });

    // Delete a concert review with the trash can icon
    document.querySelector('#deleteReviewIcon').addEventListener('click', function() {
        const reviewId = document.querySelector('#reviewId').value;

        if (!reviewId) return;

        fetch(`/concert/review/delete/${reviewId}/`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // To indicate this is an AJAX call
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();  // Reload the page to show the updated data
            } else {
                // Handle the errors here
                console.error(data.errors);
            }
        });
    });

    // Toggle the show more and show less buttons
    function toggleReview(buttonElement) {
        const parentElement = buttonElement.closest('.review-note');
        const truncatedNote = parentElement.querySelector('.truncated-note');
        const fullNote = parentElement.querySelector('.full-note');

        if (truncatedNote.style.display !== 'none') {
            truncatedNote.style.display = 'none';
            fullNote.style.display = 'inline';
        } else {
            truncatedNote.style.display = 'inline';
            fullNote.style.display = 'none';
        }
    }

    // Close the add and edit modals
    document.querySelector('#closeReviewModalButton').addEventListener('click', function() {
        $('#createReviewModal').modal('hide');
    });

    window.toggleReview = toggleReview;  // Make it available globally as you're using it inline in the template

});
