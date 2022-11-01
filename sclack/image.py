import subprocess

import urwid
from logzero import logger

color_list = [
    "black",
    "dark red",
    "dark green",
    "brown",
    "dark blue",
    "dark magenta",
    "dark cyan",
    "light gray",
    "dark gray",
    "light red",
    "light green",
    "yellow",
    "light blue",
    "light magenta",
    "light cyan",
    "white",
]


def ansi_to_urwid(ansi_text):
    result = []
    ansi_text = ansi_text.decode("utf-8")
    for instruction in ansi_text.split("\x1B["):
        try:
            attr, text = instruction.split("m", 1)
        except Exception:
            attr = "0"
            text = instruction.split("m", 1)
        attr_list = [int(code) for code in attr.split(";")]
        attr_list.sort()
        foreground = -1
        background = -1
        for attr in attr_list:
            if attr <= 29:
                pass
            elif attr <= 37:
                foreground = attr - 30
            elif attr <= 47:
                background = attr - 40
            elif attr <= 94:
                foreground = foreground + 8
            elif attr >= 100 and attr <= 104:
                background = background + 8
        foreground = color_list[foreground]
        background = color_list[background]
        result.append((urwid.AttrSpec(foreground, background), text))
    return result


class ANSICanvas(urwid.canvas.Canvas):
    def __init__(self, size, text_lines, width):
        super().__init__()

        self.text_lines = text_lines
        self._width = width

    def cols(self):
        return self._width

    def rows(self):
        return len(self.text_lines)

    def content(
        self,
        trim_left=0,
        trim_top=0,
        cols=None,
        rows=None,
        attr_map=None,
    ):
        assert cols is not None
        assert rows is not None

        for i in range(rows):
            if i < len(self.text_lines):
                text = self.text_lines[i].encode("utf-8")
            else:
                text = b""

            padding = bytes().rjust(max(0, cols - len(text)))
            line = [(None, "U", text + padding)]

            yield line


class ANSIWidget(urwid.Widget):
    # _sizing = frozenset([urwid.widget.BOX])
    _sizing = frozenset([urwid.widget.FIXED])

    def __init__(self, text, width):
        self.lines = text.split("\n")
        self._width = width

    def set_content(self, lines):
        self.lines = lines
        self._invalidate()

    def render(self, size, focus=False):
        canvas = ANSICanvas(size, self.lines, self._width)

        return canvas

    def pack(self, size=None, focus=False):
        rows = len(self.lines)
        cols = self._width
        return (cols, rows)


def img_to_ansi(path, width=None, height=None):
    command = ["chafa", "-f", "symbols"]
    explicit_width = width is not None
    explicit_height = height is not None
    if explicit_width:
        width = int(width)
    if explicit_height:
        height = int(height)
    if explicit_width and not explicit_height:
        command.extend(["--size", "{}x".format(width)])
    elif not explicit_width and height:
        command.extend(["--size", "x{}".format(height)])
    elif explicit_width and explicit_height:
        command.extend(["--size", "{}x{}".format(width, height)])
    command.append(path)
    logger.info("command: {}".format(command))
    try:
        ansi_text = subprocess.check_output(command, stderr=subprocess.STDOUT).decode(
            "utf-8"
        )
        logger.info("ANSI text length: {}".format(len(ansi_text)))
    except Exception as ex:
        ansi_text = None
        logger.exception(ex)
        logger.error(ex.output)
    return ansi_text
