	.global _start
	.global _exit

	.equ	LED,	0xA0000000
	.equ	BUT,	0xB0000000

_start:
	ldr		R0, =LED	@ R0 = LED
	ldr		R1, =BUT	@ R1 = BUT

loop:

wait_push:
	ldr		R2, [R1]
	cmp		R2, #0
	beq		wait_push

wait_release:
	ldr		R2, [R1]
	cmp		R2, #0
	bne		wait_release

	ldr		R2, [R0]
	add		R2, R2, #1
	and		R2, R2, #1
	str		R2, [R0]

	b		loop

_exit:
	b	_exit

