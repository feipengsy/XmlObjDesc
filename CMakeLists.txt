cmake_minimum_required (VERSION 3.15)
message(STATUS "cmake version ${CMAKE_VERSION}")

project(XmlObjDesc)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

install(DIRECTORY python DESTINATION ${CMAKE_INSTALL_PREFIX})
install(DIRECTORY templates DESTINATION ${CMAKE_INSTALL_PREFIX})
install(DIRECTORY xml_files DESTINATION ${CMAKE_INSTALL_PREFIX})
