# File
defaultAvatar = "https://bbs-static.miyoushe.com/avatar/avatarDefault.png"

api_base = "https://bbs-api.miyoushe.com/"

# Gets
Cookie_url = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={0}"
Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={0}&token_types=3&uid={1}"
getPostReplies = api_base + "post/wapi/getPostReplies?gids={0}&is_hot={1}&post_id={2}&size={3}&last_id={4}&order_type={5}"
webHome = api_base + "apihub/wapi/webHome?gids={0}&page={1}&page_size={2}"
getPostFull = api_base + "post/api/getPostFull?post_id={0}"
feedPosts = api_base + "post/api/feeds/posts?gid={0}&last_id=&fresh_action={1}&is_first_initialize=true&filter="
emoticon_set = api_base + "misc/api/emoticon_set?gid={0}"
getNewsList = api_base + "post/wapi/getNewsList?gids={0}&type={1}&page_size={2}&last_id={3}"
searchPosts = api_base + "post/wapi/searchPosts?gids={0}&keyword={1}&last_id={2}&size={3}"
getUserFullInfo = api_base + "user/api/getUserFullInfo?uid={0}"
userPost = api_base + "post/wapi/userPost?offset={0}&size={1}&uid={2}"
userReply = api_base + "post/wapi/userReply?offset={0}&size={1}&uid={2}"
history = api_base + "painter/api/history/list?offset={0}"

# Posts
follow = api_base + "timeline/api/follow"
unfollow = api_base + "timeline/api/unfollow"
upvotePost = api_base + "apihub/sapi/upvotePost"
collectPost = api_base + 'post/api/collectPost'
releaseReply = api_base + 'post/api/releaseReply'