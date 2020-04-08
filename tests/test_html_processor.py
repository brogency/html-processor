from os.path import (
    join,
    dirname,
)
from bs4 import BeautifulSoup
from html_processor import (
    __version__,
    HtmlProcessor,
    Rule,
    TagRule,
    TextRule,
)


ASSETS_PATH = join(dirname(dirname(__file__)), 'assets')
SOURCE_HTML = join(ASSETS_PATH, 'source.html')
PURPOSE_HTML = join(ASSETS_PATH, 'purpose.html')
PURPOSE_TAG_HTML = join(ASSETS_PATH, 'purpose-tag.html')
PURPOSE_TEXT_HTML = join(ASSETS_PATH, 'purpose-text.html')


class AdventureTextRule(TextRule):
    def get_new_string(self, string: str):
        return string.replace('BORING', 'ADVENTURE')

    def is_extract(self, string):
        return string == 'Batman is here!'


class ImageSourceRule(TagRule):
    tag = 'img'

    def get_new_tag(self, attributes, **kwargs):
        if not attributes.get('data-content'):
            src = attributes.get('data-src')
            tag = self.create_tag()
            tag.attrs['src'] = src
            return tag

    def is_extract(self, attributes):
        return attributes.get('data-content') == 'delete me'


class TextProcessor(HtmlProcessor):
    rules = [
        AdventureTextRule,
    ]


class TagProcessor(HtmlProcessor):
    rules = [
        ImageSourceRule,
    ]


class Processor(HtmlProcessor):
    rules = [
        AdventureTextRule,
        ImageSourceRule,
    ]


def test_version():
    assert __version__ == '0.0.4'


def test_text():
    source_html = open(SOURCE_HTML).read()
    processor = TextProcessor(source_html)
    purpose_html = _get_html(PURPOSE_TEXT_HTML)
    processed_html = repr(processor)

    assert processed_html == purpose_html


def test_tag():
    source_html = open(SOURCE_HTML).read()
    processor = TagProcessor(source_html)
    purpose_html = _get_html(PURPOSE_TAG_HTML)
    processed_html = processor.__repr__()

    assert processed_html == purpose_html


class EmptyTagRule(TagRule):
    tag = 'div'


def test_empty_rules():
    source_html = open(SOURCE_HTML).read()
    processor = HtmlProcessor(source_html, rules=[
        Rule,
        EmptyTagRule,
        TextRule,
    ])

    purpose_html = _get_html(SOURCE_HTML)
    processed_html = repr(processor)

    assert processed_html == purpose_html


def test_all():
    source_html = open(SOURCE_HTML).read()
    processor = Processor(source_html)

    assert bool(BeautifulSoup(str(processor), 'html.parser').find()) == True

    purpose_html = _get_html(PURPOSE_HTML)
    processed_html = repr(processor)

    assert processed_html == purpose_html


def _get_html(path):
    html = open(path).read()
    return BeautifulSoup(html.replace('\n', ''), 'html.parser').prettify()
