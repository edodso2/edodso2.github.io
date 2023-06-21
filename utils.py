import os
import shutil
import requests
import openai
from git import Repo
from pathlib import Path
from bs4 import BeautifulSoup as Soup

openai.api_key = os.getenv('OPENAI_API_KEY')

PATH_TO_BLOG = Path(os.getcwd())
PATH_TO_BLOG_REPO = PATH_TO_BLOG/'.git'
PATH_TO_CONTENT = PATH_TO_BLOG/'content'

PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

# Push the code to github
def update_blog(commit_message='Updates blog'):
    # Reports repository location to GitPython
    repo = Repo(PATH_TO_BLOG_REPO)

    # Git Add
    repo.git.add(all=True)

    # Git Commit
    repo.index.commit(commit_message)

    # Git Push
    origin = repo.remote(name='origin')
    origin.push()

# Create a new html file for the blog
def create_new_blog(title, content, cover_image):
    cover_image = Path(cover_image)

    files = len(list(PATH_TO_CONTENT.glob('*.html')))
    new_title = f'{files+1}.html'
    path_to_new_content = PATH_TO_CONTENT/new_title

    if not os.path.exists(path_to_new_content):
        # Write new file
        with open(path_to_new_content, 'w') as f:
          f.write('<!DOCTYPE html>\n')
          f.write('<html>\n')
          f.write('<head>\n')
          f.write(f'<title> {title} </title>\n')
          f.write('</head>\n')
          
          f.write('<body>\n')
          f.write(f'<img src=\'{cover_image.name}\' alt=\'Cover Image\'> <br />\n')
          f.write(f'<h1> {title} </h1>')
          f.write(content.replace('\n', '<br />\n'))
          f.write('</body>\n')
          f.write('</html>\n')
          print('Blog created')
          return path_to_new_content
    else:
        raise FileExistsError('File already exists.')

# Check for duplicate blog links
def check_for_duplicate_links(path_to_new_content, links):
    urls = [str(link.get('href')) for link in links]
    content_path = str(Path(*path_to_new_content.parts[-2:]))
    return content_path in urls

# Create the new blog link in the index.html file
def write_to_index(path_to_new_content):
    with open(PATH_TO_BLOG/'index.html') as index:
      soup = Soup(index.read(), features='html.parser')
    
    links = soup.find_all('a')
    last_link = links[-1]

    if check_for_duplicate_links(path_to_new_content, links):
        raise ValueError('Link already exists')
      
    link_to_new_blog = soup.new_tag('a', href=Path(*path_to_new_content.parts[-2:]))
    link_to_new_blog.string = path_to_new_content.name.split('.')[0]
    last_link.insert_after(link_to_new_blog)
    
    with open(PATH_TO_BLOG/'index.html', 'w') as f:
        f.write(str(soup.prettify(formatter='html')))

# Create prompt for openai. Be sure to give a biography
# so openai will make the post more accurate.
def create_prompt(title, tags, summary):
    prompt = '''
    Biography:
    My name is Eric and I am a software engineer.

    Blog:
    Title: {}
    Tags: {}
    Summary: {}
    Full Text: '''.format(title, tags, summary)
    return prompt

# Call openai to generate a blog post
def get_blog_from_openai(title, tags, summary):
    response = openai.Completion.create(engine='text-davinci-003',
                                            prompt=create_prompt(title, tags, summary),
                                            max_tokens=512, # more tokens for longer post
                                            temperature=0.7)
    return response['choices'][0]['text']

# Create the Dalle2 prompt.
# TODO: work on prompt to get better images
def dalle2_prompt(title):
    prompt = f'Pixel art abstract for \'{title}\'.'
    return prompt

# Save image to the content folder
def save_image(image_url, file_name):
    image_res = requests.get(image_url, stream = True)
    
    if image_res.status_code == 200:
        with open(PATH_TO_CONTENT/file_name, 'wb') as f:
            shutil.copyfileobj(image_res.raw, f)
    else:
        print('Error downloading image!')
    return image_res.status_code, file_name

# Call Dalle2 to generate a blog image
def get_cover_image(title, save_path):
    response = openai.Image.create(
        prompt=dalle2_prompt(title),
        n=1,
        size='1024x1024'
        )
    image_url = response['data'][0]['url']
    status_code, file_name = save_image(image_url, save_path)
    return status_code, file_name
