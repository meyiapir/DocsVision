import gradio
import gradio as gr
from config import DOC_TYPES_DICT

def greet(*args):
    files = args[:-11]
    print(files)
    values = dict(zip(list(DOC_TYPES_DICT.keys()), [(x if x else 0) for x in args[-12:]]))
    print(values)

    return values


inputs = [gr.File(file_count="multiple")]
inputs += [gr.Number(label=DOC_TYPES_DICT[doc_type]) for doc_type in DOC_TYPES_DICT]

demo = gr.Interface(
    fn=greet,
    inputs=inputs,
    outputs=["text"],
)

demo.launch()