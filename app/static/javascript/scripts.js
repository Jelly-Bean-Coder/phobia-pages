async function bookmark(phobia_id) {
    const params = new URLSearchParams({
        phobia_id: phobia_id
    });
    let bookmark = await fetch(`/create_bookmark?${params}`,);
    let status = bookmark.status

    let el = document.getElementById("bookmark-star");

    if (status === 201) {
        el.classList.add("bookmark-created");
    }
    else if (status === 200) {
        el.classList.remove("bookmark-created");
    }
}