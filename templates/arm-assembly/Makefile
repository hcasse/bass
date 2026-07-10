ARCH = arm-none-eabi-
CC = $(ARCH)gcc
CFLAGS = -g
LDFLAGS = -static -nostartfiles -nodefaultlibs
OBJDUMP=$(ARCH)objdump

all: main.elf

main.elf: main.s
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

disasm: main.elf
	$(OBJDUMP) -d $<

.phony: disasm
