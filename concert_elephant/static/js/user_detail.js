document.addEventListener("DOMContentLoaded", function() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const reviewModal = document.querySelector('#createReviewModal');
    const reviewForm = document.querySelector('#reviewForm');
    const reviewText = document.querySelector('#reviewText');
    const starRating = document.querySelector('#starRating');
    const reviewIdField = document.querySelector('#reviewId');
    const showModalBtns = document.querySelectorAll('.showModalBtn');
    const editButtons = document.querySelectorAll('.edit-review-btn');

    const addReviewURLTemplate = document.querySelector('#concert-review-submit').getAttribute('data-add-review-url-template');
    const updateReviewURLTemplate = document.querySelector('#createReviewModal').getAttribute('data-update-review');
    const deleteReviewURLTemplate = document.querySelector('#deleteReviewIcon').getAttribute('data-delete-review-url-template');

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrfToken
        }
    });

    function fetchConcertDetails(concertId, getConcertURL) {
        return fetch(getConcertURL.replace('REVIEW_ID', concertId), {
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

    showModalBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();

            // Clearing previous state
            reviewText.value = '';
            starRating.value = '';
            reviewModal.querySelectorAll('input').forEach(input => {
                if (input.type === "text" || input.type === "number") {
                    input.value = '';
                }
            });
            const concertId = btn.getAttribute('data-concert-id');
            const row = e.currentTarget.closest('tr');
            const getConcertURL = row.getAttribute('data-concert-details-url');

            fetchConcertDetails(concertId, getConcertURL).then(details => {
                reviewModal.querySelector('#modalTitle').textContent = `Add Review for ${details.artist} on ${details.date}`;
                reviewModal.setAttribute('data-concert-id', concertId);
                reviewModal.setAttribute('data-action-type', 'add');
                reviewModal.querySelector('#deleteReviewIcon').style.display = 'none';
                reviewIdField.value = "";
                $(reviewModal).modal('show');
            });
        });
    });

    editButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const getReviewURLTemplate = e.currentTarget.getAttribute('data-review-details-url');
            const reviewId = btn.getAttribute('data-review-id');
            const concertId = btn.getAttribute('data-concert-id');
            const row = e.currentTarget.closest('tr');
            const getConcertURL = row.getAttribute('data-concert-details-url');

            reviewModal.setAttribute('data-action-type', 'edit');
            reviewIdField.value = reviewId;

            fetchConcertDetails(concertId, getConcertURL)
                .then(concertDetails => {
                    return fetch(getReviewURLTemplate.replace('REVIEW_ID', reviewId), {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
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

    reviewForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const actionType = reviewModal.getAttribute('data-action-type');
        const concertId = reviewModal.getAttribute('data-concert-id');
        const reviewId = reviewIdField.value;
        let url = "";

        if (actionType === 'add') {
            url = addReviewURLTemplate.replace(0, concertId);
        } else if (actionType === 'edit') {
            url = updateReviewURLTemplate.replace(0, reviewId);
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
                location.reload();
            } else {
                console.error(data.errors);
            }
        });
    });

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

    document.querySelector('#deleteReviewIcon').addEventListener('click', function() {
        const confirmDeleteBtn = document.querySelector('#confirmDeleteBtn');
        confirmDeleteBtn.setAttribute('data-review-id', reviewIdField.value);
        $('#confirmDeleteModal').modal('show');
    });

    document.querySelector('#confirmDeleteBtn').addEventListener('click', function() {
        const reviewId = document.getElementById('reviewId').value;
        const deleteURL = deleteReviewURLTemplate.replace(0, reviewId);

        fetch(deleteURL,{
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

        $('#confirmDeleteModal').modal('hide');
    });

    document.querySelector('#closeReviewModalButton').addEventListener('click', function() {
        $('#createReviewModal').modal('hide');
    });

    window.toggleReview = toggleReview;
});
