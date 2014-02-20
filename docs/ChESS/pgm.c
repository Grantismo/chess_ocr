/**
 * @file pgm.c
 *
 * @copyright Copyright 2006-2012 Stuart Bennett <sb476@cam.ac.uk>
 *
 * PGM reading and writing functions
 */

#define _BSD_SOURCE     // endian macros (when -std=c99)

#include "pgm.h"

#include <endian.h>
#include <stdio.h>
#include <sys/types.h>	// off_t

/**
 * Writes an image out to a file in PGM format
 *
 * @param	w	width
 * @param	h	height
 * @param	maxval	maximum gray value
 * @param	image	pointer to image data
 * @param	fname	name of file to write image to
 * @return		0 on success
 */
int write_pgm(const size_t w, const size_t h, const uint16_t maxval, const void *image, const char *fname)
{
	FILE * restrict fframe;

	if (!(fframe = fopen(fname, "wb")))
		return -1;

	fprintf(fframe, "P5 %zd %zd %d\n", w, h, maxval);
	if (maxval > 255)
		for (off_t o = 0; o < w * h; o++)
			fwrite(&(uint16_t){htobe16(((uint16_t *)image)[o])}, 2, 1, fframe);
	else
		fwrite(image, maxval > 255 ? 2 : 1, w * h, fframe);
	fclose(fframe);

	return 0;
}

/**
 * Reads an image in from a file in PGM format
 *
 * @param	fname	name of file to read image from
 * @param	image	pointer to storage for image data
 * @param	size	size (in bytes) of storage available
 * @param	w	width of read image
 * @param	h	height of read image
 * @return		0 on success
 */
int read_pgm(const char *fname, void *image, size_t size, size_t *w, size_t *h)
{
	FILE * restrict fframe;
	int rv = 0;

	if (!(fframe = fopen(fname, "rb"))) {
		fprintf(stderr, "Couldn't open \"%s\" for reading\n", fname);
		return -1;
	}

	unsigned fw, fh, maxval, off;
	if (fscanf(fframe, "P5 %u %u %u%n", &fw, &fh, &maxval, &off) < 3) {
		fprintf(stderr, "\"%s\": couldn't parse header\n", fname);
		rv = -2;
		goto out;
	}

	*w = fw;
	*h = fh;

	if (size < fw * fh * (maxval > 255 ? 2 : 1)) {
		rv = -3;
		goto out;
	}

	if (fseek(fframe, off + 1, SEEK_SET) < 0) {
		fprintf(stderr, "\"%s\": no image data?\n", fname);
		rv = -4;
		goto out;
	}

	if (maxval > 255)
		for (off_t o = 0; o < fw * fh; o++) {
			uint16_t tmp;
			if (fread(&tmp, 2, 1, fframe) < 1) {
				fprintf(stderr, "\"%s\": couldn't read all of image data\n", fname);
				rv = -5;
				break;
			}
			((uint16_t *)image)[o] = be16toh(tmp);
		}
	else
		if (fread(image, 1, fw * fh, fframe) < (fw * fh)) {
			fprintf(stderr, "\"%s\": couldn't read all of image data\n", fname);
			rv = -5;
		}

out:
	fclose(fframe);

	return rv;
}
