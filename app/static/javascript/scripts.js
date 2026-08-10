async function bookmark(phobia_id) {
    const params = new URLSearchParams({
        phobia_id: phobia_id
    });
    let bookmark = await fetch(`/create_bookmark?${params}`,);
    if (await bookmark.text()) {
        document.getElementById("bookmark-star").style.backgroundColor = "#ffff00"
    }
}