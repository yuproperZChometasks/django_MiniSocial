from django import template
import re

register = template.Library()

@register.filter
def highlight(text, q):
    if not q:
        return text
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    return pattern.sub(f'<mark>{q}</mark>', str(text))