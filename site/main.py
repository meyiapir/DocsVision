import io
import gradio as gr
import requests

from bot.lib.rtf_parser import parse_rtf_header
from config import DOC_TYPES_DICT, API_HOST


def greet(*args):
    file_paths = args[0]
    if not file_paths:
        return 'Приложите файлы'

    args = args[1:]

    if len([x for x in args if x >= 0]) != len(args): return 'Кол-во документов не может быть отрицательным'

    values = dict(zip(list(DOC_TYPES_DICT.keys()), [(x if x else 0) for x in args]))

    if set(list(values.values())) == {0}:
        return 'Задайте количества документов'

    response = {doc_type: 0 for doc_type in DOC_TYPES_DICT}
    res_message = ''

    files_types = {}

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            file.seek(0)
            parsed = parse_rtf_header(file.read())

            counter = 3

            while counter > 0:
                r = requests.post(f'{API_HOST}/predict', data=dict(text=parsed))
                if r.status_code == 200:
                    r = list(DOC_TYPES_DICT.keys())[int(r.content)]
                    break
                counter -= 1

            response[r] += 1

            print(file_path, r)

            files_types.update({file_path.split('\\')[-1]: DOC_TYPES_DICT[r]})

    for doc_type in DOC_TYPES_DICT:
        if response.get(doc_type):
            value = response[doc_type]
        else:
            value = 0

        required_value = values[doc_type]

        if value != required_value:
            res_message += f"{DOC_TYPES_DICT[doc_type]}: {value} шт., должно быть {required_value}\n"

    if not res_message:
        res_message = 'Все документы в порядке!'

    res_message += ('\n\n' + '\n'.join([f'{item[0]}: {item[1]}' for item in files_types.items()]))

    return res_message


inputs = [gr.File(file_count="multiple")]
inputs += [gr.Number(label=DOC_TYPES_DICT[doc_type]) for doc_type in DOC_TYPES_DICT]

demo = gr.Interface(
    fn=greet,
    inputs=inputs,
    outputs=["text"],
    allow_flagging="never"
)

demo.launch()