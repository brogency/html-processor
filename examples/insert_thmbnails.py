from urllib.parse import urlparse
from html_processor import (
    HtmlProcessor,
    TagRule,
)


class ImageRule(TagRule):
    tag = 'img'

    rotations = (
        1,
        1.5,
        2,
        3,
    )
    sources = (
        (1024, 1280),
        (768, 1024),
    )
    default_width = 768

    def get_new_tag(self, attributes, contents=None):
        src = attributes.get('src', '')
        parsed_url = urlparse(src)

        if parsed_url.path:
            picture = self.create_tag('picture')

            for min_screen_width, width in self.sources:
                source = self.create_sources(src, min_screen_width, width)
                picture.append(source)

            img = self.create_img(src)
            picture.append(img)

            return picture

    def create_img(self, src):
        img = self.create_tag()
        img.attrs['src'] = src
        img.attrs['srcset'] = self.build_srcset(self.default_width, src)
        img.attrs['loading'] = 'lazy'

        return img

    def create_sources(self, src, min_screen_width, width):
        source = self.create_tag('source')
        source.attrs['media'] = '(min-width: {}px)'.format(min_screen_width)
        source.attrs['srcset'] = self.build_srcset(width, src)

        return source

    def build_srcset(self, width, src):
        return ', '.join(['/{}{} {}x'.format(int(width * rotate), src, rotate) for rotate in self.rotations])

    def is_extract(self, attributes, **kwargs):
        src = attributes.get('src', '')
        parsed_url = urlparse(src)
        return False if parsed_url.path else True


def process():
    source_html = open('heroes.html').read()
    processor = HtmlProcessor(source_html, rules=[ImageRule])

    with open('enhanced-heroes.html', 'w') as file:
        file.write(repr(processor))


if __name__ == '__main__':
    process()
