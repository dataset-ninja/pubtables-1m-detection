# https://www.kaggle.com/datasets/sreesankar711/pubtables-img-detect-test

import os
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

import numpy as np
import supervisely as sly
from dotenv import load_dotenv
from supervisely.io.fs import (
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
    list_files_recursively,
)
from tqdm import tqdm

import src.settings as s
from dataset_tools.convert import unpack_if_archive


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # project_name = "pubtables detection"
    dataset_path = "/home/grokhi/rawdata/pubtables-1m/PubTables-1M-Detection"
    # bboxes_path = "/home/alex/DATASETS/TODO/pubtables-detection/archive/PubTables-1M-Detection_Annotations_Test"

    batch_size = 30
    # ds_name = "test"
    images_ext = ".jpg"
    bboxes_ext = ".xml"

    def create_ann(image_path):
        labels = []

        file_name = get_file_name(image_path)

        ann_path = [f for f in anns_detection if file_name in f][0]

        # ann_path = os.path.join(bboxes_path, file_name + bboxes_ext)

        tree = ET.parse(ann_path)
        root = tree.getroot()

        img_wight = int(root.find(".//width").text)
        img_height = int(root.find(".//height").text)

        coords_xml = root.findall(".//bndbox")
        for curr_coord in coords_xml:
            left = float(curr_coord[0].text)
            top = float(curr_coord[1].text)
            right = float(curr_coord[2].text)
            bottom = float(curr_coord[3].text)

            rect = sly.Rectangle(left=left, top=top, right=right, bottom=bottom)
            label = sly.Label(rect, table)
            labels.append(label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels)

    table = sly.ObjClass("table", sly.Rectangle)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(obj_classes=[table])
    api.project.update_meta(project.id, meta.to_json())

    images_detection = [
        file for file in list_files_recursively(dataset_path, [images_ext]) if "-Detection" in file
    ]
    anns_detection = [
        file for file in list_files_recursively(dataset_path, [bboxes_ext]) if "-Detection" in file
    ]

    for ds_name in ["Train", "Val", "Test"]:
        dataset = api.dataset.create(project.id, ds_name.lower(), change_name_if_conflict=True)

        images_paths = [file for file in images_detection if ds_name in file]

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_paths))

        for images_paths_batch in sly.batched(images_paths, batch_size=batch_size):
            images_names_batch = [get_file_name(image_path) for image_path in images_paths_batch]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, images_paths_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in images_paths_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))
        return project
