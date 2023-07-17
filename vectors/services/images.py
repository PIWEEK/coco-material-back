from xml.dom import minidom


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

