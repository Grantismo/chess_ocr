/* Copyright 2010-2012 Stuart Bennett <sb476@cam.ac.uk> */

#ifndef STDUTIL_H
#define STDUTIL_H

#define MAX(a, b)  (((a) > (b)) ? (a) : (b))
#define MIN(a, b)  (((a) < (b)) ? (a) : (b))

// magic to allow stringification of macro arguments
#define XSTR(s) #s
#define STR(s) XSTR(s)

// memory barrier
#define barrier() __asm__ __volatile__("": : :"memory")

// x86-ism.  intended to stop the cpu setting on fire when spinning
static inline void cpu_relax(void)
{
	__asm__ volatile("rep; nop" ::: "memory");
}

// avoid compiler complaints about intentionally uninitialized variables
#define uninitialized_var(x) x = x

#endif /* STDUTIL_H */
