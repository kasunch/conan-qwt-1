from conans import ConanFile, tools, VisualStudioBuildEnvironment
from conans.tools import cpu_count, os_info, SystemPackageTool
from conans.util.files import load
from conans.errors import ConanException
import os
import sys
import re
import pathlib
import glob
from distutils.spawn import find_executable


class QwtConan(ConanFile):
    name = "qwt"
    description = "Qt Widgets for Technical Applications"
    topics = ("conan", "qt", "ui", "qwt")
    url = "https://github.com/blixttech/conan-qwt"
    homepage = "https://qwt.sourceforge.io/"
    license = "LGPL-3.0"  # SPDX Identifiers https://spdx.org/licenses/

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "plot": [True, False],
        "widgets": [True, False],
        "svg": [True, False],
        "opengl": [True, False],
        "mathml": [True, False],
        "designer": [True, False],
        "examples": [True, False],
        "playground": [True, False]
    }
    default_options = {
        "shared": False,
        "plot": True,
        "widgets": True,
        "svg": True,
        "opengl": True,
        "mathml": True,
        "designer": False,
        "examples": False,
        "playground": False
    }

    exports_sources = ["FindQwt.cmake"]

    def set_version(self):
        if not self.version:
            git = tools.Git(folder=self.recipe_folder)
            output = git.run("describe --all").splitlines()[0].strip()
            self.version = re.sub("^.*/v?|^v?", "", output)
        self.output.info("Version: %s" % (self.version))

    def source(self):
        source_folder = os.path.join(self.source_folder, self.name)
        svn = tools.SVN(folder=source_folder)
        print(self.conan_data["sources"])
        svn.checkout(**self.conan_data["sources"][self.version])

    def requirements(self):
        self.requires("qt/5.14.2@bincrafters/stable")

        if self.options.svg:
            self.requires("qtsvg/5.14.2@blixt/stable")

    def build(self):
        if self.settings.os == "Windows" and (not self.settings.compiler == "Visual Studio"):
            raise ConanException("Not yet implemented for this compiler")

        source_folder = os.path.join(self.source_folder, self.name)
        build_folder = os.path.join(self.build_folder, ("%s-build" % self.name))
        install_folder = os.path.join(self.build_folder, ("%s-install" % self.name))

        if not os.path.exists(build_folder):
            os.mkdir(build_folder)
        if not os.path.exists(install_folder):
            os.mkdir(install_folder)

        qwt_config_file_path = os.path.join(source_folder, "qwtconfig.pri")
        self.output.info("Configuring " + qwt_config_file_path)
        qwt_config = load(qwt_config_file_path)
        qwt_config += "\nQWT_CONFIG %s= QwtDll" % ("+" if self.options.shared else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtPlot" % ("+" if self.options.plot else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtWidgets" % ("+" if self.options.widgets else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtSvg" % ("+" if self.options.svg else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtOpenGL" % ("+" if self.options.opengl else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtMathML" % ("+" if self.options.mathml else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtDesigner" % ("+" if self.options.designer else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtExamples" % ("+" if self.options.examples else "-")
        qwt_config += "\nQWT_CONFIG %s= QwtPlayground" % ("+" if self.options.playground else "-")
        qwt_config = qwt_config.encode("utf-8")

        with open(qwt_config_file_path, "wb") as handle:
            handle.write(qwt_config)

        qwt_build_string = "CONFIG += %s" % ("release" if self.settings.build_type ==
                                             "Release" else "debug")
        qwt_build_file_path = os.path.join(source_folder, "qwtbuild.pri")
        tools.replace_in_file(qwt_build_file_path,
                              "CONFIG           += debug_and_release", qwt_build_string)
        tools.replace_in_file(qwt_build_file_path, "CONFIG           += build_all", "")
        tools.replace_in_file(qwt_build_file_path, "CONFIG           += release", qwt_build_string)

        qmake_pro_file = os.path.join(source_folder, "qwt.pro")
        qmake_command = os.path.join(self.deps_cpp_info['qt'].rootpath, "bin", "qmake")
        qmake_args = []
        qmake_args.append("-r %s" % qmake_pro_file)

        build_args = []
        if self.settings.os == "Windows":
            build_command = find_executable("jom.exe")
            if not build_command:
                build_command = "nmake.exe"
            else:
                build_args.append("-j")
                build_args.append(str(cpu_count()))
        else:
            build_command = find_executable("make")
            if not build_command:
                raise ConanException("Cannot find make")
            else:
                build_args.append("-j")
                build_args.append(str(cpu_count()))

        if self.settings.os == "Windows":
            # INSTALL_ROOT environmental variable is placed just after the drive part
            # and before the  Qt installation directory in the path.
            # Eg. C:$(INSTALL_ROOT)\.conan\3feb31\1\....
            tail = os.path.splitdrive(install_folder)[1]
            build_args.append("INSTALL_ROOT=" + tail)
        else:
            # INSTALL_ROOT environmental variable is prefixed to the Qt installation directory
            # in the path.
            # Eg. $(INSTALL_ROOT)/home/conan/.conan/data/qt/....
            build_args.append("INSTALL_ROOT=" + install_folder)
        build_args.append("install")

        self.output.info("QMAKE: %s %s" % (qmake_command, " ".join(qmake_args)))
        self.output.info("BUILD: %s %s" % (build_command, " ".join(build_args)))

        if self.settings.compiler == "Visual Studio":
            env_build = VisualStudioBuildEnvironment(self)
            with tools.environment_append(env_build.vars):
                vcvars_cmd = tools.vcvars_command(self.settings)
                self.run("%s && %s %s" % (vcvars_cmd, qmake_command, " ".join(qmake_args)),
                         cwd=build_folder)
                self.run("%s && %s %s" % (vcvars_cmd, build_command, " ".join(build_args)),
                         cwd=build_folder)
        else:
            self.run("%s %s" % (qmake_command, " ".join(qmake_args)), cwd=build_folder)
            self.run("%s %s" % (build_command, " ".join(build_args)), cwd=build_folder)

    def package(self):
        install_folder = os.path.join(self.build_folder, ("%s-install" % self.name))
        # Try to find the location where the files are installed.
        folders = glob.glob(os.path.join(install_folder, "**", "include"),
                            recursive=True)
        if len(folders) == 0:
            raise ConanException("Cannot find installation directory")
        install_prefix = pathlib.Path(folders[0]).parent

        self.copy("FindQwt.cmake", ".", ".")
        self.copy("*", dst="include", src=os.path.join(install_prefix, "include"), symlinks=True)
        self.copy("*", dst="lib", src=os.path.join(install_prefix, "lib"), symlinks=True)
        self.copy("*", dst="features", src=os.path.join(install_prefix, "features"), symlinks=True)
        self._fix_findqwt_cmake(os.path.join(self.package_folder, "FindQwt.cmake"))
        self._fix_qwtconfig_pri(os.path.join(self.package_folder, "features", "qwtconfig.pri"))

    def _fix_findqwt_cmake(self, filename):
        if not self.options.svg:
            tools.replace_in_file(filename,
                                  'list(APPEND Qwt_LIBRARIES "Qt5::Svg")\n',
                                  '')
        if self.options.shared:
            tools.replace_in_file(filename,
                                  'add_library(Qwt::Qwt STATIC IMPORTED)',
                                  'add_library(Qwt::Qwt SHARED IMPORTED)')
            tools.replace_in_file(filename,
                                  'add_library(Qwt::Mathml STATIC IMPORTED)',
                                  'add_library(Qwt::Mathml SHARED IMPORTED)')

    def _fix_qwtconfig_pri(self, filename):
        tools.replace_in_file(filename,
                              'QWT_INSTALL_PREFIX    = /usr/local/qwt-$$QWT_VERSION-svn',
                              "QWT_INSTALL_PREFIX = $$(CONAN_PKG_DIR_" + self.name.upper() + ")",
                              strict=False)
        tools.replace_in_file(filename,
                              'QWT_INSTALL_PREFIX    = C:/Qwt-$$QWT_VERSION-svn',
                              "QWT_INSTALL_PREFIX = $$(CONAN_PKG_DIR_" + self.name.upper() + ")",
                              strict=False)

    def package_info(self):
        self.cpp_info.libs = ["qwt"]
        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)
        self.env_info.__setattr__("CONAN_PKG_DIR_" + self.name.upper(), self.package_folder)
