
import libhoyolab
post_id="41214610"
import threadRender
article = libhoyolab.Article(post_id)
print(article.getTitle())
print(article.getAuthor())
# html = threadRender.render(article.getStructuredContent())
# with open("opt.html", mode="w", encoding="utf8") as f:
#     f.write(html)