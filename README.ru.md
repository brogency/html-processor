# HTML Processor

[![PyPI version](https://badge.fury.io/py/html-processor.svg)](https://badge.fury.io/py/html-processor)

HTML Processor - пакет, предоставляющий набор классов вокруг [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) для удобного изменения HTML.

## Ну и зачем?

Иногда возникает необходимость внесения постоянных изменений в HTML код по заданным правилам. Например, вставка ссылок на тамбнейлы для картинок, вставленных в WYSIWYG редактор. Хочется иметь возможность описывать изменения более декларативно и структурировано, нежели чем прямое описание в скриптах.

## Пример

В примере мы этим и займемся(Вставкой тамбнейлов в код за место картинок). Допустим у нас есть html, с описанием персонажей "Времени Приключений":

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

Но тут мы понимаем, что нам нужно оптимизировать изображения.
К примеру, мы поднимаем [nginx](https://nginx.org/ru/docs/http/ngx_http_image_filter_module.html), и настраиваем пути для изменения рамера изображений по следующему шаблону: ```/width/path```, где ```width``` - нужная ширина изображения, ```path``` - путь к изображению, как если бы мы запрашивали напрямую изображение.

И так, что же нам нужно сделать?
Нам нужно заменить такой код:

```html
<img src="/media/images/heroes/Jake.jpeg" />
```

вот на такой:

```html
<picture>
    <source media="(min-width: 1024px)" srcset="/1280/media/images/heroes/Jake.jpeg 1x, /1920/media/images/heroes/Jake.jpeg 1.5x, /2560/media/images/heroes/Jake.jpeg 2x, /3840/media/images/heroes/Jake.jpeg 3x">
    <source media="(min-width: 768px)" srcset="/1024/media/images/heroes/Jake.jpeg 1x, /1536/media/images/heroes/Jake.jpeg 1.5x, /2048/media/images/heroes/Jake.jpeg 2x, /3072/media/images/heroes/Jake.jpeg 3x">
    <img loading="lazy" src="/media/images/heroes/Jake.jpeg" srcset="/768/media/images/heroes/Jake.jpeg 1x, /1152/media/images/heroes/Jake.jpeg 1.5x, /1536/media/images/heroes/Jake.jpeg 2x, /2304/media/images/heroes/Jake.jpeg 3x" />
</picture>
```

Так же нам необходимо удалить изображения, источник которого не является ссылкой.

При этом мы не должны привязываться конкретно к этому изображению и к этому месту на странице.

Начнем. Для начала нам нужно создать базовое правило, которое будет работать для всех изображений на странице:

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

Если сейчас мы запустим скрипт, ты увидим, что ничего не изменилось(Ну кроме, разве что, форматирования).

Всё потому, что мы не описали, как мы должны изменять теги изображений. Давайте сделаем это:


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

Здесь мы переопредели метод ```get_new_tag```. Этот метод вызывается для всех тегов, определенных в атрибуте ```TagRule.tag```, из которого можете вернуть новый тег ```bs4.Tag```, на который будет заменен найденный тег. Если мы возвращаем ```None```, то с тегом ни его не происходит.
Давайте запустим скрипт, и посмотрим результат:

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

И так, мы видим, что изображения заменились на теги с использованием медиа запросов и ссылками на тамбнейлы, но у нас остались теги изображений, которые не ссылаются на сами изображения.
Давайте исправим это:

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

Мы сделали две вещи:

* Возвращаем значение из метода ```get_new_tag``` только в том случае, если ссылка в атрибуте ```src``` содержит путь.
* Переопределили метод ```is_extract```, который возвращает ```True```, если ссылки в параметре ```src``` нет пути. Данный метод отвечает за извлечение тега из html. Если он возвращает ```True```, то тег будет извлечен, если ```False```, то с тегом не будет произведено никаких действий. Метод ```is_extract``` вызывается только в том случае, если метод ```get_new_tag``` ничего не вернул.

И так, запустим скрипт и получим следующий результат:

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

Это то, чего мы хотели. Подробнее ознакомится с примером можно в ```examples/insert_thumbnails.py```.

## АПИ

### HtmlProcessor

Класс процессора, который запускает правила обработки html.
Задать правила обработки html можно, создав класс потомок и переопределив атрибут ```rules```, например:

```python
class TextProcessor(HtmlProcessor):
    rules = [
        AdventureTextRule,
    ]
```

Так же правила можно задать через конструктор.

* __init__(html: string, rules: List[Rule] = None, unqoute: bool = False) - конструтор принимает строку с html кодом. Так же в него можно передать правила обработки, как список объектов класса ```Rule```, и флаг - стоит ли применять к html строке экранирование через метод ```urllib.parse.unqoute```.

Обработанный контент можно получить из процессора тремя способами:
* Вызов метода ```process```. Данный метод вернет объект ```BeautifulSoup``` библиотеки ```bs4```.
* str(processor). Данный вызов вернет строку с обработанным и неотформатированным html кодом.
* repr(processor). Данный вызов вернет строку с обработанным и отформатированным html кодом.


### Rule

Базовый класс для описания правила обработки html кода.

### Создание кастомного правила

Объекты ```Rule``` содержат атрибут ```content```, в котором содержится объект ```BeautifulSoup```, созданый из исходного html кода.

Для создания своих правил, у класса, унаследованного от ```Rule``` обязательно должен быть переопределен метод:

* process() - данный метод вызывается для обработки объекта ```Rule.content```.

Так же для удобства Вы можете переопределить следующие методы:

* get_area - Возвращает область, в которой происходит поиск объектов. Область выбирается из атрибута ```content```.
* select(area: BeautifulSoup) - Возвращает объекты, которые нам необходимо обработать.
* select_element(element) - Возвращает ```True```, если объект подходит для обработки и ```False```, если не подходит.

Данные методы нужны для того, что бы метод ```Rule.get_elements```, возвращал необходимые для обработки элементы.

Подробнее рассмотреть создание правил можно на примере классов предопределенных правил, например ```TagRule``` и ```TextRule```.

### Предопределенные правила

#### TagRule

Правило обработки конкретного тега.
Для задания правила, необходимо создать класс, унаследованный от ```TagRule``` и определить атрибут ```tag```, который принимает название тега в виде строки, например ```tag = 'img'```.

Для работы с тегом предусмотрено два метода, которые можно переопределить:

* get_new_tag(self, attributes: dict, contents=None) - Метод принимает словарь атрибутов ```attributes```, а так же содержимое тега ```contents```. Метод вызывается для каждого найденного тега. Метод должен возвращать ```None```, если мы не хотим менять тег, или новый тег ```bs4.Tag```, который заменить текущий тег.
* is_extract(self, attributes: dict, contents=None) - Метод принимает словарь атрибутов ```attributes```, а так же содержимое тега в ```contents```. Метод возвращает ```True```, если тег необходимо извлечь из html, или ```False```, если с тегом не нужно ничего делать. Метод вызывается только в том случае, если для данного тего ни чего не вернул метод ```get_new_tag```.

#### TextRule

Правило для обработки текстов внутри html.
Для задания правила, необходимо создать класс, унаследованный от ```TextRule```.

Для обработки строки предусмотрены следующие методы.

* get_new_string(self, string: str) - принимает строку и возвращает новую, на которую нужно заменить найденную строку.
* is_extract(self, string: str) - принимает строку и возвращает ```True```, если элемент с этой строкой необходимо удалить из html, или ```False```, если оставить. Удаляется на сама строка, а тег, который эту строку содержит, а так же, содержимое этого тега.
