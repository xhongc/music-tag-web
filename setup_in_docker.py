import os
import shutil
import sys
import multiprocessing
from distutils.core import setup
from distutils.extension import Extension

NB_COMPILE_JOBS = multiprocessing.cpu_count()

try:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize
except:
    print("You don't seem to have Cython installed. Please get a")
    print("copy from www.cython.org and install it")
    sys.exit(1)


# scan the 'dvedit' directory for extension files, converting
# them to extension names in dotted notation
def scandir(dir, files=[]):
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        if os.path.isfile(path) and path.endswith(".py"):
            files.append(path.replace(os.path.sep, ".")[:-3])
        elif os.path.isdir(path):
            scandir(path, files)
    return files


# generate an Extension object from its dotted name
def makeExtension(extName):
    extPath = extName.replace(".", os.path.sep) + ".py"
    return Extension(
        extName,
        [extPath],
        include_dirs=["."],  # adding the '.' to include_dirs is CRUCIAL!!
        extra_compile_args=["-O3", "-Wall"],
        extra_link_args=['-g'],
        build_dir='build'
    )


def clean(base_path):
    full_path = os.path.join(base_path, 'yee')
    for path, dir_list, file_list in os.walk(full_path):
        if path.find('__pycache__') != -1:
            shutil.rmtree(path, ignore_errors=True)
            continue
        for file_name in file_list:
            ext = os.path.splitext(file_name)[-1]
            if ext == '.c':
                os.remove(os.path.join(path, file_name))
            elif ext == '.py':
                os.remove(os.path.join(path, file_name))
            elif ext == '.map':
                os.remove(os.path.join(path, file_name))
            elif ext == '.DS_Store':
                os.remove(os.path.join(path, file_name))
    for path, dir_list, file_list in os.walk(os.path.join(base_path, 'dependencies')):
        if path.find('__pycache__') != -1:
            shutil.rmtree(path, ignore_errors=True)
            continue


# get the list of extensions
extNames = scandir("yee")
# and build up the set of Extension objects
extensions = [makeExtension(name) for name in extNames]


# finally, we can pass all this to distutils
# setup(
#     name="yee",
#     packages=["yee"],
#     ext_modules=extensions,
#     cmdclass={'build_ext': build_ext},
# )
def setup_given_extensions(extensions):
    setup(
        name="yee",
        packages=["yee"],
        ext_modules=cythonize(extensions),
        cmdclass={'build_ext': build_ext},
    )


def setup_extensions_in_sequential():
    setup_given_extensions(extensions)


def setup_extensions_in_parallel():
    cythonize(extensions, nthreads=NB_COMPILE_JOBS)
    pool = multiprocessing.Pool(processes=NB_COMPILE_JOBS)
    pool.map(setup_given_extensions, extensions)
    pool.close()
    pool.join()


if "build_ext" in sys.argv:
    setup_extensions_in_parallel()
else:
    setup_extensions_in_sequential()
base_path = os.path.abspath('.')