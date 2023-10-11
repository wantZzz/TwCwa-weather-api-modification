from html2image import Html2Image
from bs4 import BeautifulSoup

def v1_img(pop_data):
  css_file_content = ""

  for location in pop_data.keys():
    css_file_content += f'#{location} ' + 'path {fill: '+ pop_data[location] + ';}\n\n'

  with open('style_v1.css', 'w') as f:
    f.write(css_file_content)

  try:
    hti_v1 = Html2Image(custom_flags=['--no-sandbox'])
    hti_v1.screenshot(html_file='tw_map_v1.html', save_as='image_v1.png', css_file='style_v1.css', size=(477, 636))
    #hti_v1.screenshot(html_file='tw_map_v1.html', save_as='image_v1.png', size=(1000, 1350))

    return True, None

  except Exception as e:
    return False, e

def v2_img(v2_data):
  css_file_content = ""

  time = v2_data['time']

  del v2_data['time']

  with open('tw_map_v2.html', 'r') as f:
    soup = BeautifulSoup(f.read(), "lxml")

  for location in v2_data.keys():
    css_file_content += f'g[id={location}] ' + 'path {fill: '+ v2_data[location][0] + ';}\n\n'


  elements = soup.html.body.div.div.select('a')

  for element in elements:
    key = 'C' + element['id']

    element.span.span.span.i.string = v2_data[key][1]

    with open(f'svg_icon/{time}/{v2_data[key][2]}.svg', 'r') as f:
        svg_image = BeautifulSoup(f.read(), 'xml')

    svg_image.svg['height'] = "30"
    svg_image.svg['width'] = "30"

    element.span.img.replace_with(svg_image)

  style_tag = soup.new_tag("style")
  style_tag.string = css_file_content

  soup.html.body.append(style_tag)

  with open('tw_map_v2_copy.html', 'w') as f:
    f.write(soup.prettify())

  with open('style_v2.css', 'w') as f:
    f.write(css_file_content)

  try:
    hti_v2 = Html2Image(custom_flags=['--no-sandbox'])
    hti_v2.screenshot(html_file='tw_map_v2_copy.html', save_as='image_v2.png', css_file='style_v2.css', size=(507, 696))
    #hti_v2.screenshot(html_file='tw_map_v2.html', save_as='image_v2.png', size=(1000, 1350))

    return True, None

  except Exception as e:
    return False, e