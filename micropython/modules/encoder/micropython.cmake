set(MOD_NAME encoder)
string(TOUPPER ${MOD_NAME} MOD_NAME_UPPER)
add_library(usermod_${MOD_NAME} INTERFACE)

target_sources(usermod_${MOD_NAME} INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/${MOD_NAME}.c
    ${CMAKE_CURRENT_LIST_DIR}/${MOD_NAME}.cpp
    ${CMAKE_CURRENT_LIST_DIR}/../../../drivers/encoder-pio/capture.cpp
    ${CMAKE_CURRENT_LIST_DIR}/../../../drivers/encoder-pio/encoder.cpp
)
pico_generate_pio_header(usermod_${MOD_NAME} ${CMAKE_CURRENT_LIST_DIR}/../../../drivers/encoder-pio/encoder.pio)

target_include_directories(usermod_${MOD_NAME} INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/../../../drivers/encoder-pio/
)

target_compile_definitions(usermod_${MOD_NAME} INTERFACE
    MODULE_ENCODER_ENABLED=1
)

target_link_libraries(usermod INTERFACE usermod_${MOD_NAME})