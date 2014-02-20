/* Copyright 2011-2012 Stuart Bennett <sb476@cam.ac.uk> */

#ifndef GAUSSIAN_BLUR5_H
#define GAUSSIAN_BLUR5_H

#include <stddef.h>
#include <stdint.h>

int gaussian_blur5(const size_t w, const size_t h, uint8_t im[h][w]);

#endif /* GAUSSIAN_BLUR5_H */
