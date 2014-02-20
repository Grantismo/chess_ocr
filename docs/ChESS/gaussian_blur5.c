/**
 * @file gaussian_blur5.c
 *
 * @copyright Copyright 2011-2012 Stuart Bennett <sb476@cam.ac.uk>
 *
 * This programme is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 *
 * Blurs an image with a 2D Gaussian kernel with variance ~= 1.04
 */

#include "gaussian_blur5.h"

#include "config.h"

#include <mm_malloc.h>

/**
 * Our vector types
 */
typedef char v16qi __attribute__ ((vector_size(16)));
typedef int16_t v8hi __attribute__ ((vector_size(16)));
typedef long long v2di __attribute__ ((vector_size(16)));

/**
 * Union for inserting data into vector type
 */
union v16b {
	v16qi v;
	uint8_t b[16];
};

/**
 * Perform horizontal 1D 1-4-6-4-1 blur
 *
 * @param	in	16 px (1 byte each), of which 12 will be used
 * @return              8 px (2 bytes each) blurred
 */
static inline v8hi x_blur(v16qi in)
{
	// using PMOVZXBW saves a MOVDQA per expansion but requires SSE4.1
#if HAVE_PMOVZXBW
#define __BUILTIN_IA32_BW128(x) __builtin_ia32_pmovzxbw128((x))
#else
#define __BUILTIN_IA32_BW128(x) (v8hi)__builtin_ia32_punpcklbw128((x), zero.v)

	const union v16b zero = { .b = { 0 }};
#endif
	v8hi acc, xm1, x0, xp1, xp2;

	// accumulate 1 x input (expanded to 16 bit / px storage)
	acc = __BUILTIN_IA32_BW128(in);

	// shift input along 1 byte
	in = (v16qi)__builtin_ia32_psrldqi128((v2di)in, 8);
	// expand input to 16 bit storage
	xm1 = __BUILTIN_IA32_BW128(in);
	// x 4
	xm1 = __builtin_ia32_psllwi128(xm1, 2);

	// shift input
	in = (v16qi)__builtin_ia32_psrldqi128((v2di)in, 8);
	// accumulate 4x result
	acc = __builtin_ia32_paddw128(acc, xm1);
	// expand input
	x0 = __BUILTIN_IA32_BW128(in);
	// x 2
	x0 = __builtin_ia32_psllwi128(x0, 1);
	// accumulate 2x result
	acc = __builtin_ia32_paddw128(acc, x0);
	// x 2 (= 4x total)
	x0 = __builtin_ia32_psllwi128(x0, 1);

	// shift input
	in = (v16qi)__builtin_ia32_psrldqi128((v2di)in, 8);
	// accumulate 4x (which with earler 2x = 6x)
	acc = __builtin_ia32_paddw128(acc, x0);
	// expand input
	xp1 = __BUILTIN_IA32_BW128(in);
	// x 4
	xp1 = __builtin_ia32_psllwi128(xp1, 2);

	// shift intput
	in = (v16qi)__builtin_ia32_psrldqi128((v2di)in, 8);
	// accumulate 4x result
	acc = __builtin_ia32_paddw128(acc, xp1);
	// expand input
	xp2 = __BUILTIN_IA32_BW128(in);
	// accumulate 1x result and return
	return __builtin_ia32_paddw128(acc, xp2);
}

/**
 * Perform vertical 1D 1-4-6-4-1 blur
 *
 * @param	acc	8 px (2 bytes each) from y-2 row
 * @param	ym1	8 px (2 bytes each) from y-1 row
 * @param	y0	8 px (2 bytes each) from y-0 row
 * @param	yp1	8 px (2 bytes each) from y+1 row
 * @param	yp2	8 px (2 bytes each) from y+2 row
 * @return              8 px (2 bytes each) blurred
 */
static inline v8hi y_blur(v8hi acc, v8hi ym1, v8hi y0, v8hi yp1, v8hi yp2)
{
	// mult y-1 row by 4
	ym1 = __builtin_ia32_psllwi128(ym1, 2);
	// accumulate onto y-2 row
	acc = __builtin_ia32_paddw128(acc, ym1);

	// mult y-0 row by 2
	y0 = __builtin_ia32_psllwi128(y0, 1);
	// accumulate
	acc = __builtin_ia32_paddw128(acc, y0);
	// mult y-0 row by 2 (= 4x total)
	y0 = __builtin_ia32_psllwi128(y0, 1);
	// accumulate (6x overall)
	acc = __builtin_ia32_paddw128(acc, y0);

	// mult y+1 row by 2
	yp1 = __builtin_ia32_psllwi128(yp1, 2);
	// accumulate
	acc = __builtin_ia32_paddw128(acc, yp1);

	// accumulate y+2 row
	acc = __builtin_ia32_paddw128(acc, yp2);

	// divide results by 256 and return
	return __builtin_ia32_psrlwi128(acc, 8);
}

