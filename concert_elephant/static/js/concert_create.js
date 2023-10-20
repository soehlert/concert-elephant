$(document).ready(function() {
    const csrfToken = $('[name=csrfmiddlewaretoken]').val();
    const artistCreateUrl = $('#artistCreateButton').data('url');
    const venueCreateUrl = $('#venueCreateButton').data('url');
    let openerCounter = 1;

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrfToken
        }
    });

    function autocompleteConfig(selector, url, updateFieldsFunc) {
        $(selector).autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: url,
                    type: "GET",
                    dataType: "json",
                    data: { term: request.term },
                    success: function(data) {
                        response(data);
                    }
                });
            },
            minLength: 2,
            response: function(event, ui) {
                if (!ui.content.length) {
                    $(this).val("No results found; please add a new one");
                }
            },
            select: function(event, ui) {
                updateFieldsFunc(ui, this);
                return false;
            }
        });
    }

    function updateArtistFields(ui, element) {
        $("#concert-artist").val(ui.item.id);
        $(element).val(ui.item.label);
    }

    function updateVenueFields(ui, element) {
        $("#concert-venue").val(ui.item.id);
        $(element).val(ui.item.label);
    }

    function fetchDisplayNameById(urlTemplate, hiddenInputId, displayInputId) {
        const itemId = $(hiddenInputId).val();
        if (itemId) {
            const url = urlTemplate.replace('__pk__', itemId);
            $.ajax({
                url: url,
                type: "GET",
                dataType: "json",
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                success: function(data) {
                    $(displayInputId).val(data.name);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.error("Error fetching name for ID:", itemId);
                    console.error("AJAX Error:", textStatus, errorThrown);
                    console.error("Response:", jqXHR.responseText);
                }
            });
        }
    }

    function updateOpenerFields(ui, element) {
        const counter = $(element).attr('id').split('-').pop();

        $(`#concert-opener-${counter}`).val(ui.item.id);
        $(element).val(ui.item.label);
    }

    // Set up autocomplete
    autocompleteConfig("#artist-autocomplete", $("#artist-autocomplete").data("autocomplete-url"), updateArtistFields);
    autocompleteConfig("#venue-autocomplete", $("#venue-autocomplete").data("autocomplete-url"), updateVenueFields);
    autocompleteConfig("#opener-autocomplete-1", $("#opener-autocomplete-1").data("autocomplete-url"), updateOpenerFields);

    function showModal(selector) {
        $(selector).modal('show');
        $(selector).find('form')[0].reset();
    }

    function closeModal(selector) {
        $(selector).modal('hide');
    }

    function handleModalSubmit(event, url, successCallback) {
        event.preventDefault();
        const formData = $(event.currentTarget).serialize();

        $.ajax({
            url: url,
            method: "POST",
            data: formData,
            success: function (data) {
                if (data.status === 'success') {
                    successCallback(data);
                } else if (data.status === 'error') {
                    // Display validation errors in the modal
                    let errorsHtml = '<ul>';
                    for (let field in data.errors) {
                        errorsHtml += '<li>' + data.errors[field] + '</li>';
                    }
                    errorsHtml += '</ul>';
                    $(event.currentTarget).find('.modal-messages').html('<div class="alert alert-danger text-center">' + errorsHtml + '</div>');
                }
            },
            error: function (error) {
                console.error(error);
            }
        });
    }

    $("#createArtistForm").on("submit", function (event) {
        handleModalSubmit(event, artistCreateUrl, function (data) {
            $("#modal-messages").html('<div class="alert alert-success text-center">' + data.message + '</div>');
            $('#artist-autocomplete').val(data.artist);
            $('#concert-artist').val(data.artistId);
            setTimeout(() => closeModal("#createArtistModal"), 1000);
        });
    });

    $("#createVenueForm").on("submit", function (event) {
        handleModalSubmit(event, venueCreateUrl, function (data) {
            $("#modal-venue-messages").html('<div class="alert alert-success text-center">' + data.message + '</div>');
            const venueName = data.venue.name + " - " + data.venue.city + ", " + (data.venue.state ? data.venue.state : data.venue.country);
            $('#venue-autocomplete').val(venueName);
            $('#concert-venue').val(data.venue.id);
            setTimeout(() => closeModal("#createVenueModal"), 1000);
        });
    });

    $("#createOpenerForm").on("submit", function (event) {
        handleModalSubmit(event, artistCreateUrl, function (data) {
            $("#modal-opener-messages").html('<div class="alert alert-success text-center">' + data.message + '</div>');
            $('#opener-autocomplete-1').val(data.artist);
            $('#concert-opener-1').val(data.artistId);
            setTimeout(() => closeModal("#createOpenerModal"), 1000);
        });
    });

    $("#concert-form").on("submit", function(event) {
        event.preventDefault();
        const formData = $(this).serialize();
        $.ajax({
            url: $(this).attr('action'), // Using the form's action attribute to determine where to post
            method: "POST",
            data: formData,
            success: function(response) {
                if (response.status === "success") {
                    console.log("success: redirecting to concert list")
                    window.location.href = concertListUrl;
                } else if (response.status === "error") {
                    $(".error").remove();

                    const errors = response.errors;
                    for (const field in errors) {
                        $(`[name=${field}]`).after(`<div class="error">${errors[field]}</div>`);
                    }
                }
            },
            error: function(response) {
                let jsonResponse = JSON.parse(response.responseText);
                let errors = jsonResponse.errors;

                // Clear any existing alerts
                $(".alert").remove();

                for (let field in errors) {
                    let errorMessage = errors[field].join(', ');
                    let alertHtml = '<div class="alert alert-danger mt-2" role="alert">' + errorMessage + '</div>';

                    if (field === "__all__") {
                        $(".custom-errors-container").append(alertHtml);
                    } else {
                        // Append the alert after the input field with the error
                        $("input[name='" + field + "']").closest('.form-group').append(alertHtml);
                    }
                }
            }
        });
    });

    function addOpenerField() {
        openerCounter++;

        const autocompleteUrl = $("#opener-autocomplete-1").data("autocomplete-url");

        const newOpener = `
        <div class="form-group mb-2">
            <div>
                <label for="opener-autocomplete-${openerCounter}">Opener ${openerCounter}</label>
            </div>
            <input type="text"
                   id="opener-autocomplete-${openerCounter}"
                   data-autocomplete-url="${autocompleteUrl}"
                   class="form-control opener-input"
                   placeholder="Start typing opener name..." />
            <input type="hidden" name="opener-${openerCounter}" id="concert-opener-${openerCounter}" />
        </div>
    `;

        $("#opener-container").append(newOpener);
        autocompleteConfig(`#opener-autocomplete-${openerCounter}`, autocompleteUrl, updateOpenerFields);
    }


    $(document).on("click", "[id^=createOpenerButton-]", addOpenerField);

    $(".ui-autocomplete").addClass("rounded");

    // Event handlers for modals
    $("#createNewArtistButton").click(() => showModal("#createArtistModal"));
    $("#closeArtistModalButton").click(() => closeModal("#createArtistModal"));
    $("#createNewVenueButton").click(() => showModal("#createVenueModal"));
    $("#closeVenueModalButton").click(() => closeModal("#createVenueModal"));
    $("#createNewOpenerButton").click(() => showModal("#createOpenerModal"));
    $("#closeOpenerModalButton").click(() => closeModal("#createOpenerModal"));

    // Repopulate artist, venue, and opener fields based on hidden input values
    fetchDisplayNameById(artistDetailUrlTemplate, '#concert-artist', '#artist-autocomplete');
    fetchDisplayNameById(venueDetailUrlTemplate, '#concert-venue', '#venue-autocomplete');
    for (let i = 1; i <= openerCounter; i++) {
        fetchDisplayNameById(artistDetailUrlTemplate, `#concert-opener-${i}`, `#opener-autocomplete-${i}`);
    }
});
