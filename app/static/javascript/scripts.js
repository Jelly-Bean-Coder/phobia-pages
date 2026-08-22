async function bookmark(phobia_id) {


    function newFlashMessage(message, type) {
    let template = document.getElementById("template");

    // 1. Define allowed alert types (fallback to 'primary' if invalid)
    const validTypes = ['success', 'danger', 'warning', 'info', 'secondary'];
    const alertType = validTypes.includes(type) ? type : 'primary';

    // 2. Set the HTML string using standard JavaScript template literals
    template.innerHTML = `
      <div class="alert alert-${alertType} alert-dismissible fade show position-absolute top-0 start-50 translate-middle-x w-100 z-3 mt-3" role="alert" style="z-index: 1050;">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;

    // 3. Stamp it out onto the page
    document.body.appendChild(template.content.cloneNode(true));
}

    const params = new URLSearchParams({
        phobia_id: phobia_id
    });
    let bookmark = await fetch(`/create_bookmark?${params}`,);
    let status = bookmark.status

    let el = document.getElementById("bookmark-star");

    if (status === 201) {
        el.classList.add("bookmark-created");
        newFlashMessage("Bookmark created!", "success");
    }
    else if (status === 200) {
        el.classList.remove("bookmark-created");
        newFlashMessage("Bookmark removed!", "success");
    }
}