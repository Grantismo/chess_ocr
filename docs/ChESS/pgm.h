/* Copyright 2010-2012 Stuart Bennett <sb476@cam.ac.uk> */

#ifndef PGM_H
#define PGM_H

#include <stddef.h>	// size_t
#include <stdint.h>

int write_pgm(const size_t w, const size_t h, const uint16_t maxval, const void *image, const char *fname);
int read_pgm(const char *fname, void *image, size_t size, size_t *w, size_t *h);

static inline int write_pgm8(const size_t w, const size_t h, const uint8_t image[w * h], const char *fname)
{
	return write_pgm(w, h, 255, image, fname);
}

static inline int write_pgm16(const size_t w, const size_t h, const uint16_t image[w * h], const char *fname)
{
	return write_pgm(w, h, 65535, image, fname);
}

static inline int read_pgm8(const char *fname, size_t *w, size_t *h, uint8_t image[*w * *h])
{
	return read_pgm(fname, image, *w * *h, w, h);
}

static inline int read_pgm16(const char *fname, size_t *w, size_t *h, uint16_t image[*w * *h])
{
	return read_pgm(fname, image, *w * *h * 2, w, h);
}

#endif /* PGM_H */
