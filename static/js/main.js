function hidePostCards(link) {
    try {
        let postcards = document.getElementsByClassName('rights')[0];
        postcards.setAttribute('style', 'visibility:hidden;')
        let select = document.getElementsByClassName('areas')[0].getElementsByClassName('selected')[0];
        select.removeAttribute('class');
        select.setAttribute('class', 'area');
    } catch (e) {
        console.log('bypass...')
    }
    if (link != null) {
        window.location.href = link;
    }
}