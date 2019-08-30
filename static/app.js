"use strict";

var base_url = "list/";

function getDisplayName(data) {
    var retour = data.filename;
    if(data.display_name !== undefined) {
        retour = data.display_name;
    }

    return retour;
}

function getAnchorHref(data, current_path) {
    var retour = `#${current_path}${data.filename}`;
    if(data.download_url !== undefined) {
        retour = data.download_url;
    }

    return retour;
}

function construct_page(data_list, container_id, current_path, metas) {
    $(container_id).empty();

    data_list.sort(function(a, b) {
        return getDisplayName(a).localeCompare(getDisplayName(b), 'fr', {
            sensitivity: "base",
            numeric: true
        });

    });

    data_list.forEach(function(data) {

        // Create the line div
        var paragraphe = document.createElement("div");
        paragraphe.setAttribute("class", "line-div");

        if(data.type && data.type.startsWith("image") && (metas === undefined || metas.show_images !== false)) {

            // Create image element when applicable
            var image = document.createElement("img");
            image.src = getAnchorHref(data, current_path);

            // Add the image to the line
            paragraphe.appendChild(image);
        } else {

            // Create link and containing div
            var lien = document.createElement("a");
            lien.href = getAnchorHref(data, current_path);
            lien.innerHTML = getDisplayName(data);

            var spanLien = document.createElement("div");
            spanLien.setAttribute("class", "link-div");
            spanLien.appendChild(lien);

            // Create date and containing div
            var date_mod = new Date(data.last_modified * 1000);
            var date_part = date_mod.toISOString().substr(0, 10);
            var hour_part = date_mod.toISOString().substr(11, 5);

            var spanDate = document.createElement("div");
            spanDate.setAttribute("class", "date-div");
            spanDate.innerHTML = date_part + " " + hour_part;

            // A both link and date to line
            paragraphe.appendChild(spanLien);
            paragraphe.appendChild(spanDate);
        }
        // Append line to the parent container
        this.append(paragraphe);
    }, $(container_id));
}

function loadUrl(path) {

    $.get(base_url + path, null, function(data, textStatus, request) {
        $("#current_path").text(data.current_path);

        var current_path = data.current_path;
        if(current_path !== "") {
            current_path += "/";
        }

        construct_page(data.directories, "#directories", current_path, data.metas);
        construct_page(data.files, "#files", current_path, data.metas);
    });
}

$(document).ready(function() {
    loadUrl(location.hash.substring(1));
});

window.onhashchange = function() {
    loadUrl(location.hash.substring(1));
};