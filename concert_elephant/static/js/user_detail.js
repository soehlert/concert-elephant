document.addEventListener("DOMContentLoaded", function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const reviewModal = document.querySelector('#createReviewModal');
    const reviewForm = document.querySelector('#reviewForm');
    const reviewText = document.querySelector('#reviewText');
    const starRating = document.querySelector('#starRating');
    const reviewIdField = document.querySelector('#reviewId');
    const showModalBtns = document.querySelectorAll('.showModalBtn');
    const editButtons = document.querySelectorAll('.edit-review-btn');

    const addReviewURL = document.querySelector('#concert-review-submit').getAttribute('data-add-review-url-template');
    const updateReviewURL = document.querySelector('#createReviewModal').getAttribute('data-update-review');
    const deleteReviewURL = document.querySelector('#deleteReviewIcon').getAttribute('data-delete-review-url');

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrfToken
        }
    });

    // Grab concert details to use elsewhere
    function fetchConcertDetails(concertId, getConcertURL) {
        return fetch(getConcertURL.replace('0', concertId), {
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
        btn.addEventListener('click', (e) => {
            const concertId = btn.getAttribute('data-concert-id');
            const row = e.currentTarget.closest('tr');
            const getConcertURL = row.getAttribute('data-concert-details-url');

            fetchConcertDetails(concertId, getConcertURL).then(details => {
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
        btn.addEventListener('click', (e) => {
            const getReviewURL = e.currentTarget.getAttribute('data-review-details-url');
            const reviewId = btn.getAttribute('data-review-id');
            const concertId = btn.getAttribute('data-concert-id');
            const row = e.currentTarget.closest('tr');
            const getConcertURL = row.getAttribute('data-concert-details-url');

            reviewModal.setAttribute('data-action-type', 'edit');
            reviewIdField.value = reviewId;

            // First fetch the concert details
            fetchConcertDetails(concertId, getConcertURL)
                .then(concertDetails => {
                    // Once you have the artist and date, fetch the review details
                    return fetch(getReviewURL.replace('0', reviewId), {
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
            url = addReviewURL.replace('0', concertId);
        } else if (actionType === 'edit') {
            url = updateReviewURL.replace('0', reviewId);
        }

        fetch(url, {
            method: 'POST',
            body: new FormData(reviewForm),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();  // Reload the page to show the updated data
            } else {
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

    // Open the delete confirmation modal
    document.querySelector('#deleteReviewIcon').addEventListener('click', function() {
        const confirmDeleteBtn = document.querySelector('#confirmDeleteBtn');
        confirmDeleteBtn.setAttribute('data-review-id', reviewId);
        $('#confirmDeleteModal').modal('show');
    });

    // Delete the concert review
    document.querySelector('#confirmDeleteBtn').addEventListener('click', function() {
        let reviewId = document.getElementById('reviewId').value;

        // Send a DELETE request to the server
        fetch(deleteReviewURL.replace('0', reviewId), {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to delete review');
            }
        })
        .then(data => {
            if (data.success) {
                $('#createReviewModal').modal('hide');
                location.reload();
            } else {
                console.error(data.errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });

        // Close the confirmation modal
        $('#confirmDeleteModal').modal('hide');
    });

    // Close the add and edit modals
    document.querySelector('#closeReviewModalButton').addEventListener('click', function() {
        $('#createReviewModal').modal('hide');
    });

    // Make this available, so I can call it inline in the template
    window.toggleReview = toggleReview;
});
