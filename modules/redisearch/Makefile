SRC_DIR = src
MODULE_VERSION = v8.7.90
MODULE_REPO = https://github.com/redisearch/redisearch
TARGET_MODULE = $(SRC_DIR)/bin/$(FULL_VARIANT)/search-community/redisearch.so

# Enable link-time optimization for RediSearch by default. Override with LTO=0.
LTO ?= 1
export LTO

# Inline LSE atomics on Linux AArch64 are disabled by default to keep the
# resulting binary loadable on pre-Armv8.1-a cores (Cortex-A72, AWS Graviton1,
# Raspberry Pi 4), which would otherwise SIGILL on module load.
# Override with INLINE_LSE_ATOMICS=1 to opt into the inline LSE optimization
# on Armv8.1-a+ cores (AWS Graviton2/3/4, ARM Neoverse N1/V1/V2, etc.).
INLINE_LSE_ATOMICS ?= 0
export INLINE_LSE_ATOMICS

include ../common.mk

