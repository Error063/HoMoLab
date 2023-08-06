function hidePostCards(link) {
    try {
        let postcards = document.getElementsByClassName('rights')[0];
        postcards.setAttribute('style', 'visibility:hidden;')
        let select = document.getElementsByClassName('areas')[0].getElementsByClassName('selected')[0];
        select.removeAttribute('class');
        select.setAttribute('class', 'area');
    } catch (e) {
        console.log('bypass...');
    }
    if (link != null) {
        window.location.href = link;
    }
}
function pageControl(action) {
    document.getElementsByClassName('main')[0].setAttribute('style','visibility:hidden;');
    if (action === 'reload'){
        window.location.reload();
    }else if(action === 'back'){
        window.history.back();
    }
    document.getElementsByClassName('main')[0].setAttribute('style','');
}
function forumChange(){
    let forumLogo = document.getElementsByClassName('forumLogo')[0];
    forumLogo.setAttribute('style','visibility: hidden;');
    let select = document.getElementById('forumChange');
    let index = select.selectedIndex;
    let forum = select.options[index].value;
    hidePostCards('/' + forum);
}
function accountHandler() {
    pywebview.api.accountHandler().then(function (status) {
        if(status['status'] === 'ok'){
            window.location.reload();
        }
    })
}
function refreshLoginStatus() {
    pywebview.api.refreshLoginStatus().then(function (status) {
        if(status['status'] === 'ok'){
            window.location.reload();
        }
    })
}
function deleteLog() {
    pywebview.api.deleteLog().then(function (status) {
        if(status['status'] === 'ok'){
            alert('日志删除成功！');
        }else {
            alert('日志删除失败！');
        }
    })
}