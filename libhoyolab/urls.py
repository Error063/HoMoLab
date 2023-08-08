# File
defaultAvatar = "https://bbs-static.miyoushe.com/avatar/avatarDefault.png"

api = "https://bbs-api.miyoushe.com/"

# Gets
getPostReplies = api + "post/wapi/getPostReplies?gids={0}&is_hot={1}&post_id={2}&size={3}&last_id={4}&order_type={5}"
webHome = "https://bbs-api-static.miyoushe.com/apihub/wapi/webHome?gids={0}&page={1}&page_size={2}"
getPostFull = api + "post/api/getPostFull?post_id={0}"
feedPosts = api + "post/api/feeds/posts?gid={0}&last_id=&fresh_action={1}&is_first_initialize=true&filter="
emoticon_set = "https://bbs-api-static.miyoushe.com/misc/api/emoticon_set?gid={0}"
getNewsList = api + "post/wapi/getNewsList?gids={0}&type={1}&page_size={2}&last_id={3}"
searchPosts = api + "post/wapi/searchPosts?gids={0}&keyword={1}&last_id={2}&size={3}"
Cookie_url = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={0}"
Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}"
getUserFullInfo = api + "user/api/getUserFullInfo?uid={0}"
userPost = api + "post/wapi/userPost?offset={0}&size={1}&uid={2}"
userReply = api + "post/wapi/userReply?offset={0}&size={1}&uid={2}"
history = api + "painter/api/history/list?offset={0}"

# Posts
follow = api + "timeline/api/follow"
unfollow = api + "timeline/api/unfollow"
upvotePost = api + "apihub/sapi/upvotePost"