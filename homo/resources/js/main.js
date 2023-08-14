window.pywebview_loaded = false
function hidePostCards(link) {
    try {
        let actionView = document.getElementsByClassName('userActionView')[0];
        actionView.innerHTML = '加载中...';
        let postcards = document.getElementsByClassName('rights')[0];
        postcards.setAttribute('style', 'visibility:hidden;')
        let select = document.getElementsByClassName('areas')[0].getElementsByClassName('selected')[0];
        select.removeAttribute('class');
        select.setAttribute('class', 'area');
    } catch (e) {
    }
    if (link != null) {
        window.location.href = link;
    }
}
function hideAndRedirect(link) {
    try {
        let actionView = document.getElementsByClassName('userActionView')[0];
        actionView.innerHTML = '加载中...';
        let postcards = document.getElementsByClassName('main')[0];
        postcards.setAttribute('style', 'visibility:hidden;')
    } catch (e) {
    }
    if (link != null) {
        window.location.href = link;
    }
}
function pageControl(action) {
    let actionView = document.getElementsByClassName('userActionView')[0];
    actionView.innerHTML = '加载中...';
    document.getElementsByClassName('main')[0].setAttribute('style','visibility:hidden;');
    if (action === 'reload'){
        hideAndRedirect(null)
        window.location.reload();
    }else if(action === 'back'){
        hideAndRedirect(null)
        window.history.back();
    }
    document.getElementsByClassName('main')[0].setAttribute('style','');
}
function forumChange(){
    let actionView = document.getElementsByClassName('userActionView')[0];
    actionView.innerHTML = '加载中...';
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
function followUser(uid, action) {
    pywebview.api.followUser(uid, action).then(function (status) {
        if (status['status'] === 'ok'){
            let btn = document.getElementsByClassName("followBtn")[0]
            btn.textContent = action === 'follow'?'取消关注':'关注'
            btn.setAttribute('class', `followBtn ${action === 'follow'?'follow':'unfollow'}`)
            btn.setAttribute('onclick', `followUser(${uid}, ${action === 'follow'?'unfollow':'follow'})`)
        }
        console.info(status['status'])
    })
}
function upVote(post_id, isCancel) {
    pywebview.api.upVote(post_id, isCancel).then(function (status) {
        if (status['status'] === 'ok'){
            let btn = document.getElementsByClassName("voteBtn")[0]
            btn.textContent = isCancel?'点赞':'取消点赞'
            btn.setAttribute('onclick', `upVote('${post_id}', ${(!isCancel).toString()})`)
            let voteNum = document.getElementsByClassName('voteNum')[0]
            voteNum.textContent = isCancel?(Number(voteNum.textContent) - 1).toString():(Number(voteNum.textContent) + 1).toString()
        }
        console.info(status['status'])
    })
}
function collectPost(post_id, isCancel) {
    pywebview.api.collectPost(post_id, isCancel).then(function (status) {
        if (status['status'] === 'ok'){
            let btn = document.getElementsByClassName("collectBtn")[0]
            btn.textContent = isCancel?'收藏':'取消收藏'
            btn.setAttribute('onclick', `collectPost('${post_id}', ${(!isCancel).toString()})`)
            let collectNum = document.getElementsByClassName('collectNum')[0]
            collectNum.textContent = isCancel?(Number(collectNum.textContent) - 1).toString():(Number(collectNum.textContent) + 1).toString()
        }
        console.info(status['status'])
    })
}
function openAppConfig() {
    pywebview.api.openAppConfig().then(function () {

    })
}
window.onblur = function() {
    if (!document.hasFocus()){
        let header = document.getElementsByClassName("headers")[0]
        header.setAttribute("style", "background-color: #f3f3f3;")
    }
};
window.onfocus = function () {
    let header = document.getElementsByClassName("headers")[0]
    let style = ''
    try {
        pywebview.api.getColor().then(function (colorSet) {
            let color = colorSet['colorSet'][0]
            style = `background-color: #${color};`
        })
    } catch (e) {
        console.log("using pywebview js api failed!")
    } finally {
        header.setAttribute("style", style)
    }
}
window.onbeforeunload = function(){
    hideAndRedirect(null)
}
window.addEventListener('pywebviewready', function() {
    window.pywebview_loaded = true
    console.log('pywebview has been loaded')
})