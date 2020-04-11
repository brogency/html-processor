# HTML Processor

[![PyPI version](https://badge.fury.io/py/html-processor.svg)](https://badge.fury.io/py/html-processor)

HTML Processor - a package that provides a set of classes around [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for easy HTML modification.

## Well, what for?

Sometimes it is necessary to make constant changes in HTML code according to specified rules. For example, it is necessary to insert links to thumbnails for images inserted into WYSIWYG editor. It would be desirable to be able to describe changes in a more declarative and structured way, rather than write simple scripts.

## Example

In the example we will do it (Inserting thumbnails in the code for pictures). Let's say we have html, with a description of the characters of "Adventure Time":

```html
<html>
  <head>
    <title>Heroes of Ooo</title>
  </head>
  <body>
    <header>
      <h1>
        Heroes of Ooo
      </h1>
      <img src="" />
    </header>
    <main>
      <img alt="Delete me" src="#" />
      <article>
        <figure>
          <img alt="Finn Mertens" src="/media/images/heroes/Finn.jpeg" />
          <figcaption>
            Finn Mertens
          </figcaption>
        </figure>
        <div>
          <p>
            Finn Mertens (simply known as Finn the Human and formerly known as
            Pen in the original short) the main protagonist of the Cartoon
            Network series Adventure Time.
          </p>
          <p>
            He was voiced by Jeremy Shada, who also voice as Lance from Voltron:
            Legendary Defender and Cody Maverick in Surf's Up: Wavemania.
          </p>
        </div>
      </article>
      <article>
        <figure>
          <img alt="Jake the Dog" src="/media/images/heroes/Jake.jpeg" />
          <figcaption>
            Jake the Dog
          </figcaption>
        </figure>
        <div>
          <p>
            Jake is the deuteragonist of Adventure Time. He's a magical dog and
            Finn's constant companion, best friend and adoptive brother. Jake
            has shape shifting abilities so he can "stretch" into different
            objects.
          </p>
          <p>
            He was voiced by John DiMaggio, who also voiced as Fu Dog from
            American Dragon: Jake Long.
          </p>
        </div>
      </article>
    </main>
  </body>
</html>
```

We understand that we need to optimize the images.
For example, we use [nginx](https://nginx.org/ru/docs/http/ngx_http_image_filter_module.html). We set up paths to change the image frame in the following template: ```/width/path```, where ```width``` - image width, ```path``` -  image path.

We need to replace that code:

```html
<img src="/media/images/heroes/Jake.jpeg" />
```

with the next:

```html
<picture>
    <source media="(min-width: 1024px)" srcset="/1280/media/images/heroes/Jake.jpeg 1x, /1920/media/images/heroes/Jake.jpeg 1.5x, /2560/media/images/heroes/Jake.jpeg 2x, /3840/media/images/heroes/Jake.jpeg 3x">
    <source media="(min-width: 768px)" srcset="/1024/media/images/heroes/Jake.jpeg 1x, /1536/media/images/heroes/Jake.jpeg 1.5x, /2048/media/images/heroes/Jake.jpeg 2x, /3072/media/images/heroes/Jake.jpeg 3x">
    <img loading="lazy" src="/media/images/heroes/Jake.jpeg" srcset="/768/media/images/heroes/Jake.jpeg 1x, /1152/media/images/heroes/Jake.jpeg 1.5x, /1536/media/images/heroes/Jake.jpeg 2x, /2304/media/images/heroes/Jake.jpeg 3x" />
</picture>
```

We also need to remove images, the source of which is not a link.

In doing so, we should not be tied specifically to this image and to this location on the page.

Let's get started. First we need to create a basic rule that will work for all images on the page:

```python
from html_processor import (
    HtmlProcessor,
    TagRule,
)


class ImageRule(TagRule):
    tag = 'img'


def process():
    source_html = open('heroes.html').read()
    processor = HtmlProcessor(source_html, rules=[ImageRule])

    with open('enhanced-heroes.html', 'w') as file:
        file.write(repr(processor))


if __name__ == '__main__':
    process()
```

If we run the script now, you will see that nothing has changed (except the formatting).

That's because we didn't describe how we should change the image tags. Let's do this:


```python
...
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
...
```

We overridden the method ```get_new_tag```. This method is called for all tags defined in the attribute ```TagRule.tag```, from which you can return a new tag ```bs4.Tag```, which will replace the tag found. If we return ```None```, the tag found does not change.

```html
...
    <header>
        <h1>
        Heroes of Ooo
        </h1>
        <picture>
            <source media="(min-width: 1024px)" srcset="/1280 1x, /1920 1.5x, /2560 2x, /3840 3x"/>
            <source media="(min-width: 768px)" srcset="/1024 1x, /1536 1.5x, /2048 2x, /3072 3x"/>
            <img loading="lazy" src="" srcset="/768 1x, /1152 1.5x, /1536 2x, /2304 3x"/>
        </picture>
   </header>
...
    <figure>
        <picture>
            <source media="(min-width: 1024px)" srcset="/1280/media/images/heroes/Finn.jpeg 1x, /1920/media/images/heroes/Finn.jpeg 1.5x, /2560/media/images/heroes/Finn.jpeg 2x, /3840/media/images/heroes/Finn.jpeg 3x"/>
            <source media="(min-width: 768px)" srcset="/1024/media/images/heroes/Finn.jpeg 1x, /1536/media/images/heroes/Finn.jpeg 1.5x, /2048/media/images/heroes/Finn.jpeg 2x, /3072/media/images/heroes/Finn.jpeg 3x"/>
            <img loading="lazy" src="/media/images/heroes/Finn.jpeg" srcset="/768/media/images/heroes/Finn.jpeg 1x, /1152/media/images/heroes/Finn.jpeg 1.5x, /1536/media/images/heroes/Finn.jpeg 2x, /2304/media/images/heroes/Finn.jpeg 3x"/>
        </picture>
        <figcaption>
            Finn Mertens
        </figcaption>
    </figure>
...
    <figure>
        <picture>
            <source media="(min-width: 1024px)" srcset="/1280/media/images/heroes/Jake.jpeg 1x, /1920/media/images/heroes/Jake.jpeg 1.5x, /2560/media/images/heroes/Jake.jpeg 2x, /3840/media/images/heroes/Jake.jpeg 3x"/>
            <source media="(min-width: 768px)" srcset="/1024/media/images/heroes/Jake.jpeg 1x, /1536/media/images/heroes/Jake.jpeg 1.5x, /2048/media/images/heroes/Jake.jpeg 2x, /3072/media/images/heroes/Jake.jpeg 3x"/>
            <img loading="lazy" src="/media/images/heroes/Jake.jpeg" srcset="/768/media/images/heroes/Jake.jpeg 1x, /1152/media/images/heroes/Jake.jpeg 1.5x, /1536/media/images/heroes/Jake.jpeg 2x, /2304/media/images/heroes/Jake.jpeg 3x"/>
        </picture>
        <figcaption>
            Jake the Dog
        </figcaption>
    </figure>
...
```

You may notice that the images have been replaced with tags using media queries and tambneiles links. But we still have the tags of images that do not refer to the images themselves.
Let's fix this:

```python
from urllib.parse import urlparse
...
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
...
    def is_extract(self, attributes, **kwargs):
        src = attributes.get('src', '')
        parsed_url = urlparse(src)
        return False if parsed_url.path else True
```

What we've changed:

* We return a value from the ```get_new_tag``` method only if the link in the ```src``` attribute contains a path.
* Override method ```is_extract```, which returns ```True``` if there is no path referenced in parameter ```src```. This method is responsible for extracting the tag from html. If it returns ```True``` the tag will be extracted, if ```False```, no action will be taken with the tag. ```is_extract```  is only called if method ```get_new_tag``` has not returned anything.

So, let's run the script and get the next result:

```html
<html>
 <head>
  <title>
   Heroes of Ooo
  </title>
 </head>
 <body>
  <header>
   <h1>
    Heroes of Ooo
   </h1>
  </header>
  <main>
   <article>
    <figure>
     <picture>
      <source media="(min-width: 1024px)" srcset="/1280/media/images/heroes/Finn.jpeg 1x, /1920/media/images/heroes/Finn.jpeg 1.5x, /2560/media/images/heroes/Finn.jpeg 2x, /3840/media/images/heroes/Finn.jpeg 3x"/>
      <source media="(min-width: 768px)" srcset="/1024/media/images/heroes/Finn.jpeg 1x, /1536/media/images/heroes/Finn.jpeg 1.5x, /2048/media/images/heroes/Finn.jpeg 2x, /3072/media/images/heroes/Finn.jpeg 3x"/>
      <img loading="lazy" src="/media/images/heroes/Finn.jpeg" srcset="/768/media/images/heroes/Finn.jpeg 1x, /1152/media/images/heroes/Finn.jpeg 1.5x, /1536/media/images/heroes/Finn.jpeg 2x, /2304/media/images/heroes/Finn.jpeg 3x"/>
     </picture>
     <figcaption>
      Finn Mertens
     </figcaption>
    </figure>
    <div>
     <p>
      Finn Mertens (simply known as Finn the Human and formerly known as            Pen in the original short) the main protagonist of the Cartoon            Network series Adventure Time.
     </p>
     <p>
      He was voiced by Jeremy Shada, who also voice as Lance from Voltron:            Legendary Defender and Cody Maverick in Surf's Up: Wavemania.
     </p>
    </div>
   </article>
   <article>
    <figure>
     <picture>
      <source media="(min-width: 1024px)" srcset="/1280/media/images/heroes/Jake.jpeg 1x, /1920/media/images/heroes/Jake.jpeg 1.5x, /2560/media/images/heroes/Jake.jpeg 2x, /3840/media/images/heroes/Jake.jpeg 3x"/>
      <source media="(min-width: 768px)" srcset="/1024/media/images/heroes/Jake.jpeg 1x, /1536/media/images/heroes/Jake.jpeg 1.5x, /2048/media/images/heroes/Jake.jpeg 2x, /3072/media/images/heroes/Jake.jpeg 3x"/>
      <img loading="lazy" src="/media/images/heroes/Jake.jpeg" srcset="/768/media/images/heroes/Jake.jpeg 1x, /1152/media/images/heroes/Jake.jpeg 1.5x, /1536/media/images/heroes/Jake.jpeg 2x, /2304/media/images/heroes/Jake.jpeg 3x"/>
     </picture>
     <figcaption>
      Jake the Dog
     </figcaption>
    </figure>
    <div>
     <p>
      Jake is the deuteragonist of Adventure Time. He's a magical dog and            Finn's constant companion, best friend and adoptive brother. Jake            has shape shifting abilities so he can "stretch" into different            objects.
     </p>
     <p>
      He was voiced by John DiMaggio, who also voiced as Fu Dog from            American Dragon: Jake Long.
     </p>
    </div>
   </article>
  </main>
 </body>
</html>
```

This is what we wanted. You can find out more about the example in ```examples/insert_thumbnails.py```.

## API

### HtmlProcessor

The class of processor that starts the html processing rules.
You can set the rules of html processing by creating a descendant class and overriding the attribute ```rules```, for example:

```python
class TextProcessor(HtmlProcessor):
    rules = [
        AdventureTextRule,
    ]
```
The same rules can be set through the constructor:

* __init__(html: string, rules: List[Rule] = None, unqoute: bool = False) - конструтор принимает строку с html кодом. Так же в него можно передать правила обработки, как список объектов класса ```Rule```, и флаг - стоит ли применять к html строке экранирование через метод ```urllib.parse.unqoute```.

Processed content can be obtained from the processor in 3 ways:
* Call ```process``` method. This method will return the object ```bs4.BeautifulSoup```.
* str(processor). This call will return a string with processed and unformatted html code.
* repr(processor). This call will return a string with processed and formatted html code.


### Rule

Base class for describing the html code processing rule.

### Creating a custom rule

```Rule``` objects contain an attribute ```content``` that contains an object ```BeautifulSoup``` created from the source html code.

To create its own rules, a class inherited from ```Rule``` the method must be overridden:

* process() - this method is called to process the object ```Rule.content```.

You can also override the following methods for convenience:

* get_area - returns the area where objects are searched for. The area is selected from the attribute ```content```.
* select(area: BeautifulSoup) - returns the objects that we need to process.
* select_element(element) - returns ```True``` if the object is suitable for processing and ```False``` if not.

These methods are needed to make the method ```Rule.get_elements``` returned the elements needed for processing.

The creation of rules can be seen in more detail on the example of predefined rule classes, for example ```TagRule``` and ```TextRule```.

### Predetermined rules

#### TagRule

A rule to process a specific tag.
To specify a rule, you need to create a class inherited from ```TagRule``` and define an attribute  ```tag``` that takes the tag name as a string, for example ```tag = 'img'```.

There are 2 methods for working with a tag that can be overridden:

* get_new_tag(self, attributes: dict, contents=None) - the method accepts attribute dictionary  ```attributes```, as well as the content of the tag ```contents```. The method is called for each tag found. The method must return ```None``` if we do not want to change the tag, or a new tag  ```bs4.Tag```, which will replace the current tag.
* is_extract(self, attributes: dict, contents=None) - The method accepts attribute dictionary ```attributes```, as well as the content of the tag in ```contents```. The method returns ```True``` if the tag needs to be extracted from html, or ```False``` if nothing needs to be done with the tag. The method is called only if ```get_new_tag```  has not returned anything for the given tag.

#### TextRule

A rule for processing texts inside html.
To set a rule, you should create a class inherited from ```TextRule```.

The following methods are available for string processing.

* get_new_string(self, string: str) - takes a string and returns a new string to replace the found one.
* is_extract(self, string: str) - accepts the string and returns ```True``` if the item with this string must be removed from html, or ```False``` if left. Removed by the string itself, and the tag that this string contains, as well as the content of this tag.
