from xml.dom import minidom
import cairosvg
import svgutils.transform as sg


def customize_vector(svg, directory, new_stroke=None, new_fill=None):
    # NOTE: Por consenso los svgs usarán fill blanco y negro
    #  - stroke => fil negro => None, "", #000, #000000, #030303 (old, deprecated)
    #  - fill => fil blanco: #fff, #ffffff
    with (
        minidom.parse(svg.path) as dom,
        open(f'{directory}/{svg.name}', 'w') as newsvg
    ):
        if new_stroke or new_fill:
            paths = dom.getElementsByTagName('path')
            for path in paths:
                fill = path.getAttribute('fill')
                if fill in ['#030303', '#000000', '#000', "", None]:
                    fill = f'#{new_stroke}'.replace('#none', 'none').replace("##", "#")
                else: # fill == fff | ffffff
                    fill = f'#{new_fill}'.replace('#none', 'none').replace("##", "#")
                path.setAttribute('fill', fill)
        newsvg.write(dom.toxml())


def export_to_png(svg, size):
    orig = str(svg)
    fig = sg.fromfile(orig)
    width = float(fig.width[:-2])
    height = float(fig.height[:-2])
    max_size = max(width, height)
    increase_ratio = float(size / max_size)
    new_width = round(width * increase_ratio)
    new_height = round(height * increase_ratio)
    new_name = svg.name.replace('.svg', '.png')
    dest = str(svg.parent / new_name)
    cairosvg.svg2png(url=orig, write_to=dest, output_width=new_width, output_height=new_height)

