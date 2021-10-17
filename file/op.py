import json
import os
import shutil
import time


def move(src, des, override=False, inside=False):
    """
    支持文件或文件夹的移动(shutil.move不支持覆盖)
    :param src:
    :param des:
    :param override: 是否直接覆盖
    :param inside: 仅当源为文件夹有效，如果为True则只复制文件夹下的内容，而不是复制整个源文件夹
    :return:
    """
    if override:
        copy(src, des, override=override, inside=inside)
        if os.path.isfile(src):
            os.remove(src)
        elif os.path.isdir(src):
            if inside:
                for path in os.listdir(src):
                    path = os.path.join(src, path)
                    remove(path)
            else:
                remove(src)
    else:
        if inside:
            for path in os.listdir(src):
                path = os.path.join(src, path)
                shutil.move(path, des)
        else:
            shutil.move(src, des)


def remove(path, weak=False, weak_keep=7 * 24 * 60 * 60):
    """
    删除文件或文件夹
    支持弱删除，以保留临时文件一段时间
    :param path: 删除文件路径
    :param weak: 是否是弱删除
    :param weak_keep: 弱删除文件的保持时间，单位为s
    :return:
    """
    if not os.path.exists(path):
        return

    if not weak:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    else:
        tmp_dir = 'tmp-qu'
        file_expires = 'file_expires.json'
        if not os.path.exists('tmp-qu'):
            os.mkdir(tmp_dir)
            with open(f'./{tmp_dir}/{file_expires}', 'w', encoding='utf-8') as fp:
                json.dump({}, fp)
        move(path, tmp_dir)
        with open(f'./{tmp_dir}/{file_expires}', 'r', encoding='utf-8') as fp:
            expires_map = json.load(fp)
            for file, expires in expires_map.copy().items():
                now = time.time()
                file_path = os.path.join(tmp_dir, file)
                if now >= expires and os.path.exists(file_path):
                    remove(file_path)
                    expires_map.pop(file)
        with open(f'./{tmp_dir}/{file_expires}', 'w', encoding='utf-8') as fp:
            expires_map[os.path.basename(path)] = time.time() + weak_keep
            json.dump(expires_map, fp)


def copy(src, des, override=False, inside=False):
    """
    复制文件或文件夹(shutil.copyTree会自动覆盖)
    :param src:
    :param des:
    :param override:
    :param inside: 仅当源为文件夹有效，如果为True则只复制文件夹下的内容，而不复制整个源文件夹
    :return:
    """
    if not os.path.exists(src):
        raise Exception(f"{src} not exists")

    if os.path.isfile(src):
        if os.path.isdir(des):
            des = os.path.join(des, os.path.basename(src))
        if not override and os.path.isfile(des):
            raise Exception(f"{des} exists")
        shutil.copy(src, des)
    elif os.path.isdir(src):
        if inside:
            for path in os.listdir(src):
                path = os.path.join(src, path)
                copy(path, des, override=override)
            return

        if os.path.exists(des):
            des = os.path.join(des, os.path.basename(src))

        def my_copy(s, d):
            if os.path.exists(d):
                raise Exception(f"{d} exists")
            shutil.copy2(s, d)
        copy_function = shutil.copy2 if override else my_copy
        shutil.copytree(src, des, copy_function=copy_function)

