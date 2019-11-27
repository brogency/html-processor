from urllib.parse import unquote
from bs4 import BeautifulSoup


class HtmlProcessor:
    rules = []
    processed_content = None

    def __init__(self, content, rules=None, unquote=False):
        self.unquote = unquote
        self.raw_content = content
        if rules:
            self.rules.extend(rules)

    def clear_content(self, content):
        cleared_content = content.replace('\n', '')
        return unquote(cleared_content) if self.unquote else cleared_content

    def process(self):
        content = BeautifulSoup(
            self.clear_content(self.raw_content),
            'html.parser',
        )
        for create_rule in self.rules:
            rule = create_rule(content)
            rule.process()
        return content

    def __repr__(self):
        return self.process().prettify()

    def __str__(self):
        return str(self.process())
