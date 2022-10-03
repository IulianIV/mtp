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
        this.on('sending', function (file, xhr, formData) {
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

function hidePermissions(module_id) {
    let module = document.getElementById(module_id + "_table_body");
    let showButton = document.getElementById(module_id);

    if (module.style.display === "none") {
        module.style.display = "";
        showButton.className = "btn btn-info btn-sm";
        showButton.textContent = "Collapse";
    } else {
        module.style.display = "none";
        showButton.className = "btn btn-secondary btn-sm";
        showButton.textContent = "Expand";

    }

}

$(document.getElementsByClassName('btn btn-success')).click(function(){
    let id = $(this).attr('id');

    console.log(id)
    console.log(document.getElementById("user_role_select_" + id).value)

    $.ajax({
        serverSide: false,
        url: "/api/update-user-role",
        data: {
            user_id: id,
            user_new_role: document.getElementById("user_role_select_" + id).value
        },
        success: function () {
            window.location.replace("/permissions/all-users?success=1");
        }
    });

});