/**
 * Applies 1D 1-4-6-4-1 convolutions in x and y without gain
 * 2 px border all-round is invalid, a few px at very start and end of 3rd and
 * h-3rd row (respectively) may also be invalid (due to alignment)
 *
 * @param	w	Image width
 * @param	h	Image height
 * @param	im	The image (modified in place)
 * @return              Non-zero on failure
 */
int gaussian_blur5(const size_t w, const size_t h, uint8_t im[h][w])
{
	// im could be arbitrarily aligned -- start processing at first 16 byte boundary
	uint8_t *aligned_im = (uint8_t *)((uintptr_t)((uint8_t *)im + 0xf) & ~0xf);
	ptrdiff_t align_offset = aligned_im - (uint8_t *)im;
	uint16_t *temp;

	// aligned temporary storage
	// overallocate slightly as the y_blur step might otherwise attempt to
	// read beyond the end of temp
	if (!(temp = _mm_malloc((h + 1) * w * 2, 16)))
		return -1;

	// load 16 pixels
	v16qi in = *(v16qi *)aligned_im;

	int o;
	// scan across the whole image, outputting 16 pixels at a time, avoiding
	// falling off the end: note we read o -> o+31 each iteration
	for (o = 0; o < (w * h - 31 - align_offset); o += 16) {
		// 1D blur the 16 px in "in" to get 8 output px
		// output is placed in temp from 0 for alignment win
		*(v8hi *)&temp[o] = x_blur(in);

		// load the next 16 px
		v16qi in_next = *(v16qi *)&aligned_im[o + 16];

		// shunt "in" along 8 bytes
		in = (v16qi)__builtin_ia32_psrldqi128((v2di)in, 64);
		// stick the first 8 bytes of in_next on the end
		in = (v16qi)__builtin_ia32_punpcklqdq128((v2di)in, (v2di)in_next);

		// 1D blur these 16 px
		*(v8hi *)&temp[o + 8] = x_blur(in);

		// work on in_next next iteration
		in = in_next;
		/*
		for (int x = 2; x < (w - 2); x++)
			temp[y * w + x] = im[y][x - 2] + 4 * im[y][x - 1] + 6 * im[y][x] + 4 * im[y][x + 1] + im[y][x + 2];
		*/
	}
	*(v8hi *)&temp[o] = x_blur(in);
	for (o = o + 8; o < (w * h - align_offset - 4); o++)
		temp[o] = aligned_im[o] + 4 * aligned_im[o + 1] + 6 * aligned_im[o + 2] + 4 * aligned_im[o + 3] + aligned_im[o + 4];

	v8hi ym2, ym1, y0, yp1, yp2, y_out0, y_out1;
	// top and bottom 2 rows do not get valid output
	for (int y = 2; y < (h - 2); y++)
		// batch process 16 px horizontally per iteration
		// the last four px of a row in temp are border, so can be ignored
		for (int x = 0; x < (w - 4); x += 16) {
			// blur a 8x5 block in temp vertically
			ym2 = *(v8hi *)&temp[(y - 2) * w + x];
			ym1 = *(v8hi *)&temp[(y - 1) * w + x];
			y0 = *(v8hi *)&temp[y * w + x];
			yp1 = *(v8hi *)&temp[(y + 1) * w + x];
			yp2 = *(v8hi *)&temp[(y + 2) * w + x];

			y_out0 = y_blur(ym2, ym1, y0, yp1, yp2);

			// blur the horizontally adjacent 8x5 block
			ym2 = *(v8hi *)&temp[(y - 2) * w + x + 8];
			ym1 = *(v8hi *)&temp[(y - 1) * w + x + 8];
			y0 = *(v8hi *)&temp[y * w + x + 8];
			yp1 = *(v8hi *)&temp[(y + 1) * w + x + 8];
			yp2 = *(v8hi *)&temp[(y + 2) * w + x + 8];

			y_out1 = y_blur(ym2, ym1, y0, yp1, yp2);

			// combine both 8 px results and store (at +2 to accommodate left border)
			__builtin_ia32_storedqu((char *)&im[y][x + 2 + align_offset], __builtin_ia32_packuswb128(y_out0, y_out1));
		}
		/*
		for (int x = 2; x < ((w & ~0xf) - 6); x++)
			im[y][x] = (temp[(y - 2) * w + x] + 4 * temp[(y - 1) * w + x] + 6 * temp[y * w + x] + 4 * temp[(y + 1) * w + x] + temp[(y + 2) * w + x]) >> 8;
		*/

	_mm_free(temp);

	return 0;
}
