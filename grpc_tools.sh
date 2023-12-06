#!/bin/bash

# grpc_tools.sh

# Генерация Python-кода на основе файлов .proto в текущей и всех вложенных папках
generate_python_code() {
  find . -name '*.proto' -exec python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. {} \;
}

# Вызов функции для обработки всех .proto файлов
generate_python_code
