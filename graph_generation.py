from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

MIN_GRAPH_WIDTH = 720
MIN_GRAPH_HEIGHT = 480

MAX_GRAPH_WIDTH = 7680
MAX_GRAPH_HEIGHT = 4320

DOT_SIZE = 10
STROKE_SIZE_GRID = 1
STROKE_SIZE_CONNECTION = 2

BLACK = (0, 0, 0)
GRAY = (191, 189, 182)
LIGHT_GRAY = (207, 204, 196)

FONT_SIZE = 16
FONT_SIZE_HEADER = 26

FONT_PATH = "assets/roboto-v30-latin-regular.ttf"

PADDING = 30

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
font_header = ImageFont.truetype(FONT_PATH, FONT_SIZE_HEADER)


def _rotated_text(
    text: str,
    /,
    rotation: int = 90,
    font: ImageFont.FreeTypeFont = font,
    color: tuple = BLACK,
):
    txt = _text(text, font=font, color=color)
    rotated = txt.rotate(rotation, expand=1)
    return rotated.crop(rotated.getbbox())


def _text(text: str, /, font: ImageFont.FreeTypeFont = font, color: tuple = BLACK):
    txt = Image.new("RGBA", (MAX_GRAPH_WIDTH, FONT_SIZE_HEADER * 2), color=(*BLACK, 0))
    draw = ImageDraw.Draw(txt)
    draw.text((0, 0), text, font=font, fill=(*color, 255))
    return txt.crop(txt.getbbox())


def generate_entry_pos(data, i, graph_offset_x, graph_offset_y, distance_x, distance_y):
    entry = data[i]
    x = graph_offset_x + distance_x * i + (0.5 * distance_x)
    y = graph_offset_y + distance_y * (entry - min(data)) + (0.5 * distance_y)

    return (x, y)


def generate_graph(
    labels: list[str],
    data: list[int],
    width: int,
    height: int,
    header: str,
    footer: str,
) -> BytesIO:
    image = Image.new("RGB", (width, height), "white")

    header = _text(header, font=font_header)
    header_height = header.height + 2 * PADDING

    footer = _text(footer, color=LIGHT_GRAY)
    footer_height = footer.height + PADDING

    data = list(reversed(data))

    if len(data) > 0:
        label_imgs = [_rotated_text(label, rotation=90) for label in labels]
        label_height = max([img.height for img in label_imgs]) + 2 * PADDING

        data_difference = max(data) - min(data)
        data_y_labels = list(
            reversed(
                [_text(str(min(data) + i)) for i in range(round(data_difference) + 1)]
            )
        )

        y_label_width = max([t.width for t in data_y_labels])
        y_label_heigh = max([t.height for t in data_y_labels])

    else:
        y_label_width = 0
        label_height = PADDING

    graph_offset_x = 2 * PADDING + y_label_width
    graph_offset_y = header_height

    graph_height = height - header_height - label_height - footer_height
    graph_width = width - PADDING - graph_offset_x

    draw = ImageDraw.Draw(image)

    if len(data) > 0:
        # ----------------------------- If data available ---------------------------- #

        y_labels_every_nth = 1
        if graph_height / (y_label_heigh * 1.5) < len(data_y_labels):
            y_labels_every_nth = int(
                len(data_y_labels) / (graph_height / (y_label_heigh * 1.5))
            )
        data_y_labels = [
            y for i, y in enumerate(data_y_labels) if i % y_labels_every_nth == 0
        ]

        # ------------------------- Vertical (y-axis) labels ------------------------- #
        distance_y = graph_height / (data_difference + 1)
        _distance_y = graph_height / len(data_y_labels)
        for i, y in enumerate(data_y_labels):
            offset = _distance_y * i + (0.5 * _distance_y)
            line_y = graph_offset_y + offset

            draw.line(
                (graph_offset_x, line_y, graph_offset_x + graph_width, line_y),
                LIGHT_GRAY,
                STROKE_SIZE_GRID,
            )
            image.paste(y, (PADDING, int(graph_offset_y + offset - y.height / 2)), y)

        # ------------------------ Horizontal (x-axis) labels ------------------------ #
        distance_x = graph_width / len(label_imgs)
        for i, l in enumerate(label_imgs):
            offset = distance_x * i + (0.5 * distance_x)
            x = int(graph_offset_x + offset - l.width / 2)
            y = graph_offset_x + graph_height + PADDING

            x_line = graph_offset_x + offset
            y_line = graph_offset_y + graph_height

            draw.line(
                (x_line, graph_offset_y, x_line, y_line), LIGHT_GRAY, STROKE_SIZE_GRID
            )

            image.paste(l, (x, y), l)

        # ------------------------------ Data projection ----------------------------- #
        for i in range(len(data)):
            x, y = generate_entry_pos(
                data, i, graph_offset_x, graph_offset_y, distance_x, distance_y
            )

            if i < len(data) - 1:
                # Connect this and the next point with a line
                x2, y2 = generate_entry_pos(
                    data, i + 1, graph_offset_x, graph_offset_y, distance_x, distance_y
                )
                draw.line((x, y, x2, y2), GRAY, STROKE_SIZE_CONNECTION)

            draw.ellipse(
                (
                    x - 0.5 * DOT_SIZE,
                    y - 0.5 * DOT_SIZE,
                    x + 0.5 * DOT_SIZE,
                    y + 0.5 * DOT_SIZE,
                ),
                fill=BLACK,
            )

    else:
        # --------------------------- If no data available --------------------------- #

        no_data_text = _rotated_text(
            "Keine Daten im ausgewählten Bereich.", 30, font_header
        )

        x = int(graph_offset_x + ((graph_width - no_data_text.width) / 2))
        y = int(graph_offset_y + ((graph_height - no_data_text.height) / 2))

        image.paste(no_data_text, (x, y), no_data_text)

    # ---------------------------------- Header ---------------------------------- #
    image.paste(header, (int(width / 2 - header.width / 2), PADDING), header)

    # ---------------------------------- Footer ---------------------------------- #
    image.paste(footer, (PADDING, height - footer_height), footer)

    # --------------------------- Horizontal base lines -------------------------- #
    draw.line(
        (PADDING, header_height, graph_offset_x + graph_width, header_height),
        fill=BLACK,
    )
    draw.line(
        (
            PADDING,
            graph_offset_y + graph_height,
            graph_offset_x + graph_width,
            graph_offset_y + graph_height,
        ),
        fill=BLACK,
    )

    # ---------------------------- Vertical base lines --------------------------- #
    draw.line(
        (
            graph_offset_x,
            graph_offset_y,
            graph_offset_x,
            graph_offset_y + graph_height,
        ),
        fill=BLACK,
    )
    draw.line(
        (
            graph_offset_x + graph_width,
            graph_offset_y,
            graph_offset_x + graph_width,
            graph_offset_y + graph_height,
        ),
        fill=BLACK,
    )

    # --------------------------------- Exporting -------------------------------- #
    result = BytesIO()
    image.save(result, "JPEG", quality=100)

    result.seek(0)
    return result
