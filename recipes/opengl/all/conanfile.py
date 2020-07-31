from conans import ConanFile, tools
from conans.errors import ConanException
import os


class SysConfigOpenGLConan(ConanFile):
    name = "opengl"
    version = "system"
    description = "cross-platform virtual conan package for the OpenGL support"
    topics = ("conan", "opengl", "gl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.opengl.org/"
    license = "MIT"
    settings = ("os",)

    options = {"glvnd": [True, False]}
    default_options = {"glvnd": True}

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.glvnd

    def package_id(self):
        self.info.header_only()

    def _os_derived_from_debian_11_or_later(self):
        distro = tools.os_info.linux_distro
        version = tools.os_info.os_version

        return (distro == "debian" and version >= "11") or \
               (distro == "ubuntu" and version >= "20") or \
               (distro == "pop" and version >= "20")

    def system_requirements(self):
        if not tools.os_info.is_linux or not self.settings.os == "Linux":
            return

        package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')

        if tools.os_info.with_yum:
            if tools.os_info.linux_distro == "fedora" and tools.os_info.os_version >= "32":
                packages = ["libglvnd-devel", "mesa-libGLU-devel"] # TODO add EGL and GLX
            else:
                packages = ["mesa-libGL-devel", "mesa-libGLU-devel"] # TODO add EGL and GLX
        elif tools.os_info.with_apt:
            if self._os_derived_from_debian_11_or_later():
                packages = ["libgl-dev", "libglu1-mesa-dev", "libegl-dev", "libglx-dev"]
            else:
                packages = ["libgl1-mesa-dev", "libglu1-mesa-dev", "libegl1-mesa-dev"]
        elif tools.os_info.with_pacman:
            packages = ["libglvnd", "glu"] # TODO add EGL and GLX
        elif tools.os_info.with_zypper:
            packages = ["Mesa-libGL-devel", "Mesa-libGLU-devel"] # TODO add EGL and GLX
        else:
            packages = []
            self.output.warn("Don't know how to install OpenGL for your distro.")

        for p in packages:
            package_tool.install(update=True, packages=p)

    def _gl_defines(self):
        if self.settings.os == "Macos":
            return ["GL_SILENCE_DEPRECATION=1"]
        
        return []

    def _gl_libraries(self):
        if self.settings.os == "Macos":
            return ["OpenGL"]
        elif self.settings.os == "Windows":
            return ["opengl32"]
        elif self.settings.os == "Linux":
            if self.options.glvnd:
                return ["OpenGL"]
            else:
                return ["GL"]

    def _glu_defines(self):
        return self._gl_defines()
    
    def _glu_libraries(self):
        if self.settings.os == "Macos":
            return ["OpenGL"]
        elif self.settings.os == "Windows":
            return ["glu32"]
        elif self.settings.os == "Linux":
            return ["GLU"]

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenGL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenGL"

        self.cpp_info.components["GL"].defines = self._gl_defines()
        self.cpp_info.components["GL"].libs = self._gl_libraries()

        self.cpp_info.components["GLU"].defines = self._glu_defines()
        self.cpp_info.components["GLU"].libs = self._glu_libraries()

        if self.settings.os == "Linux":
            if self.options.glvnd:
                self.cpp_info.components["OpenGL"].libs = ["OpenGL"]

            self.cpp_info.components["EGL"].libs = "EGL"
            self.ccp_info.components["GLX"].libs = "GLX"

