"""
api的集合
"""
api_base = "https://bbs-api.miyoushe.com/"

# File
defaultAvatar = "https://bbs-static.miyoushe.com/avatar/avatarDefault.png"

# Gets
Cookie_url = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={0}"
Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={0}&token_types=3&uid={1}"
Cookie_url3 = 'https://api-takumi.mihoyo.com/auth/api/getCookieAccountInfoBySToken?stoken={0}&uid={1}'
mmt_pwd = "https://webapi.account.mihoyo.com/Api/create_mmt?scene_type=1&now={}&reason=user.mihoyo.com%23%2Flogin%2Fpassword&action_type=login_by_password&account={}&t={}"
getPostReplies = api_base + "post/api/getPostReplies?gids={0}&is_hot={1}&post_id={2}&size={3}&last_id={4}&order_type={5}&only_master={6}"
getSubReplies = api_base + "post/api/getSubReplies?post_id={0}&floor_id={1}&last_id={2}&size={3}"
getRootReplyInfo = api_base + 'post/api/getRootReplyInfo?post_id={0}&reply_id={1}'
webHome = api_base + "apihub/wapi/webHome?gids={0}&page={1}&page_size={2}"
getPostFull = api_base + "post/api/getPostFull?post_id={0}"
feedPosts = api_base + "post/api/feeds/posts?gid={0}&last_id=0&fresh_action={1}&is_first_initialize=true&filter="
emoticon_set = api_base + "misc/api/emoticon_set?gid={0}"
getNewsList = api_base + "post/wapi/getNewsList?gids={0}&type={1}&page_size={2}&last_id={3}"
searchPosts = api_base + "post/wapi/searchPosts?gids={0}&keyword={1}&last_id={2}&size={3}"
getUserFullInfo = api_base + "user/api/getUserFullInfo?uid={0}"
userPost = api_base + "post/wapi/userPost?offset={0}&size={1}&uid={2}"
userReply = api_base + "post/wapi/userReply?offset={0}&size={1}&uid={2}"
history = api_base + "painter/api/history/list?offset={0}"
getForumPostList = api_base + "post/wapi/getForumPostList?forum_id={0}&gids={1}&is_good={2}&is_hot={3}&page_size={4}&sort_type={5}&last_id={6}"

# Posts
login = 'https://webapi.account.mihoyo.com/Api/login_by_password'
follow = api_base + "timeline/api/follow"
unfollow = api_base + "timeline/api/unfollow"
upvotePost = api_base + "apihub/sapi/upvotePost"
collectPost = api_base + 'post/api/collectPost'
releaseReply = api_base + 'post/api/releaseReply'
upvoteReply = api_base + "apihub/sapi/upvoteReply"
Cookie_url4 = 'https://passport-api.mihoyo.com/account/ma-cn-session/web/webVerifyForGame'