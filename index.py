import utils

# Enter blog post title
# Example: Python and AI
title = input("Blog post title: ")

# Enter blog post tags
# Example: tech, python, coding, AI, machine learning
tags = input("Blog post tags: ")

# Enter blog post summary
# Example: I talk about what the future of AI could hold for Python
summary = input("Blog post summary: ")

# Generate blog content with OpenAI
blog_content = utils.get_blog_from_openai(
    title,
    tags,
    summary
)

# Generate cover image with Dalle2
_, cover_image_save_path = utils.get_cover_image(title, 'cover_image.png')

# Create the blog HTML page
path_to_new_content = utils.create_new_blog(title, blog_content, cover_image_save_path)

# Update the index.html page with a link to the new blog
utils.write_to_index(path_to_new_content)

# Push to github
utils.update_blog('Add AI generated blog post')
