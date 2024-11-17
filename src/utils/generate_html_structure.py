
def generate_html_styles(styles):
  return f"<style>{styles}</style>"

def generate_html_page(head_content, body_content):
  html_head = "<head></head>"
  html_body="<body></body>"

  if head_content:
    html_head = f"<head>{head_content}</head>"
  if body_content:
    html_body = f"<body>{body_content}</body>"

  html_content = f"""
  <!DOCTYPE html>
  <html>
  {html_head}
  {html_body}
  </html>
"""
  return html_content

def generate_html_structure(styles, body_content):
  page_styles = generate_html_styles(styles)
  html_structure = generate_html_page(page_styles, body_content)

  return html_structure