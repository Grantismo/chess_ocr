/**
 * @file chess.c
 *
 * @copyright Copyright 2011-2013 Stuart Bennett <sb476@cam.ac.uk>
 *
 * This programme is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 *
 * This programme is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this programme.  If not, see <http://www.gnu.org/licenses/>.
 *
 * ChESS demo programme
 */

#include "chess_features.h"
#include "corner_detect.h"
#include "feature_orientation.h"
#include "gaussian_blur5.h"
#include "non_max_sup_pts.h"
#include "pgm.h"
#include "stdutil.h"

#include <mm_malloc.h>

#include <getopt.h>
#include <math.h>	// lrintf
#include <stdio.h>
#include <string.h>

static void usage(const char *invoc)
{
	printf("%s version "STR(GIT_REVISION)"\n\nUsage:	%s [options] <PGM file>\n\
\n\
Command line options summary:\n\
	-b, --no-blur				do not blur image prior to detection\n\
	-h, --help				display this text\n\
	-l, --no-localization			do not localize co-ordinates of detected features\n\
	-n, --neighbourhood			specify radius of macro comparison neighbourhood\n\
	-o, --no-orientation			do not assign orientations to detected features\n\
	-r, --radius				specify non-maximal suppression radius\n\
	-R, --response-image <file name>	save response image to <file name> in PGM format\n\
	    --negative-response			include negative areas of response in response image\n\n",
	invoc, invoc);
}

static int read_cmd_line(const int argc, char *argv[],
			 bool *blur, bool *localize, unsigned *neighbourhood,
			 bool *ori, unsigned *radius, char **resp_fname, bool *neg_resp)
{
	enum clilongopts {
		LONOBLUR,
		LONOLOC,
		LONEIGHBOURHOOD,
		LONOORI,
		LORADIUS,
		LORESP,
		LORESPNEG,
		LOUSAGE,
	};
	const struct option longopts[] = {
		{"no-blur", 0, NULL, LONOBLUR},
		{"no-localization", 0, NULL, LONOLOC},
		{"neighbourhood", 1, NULL, LONEIGHBOURHOOD},
		{"no-orientation", 0, NULL, LONOORI},
		{"radius", 1, NULL, LORADIUS},
		{"response-image", 1, NULL, LORESP},
		{"negative-response", 0, NULL, LORESPNEG},
		{"help", 0, NULL, LOUSAGE},
		{0, 0, 0, 0}
	};
	int c;

	while ((c = getopt_long(argc, argv, "bln:or:R:h", longopts, NULL)) != -1) {
		if (c == '?')
			return -1;

		switch (c) {
		case 'b':
		case LONOBLUR:
			*blur = false;
			break;
		case 'l':
		case LONOLOC:
			*localize = false;
			break;
		case 'n':
		case LONEIGHBOURHOOD:
			*neighbourhood = strtoul(optarg, NULL, 10);
			break;
		case 'o':
		case LONOORI:
			*ori = false;
			break;
		case 'r':
		case LORADIUS:
			*radius = strtoul(optarg, NULL, 10);
			break;
		case 'R':
		case LORESP:
			*resp_fname = optarg;
			break;
		case LORESPNEG:
			*neg_resp = true;
			break;
		case 'h':
		case LOUSAGE:
			usage(argv[0]);
			exit(EXIT_SUCCESS);
		}
	}

	if (optind < argc - 1) {
		printf("Unrecognized command line arguments: ");
		while (optind < argc - 1)
			printf("%s ", argv[optind++]);
		printf("\n");
		return -1;
	}

	return 0;
}

int main(int argc, char *argv[])
{
	size_t w = 0, h = 0;
	uint8_t *im = NULL;
	bool blur = true, localize = true, ori = true, neg_resp = false;
	unsigned radius = 7, neighbourhood = 30;
	char *resp_fname = NULL;

	if (argc < 2) {
		usage(argv[0]);
		return 0;
	}

	if (read_cmd_line(argc, argv, &blur, &localize, &neighbourhood, &ori,
			  &radius, &resp_fname, &neg_resp) < 0)
		return -1;

	if (read_pgm8(argv[argc - 1], &w, &h, im) != -3)
		return -2;

	if (!(im = _mm_malloc(w * h, 16))) {
		fprintf(stderr, "Allocating %dx%d storage for input image failed\n", (int)w, (int)h);
		return -3;
	}

	if (read_pgm8(argv[argc - 1], &w, &h, im))
		return -4;

	if (blur && gaussian_blur5(w, h, (uint8_t (*)[w])im))
		return -5;

	int16_t resp[w * h];

	memset(resp, 0, w * h * 2);
	corner_detect5(w, h, im, resp);

	// feature threshold guesstimate time
	int16_t max_resp = 0;
	for (unsigned px = 0; px < w * h; px++)
		if (resp[px] > max_resp)
			max_resp = resp[px];

	if (resp_fname) {
		uint8_t resp8[w * h];

		if (!neg_resp) {
			for (unsigned px = 0; px < w * h; px++)
				if (resp[px] > 0)
					resp8[px] = ((int)resp[px] * 255) / max_resp;
				else
					resp8[px] = 0;
		} else {
			int16_t min_resp = 0;
			for (unsigned px = 0; px < w * h; px++)
				if (resp[px] < min_resp)
					min_resp = resp[px];

			for (unsigned px = 0; px < w * h; px++)
				resp8[px] = ((int)(resp[px] - min_resp) * 255) / (max_resp - min_resp);
		}

		if (write_pgm8(w, h, resp8, resp_fname))
			return -6;
	}

	if (!localize)
		return 0;

	unsigned thresh = max_resp >> 6;

	struct sized_point_list *spl;

	printf("Non-maximal suppression using radius %d and neighbourhood radius %d\n",
	       radius, neighbourhood);
	if (non_max_sup_pts(w, h, resp, 7, radius, thresh, 0, neighbourhood,
			    &new_point_list, &append_pl_point, (void **)&spl) < 1)
		return -7;

	if (ori)
		for (int i = 0; i < spl->occupancy; i++)
			spl->point[i].ori = assign_orientation(w, im, lrintf(spl->point[i].pos.x - .5f) + lrintf(spl->point[i].pos.y - .5f) * w, 1);

	_mm_free(im);

	printf("%d points found:\n", spl->occupancy);
	if (ori)
		for (int i = 0; i < spl->occupancy; i++)
			printf("(%f,%f) orientation %d\n", spl->point[i].pos.x, spl->point[i].pos.y, spl->point[i].ori);
	else
		for (int i = 0; i < spl->occupancy; i++)
			printf("(%f,%f)\n", spl->point[i].pos.x, spl->point[i].pos.y);

	return 0;
}
