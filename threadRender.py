
def render(contents: list):
    output_html = '<meta charset="UTF-8">'
    para = ''
    for i in range(len(contents)):
        content = contents[i]
        insert = content["insert"]
        align = 'unset'
        try:
            if (contents[i + 1]['insert'] == "\n") and ('attributes' in contents[i + 1].keys()):
                if 'align' in contents[i + 1]['attributes'].keys():
                    align = contents[i + 1]['attributes']['align']
        except IndexError:
            pass
        if type(insert) is dict:
            if 'image' in insert.keys():
                tmp = f'<img src="{insert["image"]}" height={content["attributes"]["height"]} width={content["attributes"]["width"]}>'
                output_html += tmp

            elif "link_card" in insert.keys():
                tmp = f'<a href="{insert["link_card"]["landing_url"]}"><div style="margin:0 auto;background-color: #b6b5b5;border: none;border-radius: 10px"><img src="{insert["link_card"]["cover"]}" height=100 width=100 style="float: left"><label>{insert["link_card"]["title"]}</label></div></a>'
                output_html += tmp

            elif "divider" in insert:
                output_html += "<hr/>"

        elif type(insert) is str:
            if insert == "\n":
                output_html += f'<p>{para}</p>'
                para = ''
            elif insert == "\n\n":
                output_html += f'<p>{para}</p><br/>'
                para = ''
            else:
                for text in insert.split("\n"):
                    if "attributes" in content.keys():
                        if "bold" in content["attributes"]:
                            tmp = '<strong style="{1}">{0}</strong>'
                        else:
                            tmp = '<span style="{1}">{0}</span>'
                        if "color" in content["attributes"].keys():
                            style = f"color:{content['attributes']['color']};text-align:{align}"
                        else:
                            style = f"text-align:{align};"
                        if 'link' in content["attributes"].keys():
                            para += tmp.format('<a href="' + content['attributes'][
                                "link"] + f'" style="text-align:{align}" >{text}</a>', style)
                        else:
                            para += tmp.format(insert, style)
                    else:
                        para += f'<p style="text-align:{align}">{text}</p>'
    output_html += f'<p>{para}</p>'
    return output_html
