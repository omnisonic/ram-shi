import requests
import os
from markdownify import markdownify as md
from dotenv import load_dotenv
from bs4 import BeautifulSoup


# Load environment variables from .env file
load_dotenv()

# Load constants from environment variables
BLOG_ID = os.getenv('BLOG_ID')  # Environment variable for Blog ID
API_KEY = os.getenv('API_KEY')  # Environment variable for API Key

OUTPUT_DIR = 'content'  # Output directory for markdown files

def fetch_posts(blog_id, api_key):
    posts = []
    next_page_token = None
    
    while True:
        url = f'https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?key={api_key}'
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Append the items to the posts list
        posts.extend(data.get('items', []))
        
        # Break if there's no nextPageToken
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    
    return posts

def create_markdown_file(post, output_dir):
    title = post.get('title')
    content = post.get('content', '')  # Default to empty string if no content
    published = post.get('published')
    post_id = post.get('id')
    post_url = post.get('url')

    # Convert HTML content to Markdown
    markdown_content = md(content)

    # Extract the first image for the summary
    soup = BeautifulSoup(content, 'html.parser')
    first_image = soup.find('img')

    # Prepare the summary in the specified Markdown format
    if first_image and 'src' in first_image.attrs:
        image_src = first_image['src']
        summary = f'![image]({image_src} "Image summary")'  # Markdown syntax for image
    else:
        summary = ''  # No image found, keep summary empty

    # Prepare the Markdown file content
    markdown_file_content = (
        f'Title: {title}\n'
        f'Date: {published}\n'
        f'Summary: {summary}\n\n'
        f'Blogger_Post_URL: {post_url}\n'
        f'Post ID: {post_id}\n'
        f'{markdown_content}'
    )


    # Format: Use a safe title for the filename
    safe_title = title.replace(' ', '_').replace('/', '-') 
    filename = f"{output_dir}/{safe_title}.md"

    # Write the content to a markdown file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_file_content)

def main():
    # Fetch posts from Blogger API
    posts = fetch_posts(BLOG_ID, API_KEY)

    # Iterate over posts and create markdown files
    for post in posts:
        create_markdown_file(post, OUTPUT_DIR)

    print(f"Successfully created {len(posts)} markdown files in '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()
