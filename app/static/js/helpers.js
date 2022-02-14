// Show/Hide EUR Preview jQuery
$(document).ready(function () {
    $('button[name="show_eurview"]').click(function () {
        $('tr[class="table-primary eurview"]').show();
        $('button[name="hide_eurview"]').show();
    });
    $('button[name="hide_eurview"]').click(function () {
        $('tr[class="table-primary eurview"]').hide()
        $('button[name="hide_eurview"]').hide();

    });
});

// enable bootstrap tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

// DropzoneJS functionality config
$("div#dropzone").dropzone({
    url: '/api/post/image',
    progressBarWidth: '100%',
    maxFileSize: '5 MB',
    uploadMultiple: false,
    createImageThumbnails: true,
    maxFiles: '1',
    init: function () {
        let dropzone = this;


        // on button "close" or "X" press, remove dropzone instantiation.
        this.on('sending', function(file, xhr, formData){
            let acceptedFile = dropzone.getAcceptedFiles()[0];
            formData.append('file_uuid', acceptedFile.upload.uuid);
        });

        $('input[id="submit_post"]').click(function () {
            let acceptedFile = dropzone.getAcceptedFiles()[0];
            document.getElementById("image_uuid").value = acceptedFile.upload.uuid;
        });

        $('input[id="submit_update"]').click(function () {
            let acceptedFile = dropzone.getAcceptedFiles()[0];
            document.getElementById("image_uuid").value = acceptedFile.upload.uuid;
        });
    }
});

