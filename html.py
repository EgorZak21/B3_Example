import textwrap

# Самый простой класс TopLevelTag 
class TopLevelTag:
    # Конструктор принимает имя тега и его атрибуты (строка или кортеж/список строк)
    def __init__(self, name, **attrs):
        self.name = name
        # inner_tags - список вложенных тегов
        # TopLevelTag += InnerTag - чтобы добавить вложенный тег
        self.inner_tags = []
        self.attrs = attrs
        self.rendered = None
    
    # Переопределяем метод +=
    def __iadd__(self, inner_tag): 
        self.inner_tags.append(inner_tag)
        return self
    
    # Собираем название и атрибуты тега вместе
    def render_attrs(self):
        # Сначала идет имя тега, потом отформатированные атрибуты
        formated_atrs = [self.name]
        for attr_name ,attr_value in self.attrs.items():
            # Если значений несколько (не строка) то перечислим их через пробел
            if type(attr_value) != str:
                attr_value = " ".join(attr_value)
            # Не забываем заменить  _ на -
            attr_name = attr_name.replace('_','-')
            # Подставляем название и значение тега в строку
            formated_atrs.append('{}=\"{}\"'.format(attr_name,attr_value))
        # Превращаем список в строку, разделив пробелом
        return " ".join(formated_atrs)
    
    # Метод который создаёт код тега 
    def render(self):
        # Открытие и закрытие
        tag_open = '<{}>'.format(self.render_attrs())
        tag_close = '</{}>'.format(self.name)
        # Забираем из каждого внутреннего тега его код и объединяем в строку, разделив \n
        rendered_inner = '\n'.join([ tag.rendered for tag in self.inner_tags ])
        # Для форматирования отодвигаем вправо весь внутренний код на 4 пробела
        rendered_inner = textwrap.indent(rendered_inner,'    ')
        # Если внутреннее содержимое не пустая строка добавляем его, иначе просто открытие и закрытие тега
        if rendered_inner:
            self.rendered = '\n'.join((tag_open, rendered_inner, tag_close))
        else:
            self.rendered = tag_open + tag_close
        
    # Метод который вызывается при использовании контекстного менеджера, возвращаем сам объект
    def __enter__(self):
        return self
    
    # Метод который вызывается контекстным менеджером после выполнения блока кода
    # После всех действий с тегом и тегами, которые в него входят, можем отрендерить содержимое
    def __exit__(self, exception_type, exception_val, trace):
        self.render()

# Обертка для текстового содержимого
# Имеет только поле rendered - для удобства чтобы текст тоже рассматривался как внутренний тег
class Text:
    def __init__(self, text):
        self.rendered = text

# Наследуем от TopLevelTag
class Tag(TopLevelTag):
    # В конструкторе дополнительно запоминаем текст и is_single
    def __init__(self, name, is_single = False, text = "", **attrs):
        super().__init__(name,**attrs)
        self.is_single = is_single
        self.text = text
    
    def render(self):
        if self.is_single:
            # Если тег is_single просто рендерим его
            self.rendered = '<{}/>'.format(" ".join([self.render_attrs()]))
        else:
            # Если тег содержит текст, добавляем во внутренние теги объект класса Text
            # text.rendered - поле которое содержит текст
            # Тогда он будет обрабатываться как обычный тег
            # Вместо тега подставится нужный текст 
            # И нам не надо переписывать полностью метод render
            if self.text:
                self.inner_tags.insert(0,Text(self.text))
            super().render()

# Наследуем от TopLevelTag
# Т.к. это тоже TopLevelTag но с возможностью вывода в файл или консоль
class HTML(TopLevelTag):
    def __init__(self,output = None, **attrs):
        # Создаём тег с именем html
        super().__init__('html',**attrs)
        # Запоминаем куда выводить этот тег
        self.output = output
    
    # Метод после выполнения блока кода
    def __exit__(self, exception_type, exception_val, trace):
        # Рендерим
        self.render()
        # Если None , просто выводим в stdout (консоль)
        # Иначе в файл с именем output
        if self.output:
            with open(self.output, 'w') as file:
                file.write(self.rendered)
        else:
            print(self.rendered)

# Тест из примера (print в консоль)
if __name__ == "__main__":
    with HTML(output=None) as doc:
        with TopLevelTag("head") as head:
            with Tag("title") as title:
                title.text = "hello"
                head += title
            doc += head

        with TopLevelTag("body") as body:
            with Tag("h1", klass=("main-text",)) as h1:
                h1.text = "Test"
                body += h1

            with Tag("div", klass=("container", "container-fluid"), id="lead") as div:
                with Tag("p") as paragraph:
                    paragraph.text = "another test"
                    div += paragraph

                with Tag("img", is_single=True, src="/icon.png") as img:
                    div += img

                body += div

            doc += body