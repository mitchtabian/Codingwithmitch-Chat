
document.addEventListener("DOMContentLoaded", function() {

    var $ = typeof($) === "undefined" ? django.jQuery : $,
        _ = _cropper_messages;

    if($("#cropper_modal").length > 0) return;

    $(document.body).append($(
        '<div id="cropper_modal" role="dialog" aria-labelledby="modalLabel" tabindex="-1">' +
            '<div class="modal-dialog modal-lg" role="document">' +
                '<div class="modal-content">' +
                    '<div class="modal-header">' +
                        '<h4 class="modal-title" id="modalLabel" data-warning=""></h4>' +
                    '</div>' +
                    '<div class="modal-body">' +
                        '<div class="img-container">' +
                            '<img id="cropper_image">' +
                        '</div>' +
                        '<div class="preview_container">' +
                            '<div class="cropper_preview"></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="modal-footer submit-row">' +
                        '<div id="btn-actions" class="col-md-12">' +
                            '<button type="button" class="rotate-left" data-action="cropper.rotate(-10)" title="' + _['Rotate (clockwise)'] + '"></button>' +
                            '<button type="button" class="rotate-right" data-action="cropper.rotate(10)" title="' + _['Rotate (counterclockwise)'] + '"></button>' +
                            '<button type="button" class="reset" data-action="cropper.reset()" title="' + _['Redefine'] + '"></button>' +
                        '</div>' +
                        '<input type="checkbox" id="cropper_limit_dimensions" checked />' +
                        '<label for="cropper_limit_dimensions" title="' + _['Automatically limits the image\'s dimensions'] + '">' + _['Limit dimensions'] + '</label>' +
                        '<input type="button" id="btn-cancel" value="' + _['Cancel'] + '" />' +
                        '<input type="button" id="btn-save" class="default" value="' + _['Save image'] + '" />' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>'
    ));

    var imageFields = $(".cropperImageField.linked").not(".inline-related .cropperImageField")
        ,cropper
        ,$currentEditor
        ,currentFileName
        ,cropQueue = []
        ,$cropperFileUpload = $('<input type="file" id="cropper_file" style="display: none" accept="image/*" />');

    $("form").append($cropperFileUpload);

    cropper = new Cropper($("#cropper_image")[0], {
        autoCropArea: 1,
        viewMode: 1,
        dragMode: 'move',
        cropBoxMovable: true,
        cropBoxResizable: true,
        preview: ".cropper_preview",
        ready: checkImageDimensions,
    });

    function setPreview($field, url) {
        if(url) $("img", $field).attr("src", url);
    }


    $(".cropperImageField img").each(function (i, e) {
        var $img = $(e), url = $img.attr("src");

        if(url && url.substring(0, 9) == "filename:") {
            url = url.split(";").splice(1).join(";");
            $img.attr("src", url);
        }
    });


    $("span.cropper-move").on("mouseup", function() {
        var $modalBody = $(".modal-body");
        $("canvas", $modalBody).remove();
        $modalBody.append(cropper.getCroppedCanvas());
    });

    $(".cropperImageField .deleteImage").click(function () {
        var $parent = $(this).closest(".cropperImageField");

        $("img", $parent).attr("src", null);
        $("input", $parent).val("");
    });

    $(".cropperImageField .placeholder, .cropperImageField img").click(function() {
        $cropperFileUpload.val("");
        var $field = $(this).closest(".cropperImageField").eq(0);
        if($field.closest(".inline-related").length === 0) {
            cropQueue = imageFields.not($field).toArray();
        } else {
            cropQueue = $field.closest("tr").find(".cropperImageField.linked").not($field).toArray();
        }
        cropQueue.splice(0,0,$field[0]);
        $cropperFileUpload.click();
    });

    $cropperFileUpload.change(function() {
        var input = this;
        if(input.value === "") return;

        $currentEditor = $(cropQueue.shift());

        if($currentEditor.length === 0) {
            $cropperFileUpload.val("");
            return;
        }

        currentFileName = input.value.split("\\").pop().replace(/\.([^\.]+)$/, "").substr(0, 50);

        var aspectRatio = $currentEditor.attr("data-aspectratio") || null;

        if(input.files && input.files[0]) {
            var reader = new FileReader()
                ,file = input.files[0]
                ,isGif = file.type == "image/gif"
                ,maxSize = 5; // In MB

            if(file.size > maxSize * 1024 * 1024) {
                alert(_["File above the size limit"] + " (" + maxSize + "MB).");
                return;
            } else if(file.type.substr(0,5) !== "image") {
                alert(_["Invalid image file"]);
                return;
            }

            reader.onload = function (e) {
                if(isGif) {
                    var dataUrl = e.target.result;

                    $("input", $currentEditor).val("filename:" + currentFileName +".gif;" + dataUrl);
                    setPreview($currentEditor, dataUrl);
                    $cropperFileUpload.val("");
                } else {
                    openModal(e.target.result, aspectRatio);
                }
            };
            reader.readAsDataURL(input.files[0]);
        }
    });


    function openModal(imageObject, aspectRatio) {
        var $modal = $('#cropper_modal'),
            hasFixedDimensions = !!$currentEditor.attr("data-dimensions");

        $modal.removeClass("can_limit_dimensions");
        $("#cropper_limit_dimensions").prop("checked", !hasFixedDimensions);

        if(!hasFixedDimensions) $modal.addClass("can_limit_dimensions");

        $modal.css("display", "flex");

        $("#modalLabel").html(_["Crop for"] + " " + $currentEditor.attr("data-label"));

        cropper.replace(imageObject);
        cropper.setAspectRatio(aspectRatio);
    }

    function checkImageDimensions() {
        $("#cropper_modal .modal-title").attr("data-warning", "");

        var dimensions = $currentEditor.attr("data-dimensions");
        if(dimensions) {
            dimensions = dimensions.split(",");
            var imageData = cropper.getImageData();

            if(imageData.naturalWidth < dimensions[0] || imageData.naturalHeight < dimensions[1]) {
                var warning_message = _["Selected image ({source_image_size}) is smaller than the recommended size ({fixed_image_size}). Loss of quality may occur."]
                    .replace("{source_image_size}", imageData.naturalWidth + "x" + imageData.naturalHeight)
                    .replace("{fixed_image_size}", dimensions.join("x"));

                $("#cropper_modal .modal-title").attr("data-warning", warning_message);
            }
        }
    }

    $('#btn-actions').click(function(e) {
        var $button = $(e.target).closest("button");

        if($button.attr("data-method")) {
            var method = $button.attr("data-method"), arg  = $button.attr("data-arg");
            if(method.includes("scale")) $button.attr("data-arg", arg == 1 ? -1 : 1);
            eval("method(" + arg + ")");
        } else {
            eval($button.attr("data-action"));
        }
    });

    $('#btn-save').click(function(e) {
        var options = { }
            ,fixedDimensions = $currentEditor.attr("data-dimensions") || null
            ,hasLimitedDimensions = $("#cropper_limit_dimensions").is(":checked") && !fixedDimensions
            ,croppedCanvas = cropper.getCroppedCanvas(options)
            ,maxDimension = 1920;

        if(fixedDimensions) {

            fixedDimensions = fixedDimensions.split(",");
            options.width = fixedDimensions[0];
            options.height = fixedDimensions[1];
            croppedCanvas = cropper.getCroppedCanvas(options);

        } else if(hasLimitedDimensions) {

            if(croppedCanvas.height > maxDimension || croppedCanvas.width > maxDimension) {

                var proportion = maxDimension / Math.max(croppedCanvas.width, croppedCanvas.height),
                    targetWidth = Math.ceil(croppedCanvas.width * proportion);

                options = {
                    width: targetWidth,
                    height: Math.ceil(croppedCanvas.height * proportion),
                    imageSmoothingEnabled: true,
                    imageSmoothingQuality: "high"
                }
                croppedCanvas = cropper.getCroppedCanvas(options);
            }

        }

        var mimeType = $cropperFileUpload[0].files[0].type,
            dataUrl = croppedCanvas.toDataURL(mimeType, 0.8);

        setPreview($currentEditor, dataUrl);
        $("input", $currentEditor).val("filename:" + currentFileName +";" + dataUrl);
        $('#cropper_modal').hide();
        $cropperFileUpload.change();
    });

    $("#btn-cancel").click(function() {
        $cropperFileUpload.val("");
        $("#cropper_modal").hide();
    });

});