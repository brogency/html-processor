from bs4.element import Comment


class Rule:
    def __init__(self, content):
        self.content = content

    def process(self):
        pass


class TagRule(Rule):
    tag = ''

    def create_tag(self, tag=None):
        tag = tag or self.tag
        return self.content.new_tag(tag)

    def get_tags(self):
        return self.content.findAll(self.tag)

    def process(self):
        tags = self.get_tags()
        for tag in tags:
            attributes = tag.attrs
            new_tag = self.get_new_tag(attributes)
            if new_tag:
                tag.replaceWith(new_tag)
            elif self.is_extract(attributes):
                tag.extract()

    def get_new_tag(self, attributes):
        tag = self.create_tag()
        tag.attrs = attributes

        return tag

    def is_extract(self, tag):
        return False


class TextRule(Rule):
    def process(self):
        html_strings = [
            html_string
            for html_string in self.content.findAll(text=True)
            if not isinstance(html_string, Comment) and self.select_string(html_string)
        ]
        for html_string in html_strings:
            string = str(html_string)
            new_string = self.get_new_string(string)
            if new_string != string:
                html_string.replace_with(new_string)

    def get_new_string(self, string):
        return string

    def select_string(self, string):
        return True
