# https://huggingface.co/datasets/bsmock/pubtables-1m/blob/main/README.md

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
    list_files,
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

    images_ext = ".jpg"
    bboxes_ext = ".xml"

    mapp = {"1": "True", "0": "False"}

    def create_ann(image_path):
        labels = []

        file_name = get_file_name(image_path)
        ann_path = f"{dataset_path}/{ds_name}/{file_name}{bboxes_ext}"

        # ann_path = [f for f in anns_paths if file_name in f][0]
        # ann_path = os.path.join(bboxes_path, file_name + bboxes_ext)

        if file_exists(ann_path):
            tree = ET.parse(ann_path)
            root = tree.getroot()

            image_np = sly.imaging.image.read(image_path)[:, :, 0]
            img_height = image_np.shape[0]
            img_wight = image_np.shape[1]

            # img_wight = int(root.find(".//width").text)
            # img_height = int(root.find(".//height").text)

            nam_xml = root.findall(".//name")
            pos_xml = root.findall(".//pose")
            trnc_xml = root.findall(".//truncated")
            diff_xml = root.findall(".//difficult")
            occl_xml = root.findall(".//occluded")
            coords_xml = root.findall(".//bndbox")

            for nam, pos, trnc, dif, ocl, curr_coord in zip(
                nam_xml, pos_xml, trnc_xml, diff_xml, occl_xml, coords_xml
            ):
                left = float(curr_coord[0].text)
                top = float(curr_coord[1].text)
                right = float(curr_coord[2].text)
                bottom = float(curr_coord[3].text)

                rect = sly.Rectangle(left=left, top=top, right=right, bottom=bottom)

                pose = sly.Tag(pose_meta, value=pos.text)
                trunc = sly.Tag(trunc_meta, value=mapp[trnc.text])
                diff = sly.Tag(diff_meta, value=mapp[dif.text])
                occl = sly.Tag(occl_meta, value=mapp[ocl.text])

                curr_obj = obj_table if nam.text == "table" else obj_table_rot
                label = sly.Label(rect, curr_obj, tags=[pose, trunc, diff, occl])
                labels.append(label)

            return sly.Annotation(img_size=(img_height, img_wight), labels=labels)

    obj_table = sly.ObjClass("table", sly.Rectangle)
    obj_table_rot = sly.ObjClass("table rotated", sly.Rectangle)

    pose_meta = sly.TagMeta("pose", sly.TagValueType.ANY_STRING)
    trunc_meta = sly.TagMeta(
        "truncated", sly.TagValueType.ONEOF_STRING, possible_values=["True", "False"]
    )
    diff_meta = sly.TagMeta(
        "difficult", sly.TagValueType.ONEOF_STRING, possible_values=["True", "False"]
    )
    occl_meta = sly.TagMeta(
        "occluded", sly.TagValueType.ONEOF_STRING, possible_values=["True", "False"]
    )

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(
        obj_classes=[obj_table, obj_table_rot],
        tag_metas=[pose_meta, trunc_meta, diff_meta, occl_meta],
    )
    api.project.update_meta(project.id, meta.to_json())

    # images_detection = list_files_recursively(dataset_path, [images_ext])
    # anns_detection = list_files_recursively(dataset_path, [bboxes_ext])

    for ds_name in ["val", "test", "train"]:
        dataset = api.dataset.create(project.id, ds_name.lower(), change_name_if_conflict=True)

        # anns_paths = [f for f in anns_detection if ds_name in f]
        # images_paths = [f"{dataset_path}/images/{get_file_name(f)}{images_ext}" for f in anns_paths]
        # images_paths = list_files(f"{dataset_path}/{ds_name}", [images_ext])

        with open(f"{dataset_path}/{ds_name}_filelist.txt", "r") as f:
            file_paths = f.readlines()

        anns_paths = [f"{dataset_path}/{path.strip()}" for path in file_paths]
        images_paths = [f"{dataset_path}/images/{get_file_name(f)}{images_ext}" for f in anns_paths]

        progress = sly.Progress("Create dataset {}".format(ds_name), len(anns_paths))

        for images_paths_batch in sly.batched(images_paths, batch_size=batch_size):
            images_names_batch = [
                get_file_name_with_ext(image_path) for image_path in images_paths_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, images_paths_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in images_paths_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))
    return project
