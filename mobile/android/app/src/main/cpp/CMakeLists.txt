cmake_minimum_required(VERSION 3.31.6)

project("maestro-qwen" LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(LLAMA_SRC
    "${CMAKE_CURRENT_LIST_DIR}/../../../../third_party/llama.cpp"
)

# Maestro usa somente a biblioteca de inferência.
# Não compilar CLI, server, testes ou exemplos.
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)

set(LLAMA_BUILD_COMMON OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_SERVER OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_APP OFF CACHE BOOL "" FORCE)
set(LLAMA_OPENSSL OFF CACHE BOOL "" FORCE)

set(GGML_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GGML_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GGML_NATIVE OFF CACHE BOOL "" FORCE)
set(GGML_OPENMP OFF CACHE BOOL "" FORCE)
set(GGML_BACKEND_DL OFF CACHE BOOL "" FORCE)
set(GGML_CPU_ALL_VARIANTS OFF CACHE BOOL "" FORCE)
set(GGML_LLAMAFILE OFF CACHE BOOL "" FORCE)

if(ANDROID_ABI STREQUAL "arm64-v8a")
    set(GGML_SYSTEM_ARCH "ARM" CACHE STRING "" FORCE)
    set(GGML_CPU_KLEIDIAI ON CACHE BOOL "" FORCE)
endif()

add_subdirectory(
    "${LLAMA_SRC}"
    "${CMAKE_CURRENT_BINARY_DIR}/llama"
    EXCLUDE_FROM_ALL
)

add_library(
    maestro-qwen
    SHARED
    maestro_qwen.cpp
)

target_include_directories(
    maestro-qwen
    PRIVATE
    "${LLAMA_SRC}/include"
    "${LLAMA_SRC}/ggml/include"
)

target_link_libraries(
    maestro-qwen
    PRIVATE
    llama
    android
    log
)
