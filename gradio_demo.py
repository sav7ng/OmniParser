import json
from typing import Optional, Tuple

import gradio as gr
import numpy as np
import torch
from PIL import Image
import io


import base64, os

from PIL.ImageFile import ImageFile

from utils import check_ocr_box, get_yolo_model, get_caption_model_processor, get_som_labeled_img
import torch
from PIL import Image

# os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

yolo_model = get_yolo_model(model_path='weights/icon_detect/best.pt')
# yolo_model.to('cpu')
# caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path="weights/icon_caption_florence", device='cpu')
caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path="weights/icon_caption_florence")
# caption_model_processor = get_caption_model_processor(model_name="blip2", model_name_or_path="weights/icon_caption_blip2")



MARKDOWN = """
# OmniParser for Pure Vision Based General GUI Agent 🔥
<div>
    <a href="https://arxiv.org/pdf/2408.00203">
        <img src="https://img.shields.io/badge/arXiv-2408.00203-b31b1b.svg" alt="Arxiv" style="display:inline-block;">
    </a>
</div>

OmniParser is a screen parsing tool to convert general GUI screen to structured elements. 
"""

# DEVICE = torch.device('cpu')
DEVICE = torch.device('cuda')

# @spaces.GPU
# @torch.inference_mode()
# @torch.autocast(device_type="cuda", dtype=torch.bfloat16)
def process(
    image_input,
    box_threshold,
    iou_threshold,
    use_paddleocr,
    output_coord_in_ratio,
    imgsz
) -> tuple[ImageFile, str, str]:

    print(imgsz)
    image_save_path = 'imgs/saved_image_demo.png'
    image_input.save(image_save_path)
    image = Image.open(image_save_path)
    box_overlay_ratio = image.size[0] / 3200
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }
    # import pdb; pdb.set_trace()
    ocr_bbox_rslt, is_goal_filtered = check_ocr_box(image_save_path, display_img = False, output_bb_format='xyxy', goal_filtering=None, easyocr_args={'paragraph': False, 'text_threshold':0.9}, use_paddleocr=use_paddleocr)
    text, ocr_bbox = ocr_bbox_rslt
    # print('prompt:', prompt)
    dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(image_save_path, yolo_model, BOX_TRESHOLD = box_threshold, output_coord_in_ratio=output_coord_in_ratio, ocr_bbox=ocr_bbox,draw_bbox_config=draw_bbox_config, caption_model_processor=caption_model_processor, ocr_text=text,iou_threshold=iou_threshold, imgsz=imgsz)
    image = Image.open(io.BytesIO(base64.b64decode(dino_labled_img)))
    print('finish processing')
    # parsed_content_list = '\n'.join(parsed_content_list)
    parsed_map = {}
    for item in parsed_content_list:
        # 从字符串中提取数字和对应的文本
        key_value = item.split(": ")
        if len(key_value) == 2:  # 确保分割成功
            key = int(key_value[0].split()[-1])  # 提取 "Text Box ID N"
            value = key_value[1]  # 提取文本
            parsed_map[key] = value
    parsedContentListJsonStrE = json.dumps(parsed_map)
    parsedContentListJsonStr = parsedContentListJsonStrE.encode('utf-8').decode('unicode_escape')
    label_coordinates_serializable = {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in
                                      label_coordinates.items()}
    labelCoordinatesJsonStr = json.dumps(label_coordinates_serializable)
    return image, parsedContentListJsonStr, labelCoordinatesJsonStr



with gr.Blocks() as demo:
    gr.Markdown(MARKDOWN)
    with gr.Row():
        with gr.Column():
            image_input_component = gr.Image(
                type='pil', label='Upload image')
            # set the threshold for removing the bounding boxes with low confidence, default is 0.05
            box_threshold_component = gr.Slider(
                label='Box Threshold', minimum=0.01, maximum=1.0, step=0.01, value=0.05)
            # set the threshold for removing the bounding boxes with large overlap, default is 0.1
            iou_threshold_component = gr.Slider(
                label='IOU Threshold', minimum=0.01, maximum=1.0, step=0.01, value=0.1)
            use_paddleocr_component = gr.Checkbox(
                label='Use PaddleOCR', value=True)
            output_coord_in_ratio_component = gr.Checkbox(
                label='Use Output Coord In Ratio', value=False)
            imgsz_component = gr.Slider(
                label='Icon Detect Image Size', minimum=640, maximum=1920, step=32, value=640)
            submit_button_component = gr.Button(
                value='Submit', variant='primary')
        with gr.Column():
            image_output_component = gr.Image(type='pil', label='Image Output')
            parsedContentListJsonStr_output_component = gr.Textbox(label='parsedContentListJsonStr', placeholder='Text Output', show_copy_button = True, show_label = True)
            labelCoordinatesJsonStr_output_component = gr.Textbox(label='labelCoordinatesJsonStr', placeholder='Text Output', show_copy_button = True, show_label = True)

    submit_button_component.click(
        fn=process,
        inputs=[
            image_input_component,
            box_threshold_component,
            iou_threshold_component,
            use_paddleocr_component,
            output_coord_in_ratio_component,
            imgsz_component
        ],
        outputs=[image_output_component, parsedContentListJsonStr_output_component, labelCoordinatesJsonStr_output_component]
    )

# demo.launch(debug=False, show_error=True, share=True)
demo.launch(show_api=True, debug=True, show_error=True, max_file_size=1 * gr.FileSize.GB, server_name='0.0.0.0')