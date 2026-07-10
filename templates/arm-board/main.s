	.global _start
	.global _exit

	.equ	LED,	0xA0000000
	.equ	BUT,	0xB0000000

_start:
	ldr	R0, =LED
	ldr	R1, =BUT
loop:
	ldr	R2, [R1]
	str R2, [R0]
	b	loop

_exit:
	b	_exit
