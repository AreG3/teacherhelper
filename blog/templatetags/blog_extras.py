from django import template

register = template.Library()

@register.filter
def user_in_collaboration_group(user, post):
    return post.co_creation_group and user in post.co_creation_group.user_set.all()
