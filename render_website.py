import argparse
import json
import math
import os
from urllib.parse import urlsplit

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


DEFAULT_FILE_FOLDER = 'media/'
DEFAULT_PAGE_FOLDER = 'pages/'
LIBRARY_JSON_PATH = os.path.join(DEFAULT_FILE_FOLDER, 'library.json')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Script for developing an online library'
    )
    default_file_folder = DEFAULT_FILE_FOLDER
    default_page_folder = DEFAULT_PAGE_FOLDER
    parser.add_argument(
        '-f',
        '--file_folder',
        help='media directory path',
        type=str,
        default=default_file_folder
    )
    parser.add_argument(
        '-p',
        '--page_folder',
        help='path to the folder with the pages',
        type=str,
        default=default_page_folder
    )
    args = parser.parse_args()
    return args.file_folder, args.page_folder


def on_reload():
    load_dotenv()
    file_folder, page_folder = parse_arguments()
    os.makedirs(page_folder, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    library_path = LIBRARY_JSON_PATH

    with open(library_path, 'r', encoding='utf8') as my_file:
        library = json.load(my_file)
    for book in library:
        image_link = urlsplit(book['image_link'])
        book['image_link'] = image_link.path.split('/')[2]
        book['book_path'] = os.path.join(f"{book['book_name']}.txt")

    quantity_books_on_page = 10
    columns = 2
    pages = chunked(library, quantity_books_on_page)
    quantity_pages = math.ceil(len(library) / quantity_books_on_page)
    for page_number, page in enumerate(pages, 1):
        rendered_page = template.render(library=chunked(page, columns),
                                        quantity_pages=quantity_pages,
                                        page_number=page_number)
        page_path = os.path.join(page_folder, f'index{page_number}.html')
        with open(page_path, 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()