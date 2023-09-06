import re
from distutils.core import setup

from Cython.Build import cythonize
import os
import shutil
import tempfile
import logging
import sys

# set up logging
logger = logging.getLogger("encrypt-py")

format_string = (
    "%(asctime)s|%(filename)s|%(funcName)s|line:%(lineno)d|%(levelname)s| %(message)s"
)
formatter = logging.Formatter(format_string, datefmt="%Y-%m-%dT%H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.stream = sys.stdout

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def walk_file(file_path):
    if os.path.isdir(file_path):
        for current_path, sub_folders, files_name in os.walk(file_path):
            base_name = os.path.basename(current_path)
            if base_name in ["migrations"]:
                continue
            for file in files_name:
                if file.endswith(".py"):
                    file_path = os.path.join(current_path, file)
                    yield file_path

    else:
        yield file_path


def delete_files(files_path):
    """
    @summary: 删除文件
    ---------
    @param files_path: 文件路径 py 及 c 文件
    ---------
    @result:
    """
    try:
        # 删除python文件及c文件
        for file in files_path:
            os.remove(file)  # py文件
            os.remove(file.replace(".py", ".c"))  # c文件

    except Exception as e:
        pass


def rename_excrypted_file(output_file_path):
    files = walk_file(output_file_path)
    for file in files:
        if file.endswith(".pyd") or file.endswith(".so"):
            new_filename = re.sub("(.*)\..*\.(.*)", r"\1.\2", file)
            os.rename(file, new_filename)


class TemporaryDirectory(object):
    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


def encrypt_py(py_files: list):
    encrypted_py = []

    with TemporaryDirectory() as td:
        total_count = len(py_files)
        for i, py_file in enumerate(py_files):
            try:
                dir_name = os.path.dirname(py_file)
                file_name = os.path.basename(py_file)

                # os.chdir(dir_name)

                logger.debug("正在加密 {}/{},  {}".format(i + 1, total_count, file_name))

                setup(
                    ext_modules=cythonize([py_file], quiet=True, language_level=3),
                    script_args=["build_ext", "-t", td, "--inplace"],
                )

                encrypted_py.append(py_file)
                logger.debug("encrypted success {}".format(file_name))

            except Exception as e:
                logger.exception("encrypted failed {} , error {}".format(py_file, e))
                temp_c = py_file.replace(".py", ".c")
                if os.path.exists(temp_c):
                    os.remove(temp_c)

        return encrypted_py


if __name__ == '__main__':
    encode_dir = "/Users/macbookair/coding/music-tag-web/django_vue_cli/"
    fileSet = walk_file(encode_dir)
    encrypted_py = encrypt_py(list(fileSet))
    delete_files(encrypted_py)
    rename_excrypted_file(encode_dir)